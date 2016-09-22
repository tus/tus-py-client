import os
import StringIO

import pycurl
import requests


class FileUpload(object):
    DEFAULT_HEADERS = ["Expect:", "Content-Type: application/offset+octet-stream",
                       "Tus-Resumable: 1.0.0"]

    def __init__(self, file_name, url, chunk_size=None):
        if not os.path.isfile(self.file_name):
            raise ValueError("invalid file {}".format(self.file_name))

        self.file_name = file_name
        self.file_size = os.path.getsize(file_name)
        self.url = url
        self.offset = self.get_offset()
        self.response = None
        self.request = None
        self.chunk_size = chunk_size or (20 * self.file_size) / 100

    @property
    def headers(self):
        return self.DEFAULT_HEADERS + ["Upload-Offset: {}".format(self.offset)]

    def upload(self, stop_at=None):
        if not stop_at or stop_at > self.file_size:
            stop_at = self.file_size

        while self.offset < stop_at:
            self.upload_chunk()

    def upload_chunk(self):
        self._do_request()
        self.offset += self._request_length

    def get_offset(self):
        resp = requests.head(self.url, headers={"Tus-Resumable": "1.0.0"})
        return int(resp.headers["Upload-Offset"])

    @property
    def _request_length(self):
        left = self.file_size - self.offset
        return self.chunk_size if left > self.chunk_size else left

    def _do_request(self):
        self._prepare_request()
        try:
            self.request.perform()
        finally:
            self._end_request()

    def _end_request(self):
        if self.request:
            self.request.close()

    def _prepare_request(self):
        c = pycurl.Curl()
        c.setopt(pycurl.VERBOSE, 1)
        c.setopt(pycurl.URL, self.url)
        hout = StringIO.StringIO()

        c.setopt(pycurl.HEADERFUNCTION, hout.write)
        c.setopt(pycurl.WRITEFUNCTION, self._prepare_response)
        c.setopt(pycurl.UPLOAD, 1)
        c.setopt(pycurl.CUSTOMREQUEST, 'PATCH')

        f = open(self.file_name, 'rb')
        f.seek(self.offset)
        c.setopt(pycurl.READFUNCTION, f.read)
        c.setopt(pycurl.INFILESIZE, self._request_length)
        c.setopt(pycurl.HTTPHEADER, self.headers)
        self.request = c

    def _prepare_response(self, content):
        output = StringIO.StringIO()
        output.write(content)
        self.response = output.getvalue()
