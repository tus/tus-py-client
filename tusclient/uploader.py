import os

import requests

from tusclient.exceptions import TusUploadFailed
from tusclient.request import TusRequest


class Uploader(object):
    DEFAULT_HEADERS = {"Expect": '',
                       "Content-Type": "application/offset+octet-stream",
                       "Tus-Resumable": "1.0.0"}
    DEFAULT_CHUNK_SIZE = 2 * 1024 * 1024  # 2kb

    def __init__(self, file_name, url=None, client=None, chunk_size=None):
        if not os.path.isfile(file_name):
            raise ValueError("invalid file {}".format(file_name))

        self.file_name = file_name
        self.file_size = os.path.getsize(file_name)
        self.stop_at = self.file_size
        self.client = client
        self.url = url or self.create_url()
        self.offset = self.get_offset()
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        self.request = None

    @property
    def headers(self):
        return dict(self.DEFAULT_HEADERS, **self.client.headers)

    def headers_as_list(self):
        headers = self.headers
        headers_list = ['{}: {}'.format(key, value) for key, value in headers.iteritems()]
        return headers_list

    def get_offset(self):
        resp = requests.head(self.url, headers=self.headers)
        return int(resp.headers["upload-offset"])

    def create_url(self):
        headers = self.headers
        headers['upload-length'] = str(self.file_size)
        resp = requests.post(self.client.url, headers=headers)
        return resp.headers.get("location")

    @property
    def request_length(self):
        remainder = self.stop_at - self.offset
        return self.chunk_size if remainder > self.chunk_size else remainder

    def verify_upload(self):
        if self.request.status_code == 204:
            print '{} bytes uploaded ...'.format(self.request.response_headers.get('upload-offset'))
        else:
            raise TusUploadFailed

    def _do_request(self):
        self.request = TusRequest(self)
        try:
            self.request.perform()
            self.verify_upload()
        finally:
            self.request.close()

    def upload(self, stop_at=None):
        if stop_at:
            self.stop_at = stop_at

        while self.offset < self.stop_at:
            self.upload_chunk()
        else:
            print "maximum upload specified({} bytes) has been reached".format(self.stop_at)

    def upload_chunk(self):
        self._do_request()
        self.offset += self.request_length
