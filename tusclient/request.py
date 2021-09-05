from typing import Optional
import base64
import asyncio
from functools import wraps

import requests
import aiohttp

from tusclient.exceptions import TusUploadFailed, TusCommunicationError


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
        self._url = uploader.url
        self.response_headers = {}
        self.status_code = None
        self.response_content = None

        self._request_headers = {
            'upload-offset': str(uploader.offset),
            'Content-Type': 'application/offset+octet-stream'
        }
        self._request_headers.update(uploader.get_headers())
        self._upload_checksum = uploader.upload_checksum
        self._checksum_algorithm = uploader.checksum_algorithm
        self._checksum_algorithm_name = uploader.checksum_algorithm_name

        self._chunk = ChunkReader(
            uploader.get_file_stream(),
            uploader.offset,
            uploader.get_request_length(),
        )

    def add_checksum(self, file):
        checksum = self._checksum_algorithm()
        chunk = file.read(8192)
        while chunk:
            checksum.update(chunk)
            chunk = file.read(8192)

        self._request_headers['upload-checksum'] = \
            ' '.join((
                self._checksum_algorithm_name,
                base64.b64encode(
                    checksum.digest()
                ).decode('ascii'),
            ))


class TusRequest(BaseTusRequest):
    """Class to handle async Tus upload requests"""

    def perform(self):
        """
        Perform actual request.
        """
        if self._upload_checksum:
            self.add_checksum(self._chunk.reset())
        try:
            resp = requests.patch(self._url, data=self._chunk.reset(),
                                  headers=self._request_headers)
            self.status_code = resp.status_code
            self.response_content = resp.content
            self.response_headers = {
                k.lower(): v for k, v in resp.headers.items()}
        except requests.exceptions.RequestException as error:
            raise TusUploadFailed(error)


class AsyncTusRequest(BaseTusRequest):
    """Class to handle async Tus upload requests"""

    def __init__(self, *args, io_loop: Optional[asyncio.AbstractEventLoop] = None, **kwargs):
        self.io_loop = io_loop
        super().__init__(*args, **kwargs)

    async def perform(self):
        """
        Perform actual request.
        """
        if self._upload_checksum:
            self.add_checksum(self._chunk.reset())
        try:
            async with aiohttp.ClientSession(loop=self.io_loop) as session:
                async with session.patch(self._url, data=self._chunk.reset().async_reader(8*1024), headers=self._request_headers) as resp:
                    self.status_code = resp.status
                    self.response_headers = {
                        k.lower(): v for k, v in resp.headers.items()}
                    self.response_content = await resp.content.read()
        except aiohttp.ClientError as error:
            raise TusUploadFailed(error)


class ChunkReader(object):
    def __init__(self, file, start, length):
        self.file = file
        self.start = start
        self.len = length  # to send Content-Length in headers
        self.remaining = None

    def reset(self):
        self.file.seek(self.start)
        self.remaining = self.len
        return self

    def read(self, size=-1):
        if self.remaining is None:
            raise Exception("reset() must be called before first read")

        if size == -1 or size > self.remaining:
            size = self.remaining
        data = self.file.read(size)
        self.remaining -= len(data)
        return data

    async def async_reader(self, size=-1):
        chunk = self.read(size)
        while chunk:
            yield chunk
            chunk = self.read(size)
