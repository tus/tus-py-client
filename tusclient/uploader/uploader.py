from typing import Optional
import time
import asyncio

from tusclient.uploader.baseuploader import BaseUploader

from tusclient.exceptions import TusUploadFailed, TusCommunicationError
from tusclient.request import TusRequest, AsyncTusRequest


def _verify_upload(request: TusRequest):
    if request.status_code == 204:
        return True
    else:
        raise TusUploadFailed('', request.status_code, request.response_content)


class Uploader(BaseUploader):
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

        while self.offset < self.stop_at:
            self.upload_chunk()

    def upload_chunk(self):
        """
        Upload chunk of file.
        """
        self._retried = 0
        self._do_request()
        self.offset = int(self.request.response_headers.get('upload-offset'))

    def _do_request(self):
        self.request = TusRequest(self)
        try:
            self.request.perform()
            _verify_upload(self.request)
        except TusUploadFailed as error:
            self._retry_or_cry(error)

    def _retry_or_cry(self, error):
        if self.retries > self._retried:
            time.sleep(self.retry_delay)

            self._retried += 1
            try:
                self.offset = self.get_offset()
            except TusCommunicationError as e:
                self._retry_or_cry(e)
            else:
                self._do_request()
        else:
            raise error


class AsyncUploader(BaseUploader):
    def __init__(self, *args, io_loop: Optional[asyncio.AbstractEventLoop] = None, **kwargs):
        self.io_loop = io_loop
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
        while self.offset < self.stop_at:
            await self.upload_chunk()

    async def upload_chunk(self):
        """
        Upload chunk of file.
        """
        self._retried = 0
        await self._do_request()
        self.offset = int(self.request.response_headers.get('upload-offset'))

    async def _do_request(self):
        self.request = AsyncTusRequest(self)
        try:
            await self.request.perform()
            _verify_upload(self.request)
        except TusUploadFailed as error:
            await self._retry_or_cry(error)

    async def _retry_or_cry(self, error):
        if self.retries > self._retried:
            asyncio.sleep(self.retry_delay, loop=self.io_loop)

            self._retried += 1
            try:
                self.offset = self.get_offset()
            except TusCommunicationError as err:
                await self._retry_or_cry(err)
            else:
                await self._do_request()
        else:
            raise error
