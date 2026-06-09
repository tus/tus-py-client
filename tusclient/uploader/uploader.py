from typing import Optional
import time
import asyncio
from urllib.parse import urljoin

import requests
import aiohttp
import ssl

from tusclient.uploader.baseuploader import BaseUploader

from tusclient.detailed_error import (
    create_upload_request_error,
    create_upload_response_error,
)
from tusclient.exceptions import TusUploadAborted, TusUploadFailed, TusCommunicationError
from tusclient.protocol_generated import (
    CREATE_UPLOAD_METHOD,
    LOCATION_HEADER_NAME,
    UPLOAD_OFFSET_HEADER_NAME,
    is_successful_response_status,
    upload_body_headers,
)
from tusclient.request import TusRequest, AsyncTusRequest, catch_requests_error


def _verify_upload(request: TusRequest):
    if 200 <= request.status_code < 300:
        return True
    else:
        raise TusUploadFailed("", request.status_code, request.response_content)


class Uploader(BaseUploader):
    @catch_requests_error
    def create_url_with_upload(self, bytes_to_upload: int):
        """
        Create a new upload URL and send the first bytes in the creation request.
        """
        if bytes_to_upload < 0:
            raise ValueError("bytes_to_upload must be non-negative")
        if self.upload_length_deferred:
            raise ValueError(
                "create_url_with_upload cannot be used with upload_length_deferred"
            )
        if bytes_to_upload > self.get_file_size():
            raise ValueError("bytes_to_upload cannot exceed the upload size")

        stream = self.get_file_stream()
        try:
            chunk = stream.read(bytes_to_upload)
        finally:
            if self.file_stream is None:
                stream.close()

        if len(chunk) != bytes_to_upload:
            raise ValueError(
                "Could only read {} of {} requested upload bytes".format(
                    len(chunk),
                    bytes_to_upload,
                )
            )

        headers = self.get_url_creation_headers()
        headers.update(
            upload_body_headers(
                self.protocol,
                done=bytes_to_upload == self.get_file_size(),
            )
        )
        context = self.run_before_request(CREATE_UPLOAD_METHOD, self.client.url, headers)
        try:
            resp = requests.request(
                CREATE_UPLOAD_METHOD,
                self.client.url,
                data=chunk,
                headers=context.headers,
                verify=self.verify_tls_cert,
                cert=self.client_cert,
            )
        except requests.exceptions.RequestException as error:
            if self.is_aborted():
                raise TusUploadAborted()
            raise create_upload_request_error(context, error)
        finally:
            self.clear_current_request()
        self.run_after_response(context, resp)

        if not is_successful_response_status(resp.status_code):
            raise create_upload_response_error(context, resp)

        url = resp.headers.get(LOCATION_HEADER_NAME)
        if url is None:
            raise create_upload_response_error(context, resp)

        offset = resp.headers.get(UPLOAD_OFFSET_HEADER_NAME)
        if offset is None:
            raise create_upload_response_error(context, resp)

        try:
            accepted_offset = int(offset)
        except ValueError:
            raise TusCommunicationError(
                "Unexpected accepted upload offset {}".format(offset),
                resp.status_code,
                resp.content,
            )
        if accepted_offset < 0 or accepted_offset > bytes_to_upload:
            raise TusCommunicationError(
                "Unexpected accepted upload offset {}".format(accepted_offset),
                resp.status_code,
                resp.content,
            )

        previous_offset = self.offset
        self.set_url(urljoin(self.client.url, url))
        self.offset = accepted_offset
        self.notify_progress(previous_offset)
        self.notify_progress(self.offset)
        self.notify_chunk_complete(self.offset - previous_offset, self.offset)
        self.remove_url_on_success()
        return self.url

    def upload(self, stop_at: Optional[int] = None):
        """
        Perform file upload.

        Performs continous upload of chunks of the file. The size uploaded at each cycle is
        the value of the attribute 'chunk_size'.

        :Args:
            - stop_at (Optional[int]):
                Determines at what offset value the upload should stop. If not specified this
                defaults to the file size.
        """
        self.stop_at = stop_at or self.file_size

        if not self.url:
            # Ensure the POST request is performed even for empty files.
            # This ensures even empty files can be uploaded; in this case
            # only the POST request needs to be performed.
            self.set_url(self.create_url())
            self.offset = 0

        while self.stop_at is None or (self.offset < self.stop_at):
            self.upload_chunk()

    def upload_chunk(self):
        """
        Upload chunk of file.
        """
        self._retried = 0

        # Ensure that we have a URL, as this is behavior we allowed previously.
        # See https://github.com/tus/tus-py-client/issues/82.
        if not self.url:
            self.set_url(self.create_url())
            self.offset = 0

        previous_offset = self.offset
        if not self.upload_length_deferred:
            self.notify_progress(previous_offset)
        self._do_request()
        self.offset = int(self.request.response_headers.get("upload-offset"))
        if self.upload_length_deferred and self.request.stream_eof:
            self.file_size = self.offset
            self.stop_at = self.offset
        if self.upload_length_deferred:
            self.notify_progress(previous_offset)
        self.notify_progress(self.offset)
        self.notify_chunk_complete(self.offset - previous_offset, self.offset)
        self.remove_url_on_success()

    @catch_requests_error
    def create_url(self):
        """
        Return upload url.

        Makes request to tus server to create a new upload url for the required file upload.
        """
        headers = self.get_url_creation_headers()
        context = self.run_before_request("POST", self.client.url, headers)
        try:
            resp = requests.post(
                self.client.url,
                headers=context.headers,
                verify=self.verify_tls_cert,
                cert=self.client_cert,
            )
        except requests.exceptions.RequestException as error:
            if self.is_aborted():
                raise TusUploadAborted()
            raise create_upload_request_error(context, error)
        finally:
            self.clear_current_request()
        self.run_after_response(context, resp)
        url = resp.headers.get("location")
        if not is_successful_response_status(resp.status_code) or url is None:
            raise create_upload_response_error(context, resp)
        return urljoin(self.client.url, url)

    def _do_request(self):
        self.request = TusRequest(self)
        try:
            self.request.perform()
            _verify_upload(self.request)
        except TusUploadFailed as error:
            self._retry_or_cry(error)

    def _retry_or_cry(self, error):
        retry_attempt = self._retried
        if self._retry_limit() <= retry_attempt:
            raise error
        if not self._should_retry(error, retry_attempt):
            raise error

        time.sleep(self._retry_delay_seconds(retry_attempt))
        self._retried += 1
        previous_offset = self.offset
        try:
            recovered_offset = self.get_offset()
        except TusCommunicationError as err:
            self._retry_or_cry(err)
        else:
            if recovered_offset > previous_offset:
                self._retried = 0
            self.offset = recovered_offset
            self._do_request()


class AsyncUploader(BaseUploader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def upload(self, stop_at: Optional[int] = None):
        """
        Perform file upload.

        Performs continous upload of chunks of the file. The size uploaded at each cycle is
        the value of the attribute 'chunk_size'.

        :Args:
            - stop_at (Optional[int]):
                Determines at what offset value the upload should stop. If not specified this
                defaults to the file size.
        """
        self.stop_at = stop_at or self.file_size

        if not self.url:
            self.set_url(await self.create_url())
            self.offset = 0

        while self.stop_at is None or (self.offset < self.stop_at):
            await self.upload_chunk()

    async def upload_chunk(self):
        """
        Upload chunk of file.
        """
        self._retried = 0

        # Ensure that we have a URL, as this is behavior we allowed previously.
        # See https://github.com/tus/tus-py-client/issues/82.
        if not self.url:
            self.set_url(await self.create_url())
            self.offset = 0

        previous_offset = self.offset
        if not self.upload_length_deferred:
            self.notify_progress(previous_offset)
        await self._do_request()
        self.offset = int(self.request.response_headers.get("upload-offset"))
        if self.upload_length_deferred and self.request.stream_eof:
            self.file_size = self.offset
            self.stop_at = self.offset
        if self.upload_length_deferred:
            self.notify_progress(previous_offset)
        self.notify_progress(self.offset)
        self.notify_chunk_complete(self.offset - previous_offset, self.offset)
        self.remove_url_on_success()

    async def create_url(self):
        """
        Return upload url.

        Makes request to tus server to create a new upload url for the required file upload.
        """
        try:
            ssl_ctx = ssl.create_default_context()
            if (self.client_cert is not None):
                if self.client_cert is str:
                    ssl_ctx.load_cert_chain(certfile=self.client_cert)
                else:
                    ssl_ctx.load_cert_chain(certfile=self.client_cert[0], keyfile=self.client_cert[1])
            conn = aiohttp.TCPConnector(ssl=ssl_ctx)
            async with aiohttp.ClientSession(connector=conn) as session:
                headers = self.get_url_creation_headers()
                context = self.run_before_request("POST", self.client.url, headers)
                try:
                    verify_tls_cert = None if self.verify_tls_cert else False
                    async with session.post(
                        self.client.url, headers=context.headers, ssl=verify_tls_cert
                    ) as resp:
                        self.run_after_response(context, resp)
                        url = resp.headers.get("location")
                        if url is None:
                            msg = (
                                "Attempt to retrieve create file url with status {}".format(
                                    resp.status
                                )
                            )
                            raise TusCommunicationError(
                                msg, resp.status, await resp.content.read()
                            )
                        return urljoin(self.client.url, url)
                finally:
                    self.clear_current_request()
        except aiohttp.ClientError as error:
            if self.is_aborted():
                raise TusUploadAborted()
            raise TusCommunicationError(error)

    async def _do_request(self):
        self.request = AsyncTusRequest(self)
        try:
            await self.request.perform()
            _verify_upload(self.request)
        except TusUploadFailed as error:
            await self._retry_or_cry(error)

    async def _retry_or_cry(self, error):
        retry_attempt = self._retried
        if self._retry_limit() <= retry_attempt:
            raise error
        if not self._should_retry(error, retry_attempt):
            raise error

        await asyncio.sleep(self._retry_delay_seconds(retry_attempt))
        self._retried += 1
        previous_offset = self.offset
        try:
            recovered_offset = self.get_offset()
        except TusCommunicationError as err:
            await self._retry_or_cry(err)
        else:
            if recovered_offset > previous_offset:
                self._retried = 0
            self.offset = recovered_offset
            await self._do_request()
