import os

import pycurl
import requests

from tusclient.exceptions import TusUploadFailed


class FileUpload(object):
    DEFAULT_HEADERS = {"Expect": '',
                       "Content-Type": "application/offset+octet-stream",
                       "Tus-Resumable": "1.0.0"}
    DEFAULT_CHUNK_SIZE = 2 * 1024 * 1024  # 2kb

    def __init__(self, file_name, url=None, end_point=None, chunk_size=None):
        if not os.path.isfile(file_name):
            raise ValueError("invalid file {}".format(file_name))

        self.file_name = file_name
        self.file_size = os.path.getsize(file_name)
        self.stop_at = self.file_size
        self.end_point = end_point

        if not url:
            url = self.create_url()
        self.url = url
        self.offset = self.get_offset()
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        self.response_headers = {}
        self.request = None

    @property
    def headers(self):
        return dict(self.DEFAULT_HEADERS, **self.end_point.headers)

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
        resp = requests.post(self.end_point.url, headers=headers)
        return resp.headers.get("location")

    @property
    def _request_length(self):
        remainder = self.stop_at - self.offset
        return self.chunk_size if remainder > self.chunk_size else remainder

    def _end_request(self):
        if self.request:
            self.request.close()

    def _prepare_response_header(self, header_line):
        header_line = header_line.decode('iso-8859-1')
        if ':' not in header_line:
            return

        name, value = header_line.split(':', 1)
        name = name.strip()
        value = value.strip()
        self.response_headers[name.lower()] = value

    def _prepare_request(self):
        self.request = pycurl.Curl()
        self.request.setopt(pycurl.URL, self.url)

        self.request.setopt(pycurl.HEADERFUNCTION, self._prepare_response_header)
        self.request.setopt(pycurl.UPLOAD, 1)
        self.request.setopt(pycurl.CUSTOMREQUEST, 'PATCH')

        f = open(self.file_name, 'rb')
        f.seek(self.offset)
        self.request.setopt(pycurl.READFUNCTION, f.read)
        self.request.setopt(pycurl.INFILESIZE, self._request_length)

        headers = ["upload-offset: {}".format(self.offset)] + self.headers_as_list()
        self.request.setopt(pycurl.HTTPHEADER, headers)

    def verify_upload(self):
        response_code = self.request.getinfo(pycurl.RESPONSE_CODE)
        if response_code == 204:
            print 'uploaded {} bytes ...'.format(self.response_headers.get('upload-offset'))
            return True
        else:
            raise TusUploadFailed

    def _do_request(self):
        self._prepare_request()
        try:
            self.request.perform()
            self.verify_upload()
        finally:
            self._end_request()

    def upload(self, stop_at=None):
        if stop_at:
            self.stop_at = stop_at

        while self.offset < self.stop_at:
            self.upload_chunk()
        else:
            print "maximum upload specified({} bytes) has been reached".format(self.stop_at)

    def upload_chunk(self):
        self._do_request()
        self.offset += self._request_length
