from typing import Optional
import base64
import asyncio
from functools import wraps

import requests
import aiohttp
import ssl

from tusclient.exceptions import TusUploadAborted, TusUploadFailed, TusCommunicationError
from tusclient.protocol_generated import (
    UPLOAD_CHUNK_METHOD,
    UPLOAD_CHUNK_OPERATION_ID,
    request_method_plan,
    upload_body_headers,
)


# Catches requests exceptions and throws custom tuspy errors.
def catch_requests_error(func):
    """Deocrator to catch requests exceptions"""

    @wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as error:
            raise TusCommunicationError(error)

    return _wrapper


class BaseTusRequest:
    """
    Http Request Abstraction.

    Sets up tus custom http request on instantiation.

    requires argument 'uploader' an instance of tusclient.uploader.Uploader
    on instantiation.

    :Attributes:
        - response_headers (dict)
        - file (file):
            The file that is being uploaded.
    """

    def __init__(self, uploader):
        self.uploader = uploader
        self._url = uploader.url
        self.status_code = None
        self.response_headers = {}
        self.response_content = None
        self.stream_eof = False
        self.verify_tls_cert = bool(uploader.verify_tls_cert)
        self.file = uploader.get_file_stream()
        self.file.seek(uploader.offset)
        self.client_cert = uploader.client_cert

        self._operation_headers = {
            "upload-offset": str(uploader.offset),
        }
        self._offset = uploader.offset
        self._upload_length_deferred = uploader.upload_length_deferred
        self._content_length = uploader.get_request_length()
        self._upload_checksum = uploader.upload_checksum
        self._checksum_algorithm = uploader.checksum_algorithm
        self._checksum_algorithm_name = uploader.checksum_algorithm_name

    def add_checksum(self, headers, chunk: bytes):
        if self._upload_checksum:
            headers["upload-checksum"] = " ".join(
                (
                    self._checksum_algorithm_name,
                    base64.b64encode(self._checksum_algorithm(chunk).digest()).decode(
                        "ascii"
                    ),
                )
            )

    def request_method_plan(self):
        return request_method_plan(
            UPLOAD_CHUNK_OPERATION_ID,
            UPLOAD_CHUNK_METHOD,
            self.uploader.request_method_input_options(),
        )

    def _is_final_chunk(self, stream_eof, chunk_size):
        if self._upload_length_deferred:
            return stream_eof
        return self._offset + chunk_size >= self.uploader.file_size


class TusRequest(BaseTusRequest):
    """Class to handle async Tus upload requests"""

    def perform(self):
        """
        Perform actual request.
        """
        try:
            chunk = self.file.read(self._content_length)
            stream_eof = len(chunk) < self._content_length
            operation_headers = dict(self._operation_headers)
            self.add_checksum(operation_headers, chunk)
            operation_headers.update(
                upload_body_headers(
                    self.uploader.protocol,
                    done=self._is_final_chunk(stream_eof, len(chunk)),
                )
            )
            if stream_eof and self._upload_length_deferred:
                operation_headers["upload-length"] = str(self._offset + len(chunk))
            method_plan = self.request_method_plan()
            operation_headers.update(method_plan["headers"])
            headers = self.uploader.prepare_request_headers(operation_headers)
            context = self.uploader.run_before_request(method_plan["method"], self._url, headers)
            try:
                resp = requests.request(
                    method_plan["method"],
                    self._url,
                    data=chunk,
                    headers=context.headers,
                    verify=self.verify_tls_cert,
                    stream=True,
                    cert=self.client_cert,
                )
            finally:
                self.uploader.clear_current_request()
            self.uploader.run_after_response(context, resp)
            self.status_code = resp.status_code
            self.response_content = resp.content
            self.response_headers = {k.lower(): v for k, v in resp.headers.items()}
            self.stream_eof = stream_eof
        except requests.exceptions.RequestException as error:
            if self.uploader.is_aborted():
                raise TusUploadAborted()
            raise TusUploadFailed(error)

class AsyncTusRequest(BaseTusRequest):
    """Class to handle async Tus upload requests"""

    def __init__(
        self, *args, io_loop: Optional[asyncio.AbstractEventLoop] = None, **kwargs
    ):
        self.io_loop = io_loop
        super().__init__(*args, **kwargs)

    async def perform(self):
        """
        Perform actual request.
        """
        chunk = self.file.read(self._content_length)
        stream_eof = len(chunk) < self._content_length
        operation_headers = dict(self._operation_headers)
        self.add_checksum(operation_headers, chunk)
        operation_headers.update(
            upload_body_headers(
                self.uploader.protocol,
                done=self._is_final_chunk(stream_eof, len(chunk)),
            )
        )
        try:
            ssl_ctx = ssl.create_default_context()
            if self.client_cert is not None:
                if self.client_cert is str:
                    ssl_ctx.load_cert_chain(certfile=self.client_cert)
                else:
                    ssl_ctx.load_cert_chain(
                        certfile=self.client_cert[0], keyfile=self.client_cert[1]
                    )
            conn = aiohttp.TCPConnector(ssl=ssl_ctx)
            async with aiohttp.ClientSession(loop=self.io_loop, connector=conn) as session:
                verify_tls_cert = None if self.verify_tls_cert else False
                method_plan = self.request_method_plan()
                operation_headers.update(method_plan["headers"])
                headers = self.uploader.prepare_request_headers(operation_headers)
                context = self.uploader.run_before_request(
                    method_plan["method"], self._url, headers
                )
                try:
                    async with session.request(
                        method_plan["method"],
                        self._url,
                        data=chunk,
                        headers=context.headers,
                        ssl=verify_tls_cert,
                    ) as resp:
                        self.uploader.run_after_response(context, resp)
                        self.status_code = resp.status
                        self.response_headers = {
                            k.lower(): v for k, v in resp.headers.items()
                        }
                        self.response_content = await resp.content.read()
                        self.stream_eof = stream_eof
                finally:
                    self.uploader.clear_current_request()
        except aiohttp.ClientError as error:
            if self.uploader.is_aborted():
                raise TusUploadAborted()
            raise TusUploadFailed(error)
