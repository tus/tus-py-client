from typing import Optional
import asyncio
from urllib.parse import urljoin

import requests
import aiohttp
import ssl

from tusclient.uploader.baseuploader import BaseUploader

from tusclient.async_upload_chunks_generated import (
    upload_chunk_with_retry as async_upload_chunk_with_retry,
)
from tusclient.detailed_error import (
    create_upload_request_error,
    create_upload_response_error,
)
from tusclient.exceptions import TusUploadAborted, TusUploadFailed, TusCommunicationError
from tusclient.protocol_generated import (
    CREATE_UPLOAD_METHOD,
    LOCATION_HEADER_NAME,
    UPLOAD_CHUNK_METHOD,
    UPLOAD_CHUNK_OPERATION_ID,
    UPLOAD_OFFSET_HEADER_NAME,
    is_successful_response_status,
    request_method_plan,
    upload_body_headers,
)
from tusclient.request import TusRequest, AsyncTusRequest, catch_requests_error
from tusclient.upload_chunks_generated import upload_chunk_with_retry


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
        parallel_uploads = self.parallel_upload_count()

        if parallel_uploads > 1:
            if stop_at is not None and stop_at != self.file_size:
                raise ValueError("tus: stop_at is not supported with parallel uploads")
            self.upload_parallel(parallel_uploads)
            return

        if not self.url:
            # Ensure the POST request is performed even for empty files.
            # This ensures even empty files can be uploaded; in this case
            # only the POST request needs to be performed.
            self.set_url(self.create_url())
            self.offset = 0

        while self.stop_at is None or (self.offset < self.stop_at):
            self.upload_chunk()

    def upload_parallel(self, parallel_uploads: int):
        self.assert_parallel_upload_policy_supported()
        part_ranges = self.parallel_upload_part_ranges(parallel_uploads)
        partial_urls = [
            self.create_partial_url(end - start)
            for start, end in part_ranges
        ]
        accepted_bytes = 0

        for part_url, (start, end) in zip(partial_urls, part_ranges):
            part_size = end - start
            accepted_bytes += self.upload_partial_chunk(part_url, start, end)
            self.offset = accepted_bytes
            self.notify_progress(self.offset)
            self.notify_chunk_complete(part_size, self.offset)

        self.set_url(self.create_final_url(partial_urls))
        self.offset = self.file_size
        self.remove_url_on_success()

    @catch_requests_error
    def create_partial_url(self, part_size: int):
        headers = self.get_url_creation_headers(
            metadata=self.metadata_for_partial_uploads,
            partial=True,
            upload_length=part_size,
        )
        context = self.run_before_request(CREATE_UPLOAD_METHOD, self.client.url, headers)
        try:
            resp = requests.request(
                CREATE_UPLOAD_METHOD,
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
        url = resp.headers.get(LOCATION_HEADER_NAME)
        if not is_successful_response_status(resp.status_code) or url is None:
            raise create_upload_response_error(context, resp)
        return urljoin(self.client.url, url)

    @catch_requests_error
    def upload_partial_chunk(self, partial_url: str, start: int, end: int):
        chunk = self.read_file_range(start, end)
        operation_headers = {
            UPLOAD_OFFSET_HEADER_NAME: "0",
        }
        operation_headers.update(upload_body_headers(self.protocol, done=True))
        method_plan = request_method_plan(
            UPLOAD_CHUNK_OPERATION_ID,
            UPLOAD_CHUNK_METHOD,
            self.request_method_input_options(),
        )
        operation_headers.update(method_plan["headers"])
        headers = self.prepare_request_headers(operation_headers)
        context = self.run_before_request(method_plan["method"], partial_url, headers)
        try:
            resp = requests.request(
                method_plan["method"],
                partial_url,
                data=chunk,
                headers=context.headers,
                verify=self.verify_tls_cert,
                stream=True,
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

        accepted_offset = resp.headers.get(UPLOAD_OFFSET_HEADER_NAME)
        if accepted_offset is None:
            raise create_upload_response_error(context, resp)

        try:
            accepted_offset = int(accepted_offset)
        except ValueError:
            raise TusCommunicationError(
                "Unexpected accepted upload offset {}".format(accepted_offset),
                resp.status_code,
                resp.content,
            )
        if accepted_offset != len(chunk):
            raise TusCommunicationError(
                "Unexpected accepted upload offset {}".format(accepted_offset),
                resp.status_code,
                resp.content,
            )

        return accepted_offset

    @catch_requests_error
    def create_final_url(self, partial_urls):
        headers = self.get_url_creation_headers(final_upload_urls=partial_urls)
        context = self.run_before_request(CREATE_UPLOAD_METHOD, self.client.url, headers)
        try:
            resp = requests.request(
                CREATE_UPLOAD_METHOD,
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
        url = resp.headers.get(LOCATION_HEADER_NAME)
        if not is_successful_response_status(resp.status_code) or url is None:
            raise create_upload_response_error(context, resp)
        return urljoin(self.client.url, url)

    def upload_chunk(self):
        """
        Upload chunk of file.
        """
        # Ensure that we have a URL, as this is behavior we allowed previously.
        # See https://github.com/tus/tus-py-client/issues/82.
        if not self.url:
            self.set_url(self.create_url())
            self.offset = 0

        upload_chunk_with_retry(
            self,
            self._perform_patch_request,
            self._upload_retry_delays_ms(),
            on_should_retry=self.on_should_retry,
        )
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

    def _perform_patch_request(self):
        """Send one chunk PATCH and absorb its accepted state on success.

        The retry algorithm around this transport step lives in the generated
        ``upload_chunk_with_retry`` (see tusclient/upload_chunks_generated.py).
        """
        self.request = TusRequest(self)
        self.request.perform()
        _verify_upload(self.request)
        self.offset = int(self.request.response_headers.get("upload-offset"))
        if self.upload_length_deferred and self.request.stream_eof:
            self.file_size = self.offset
            self.stop_at = self.offset


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
        parallel_uploads = self.parallel_upload_count()

        if parallel_uploads > 1:
            if stop_at is not None and stop_at != self.file_size:
                raise ValueError("tus: stop_at is not supported with parallel uploads")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                Uploader.upload_parallel,
                self,
                parallel_uploads,
            )
            return

        if not self.url:
            self.set_url(await self.create_url())
            self.offset = 0

        while self.stop_at is None or (self.offset < self.stop_at):
            await self.upload_chunk()

    def create_partial_url(self, part_size: int):
        return Uploader.create_partial_url(self, part_size)

    def upload_partial_chunk(self, partial_url: str, start: int, end: int):
        return Uploader.upload_partial_chunk(self, partial_url, start, end)

    def create_final_url(self, partial_urls):
        return Uploader.create_final_url(self, partial_urls)

    async def upload_chunk(self):
        """
        Upload chunk of file.
        """
        # Ensure that we have a URL, as this is behavior we allowed previously.
        # See https://github.com/tus/tus-py-client/issues/82.
        if not self.url:
            self.set_url(await self.create_url())
            self.offset = 0

        await async_upload_chunk_with_retry(
            self,
            self._perform_patch_request,
            self._upload_retry_delays_ms(),
            on_should_retry=self.on_should_retry,
        )
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

    async def _perform_patch_request(self):
        """Send one chunk PATCH and absorb its accepted state on success.

        The retry algorithm around this transport step lives in the generated
        ``upload_chunk_with_retry`` (see tusclient/async_upload_chunks_generated.py).
        """
        self.request = AsyncTusRequest(self)
        await self.request.perform()
        _verify_upload(self.request)
        self.offset = int(self.request.response_headers.get("upload-offset"))
        if self.upload_length_deferred and self.request.stream_eof:
            self.file_size = self.offset
            self.stop_at = self.offset
