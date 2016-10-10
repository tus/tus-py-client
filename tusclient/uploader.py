from __future__ import print_function
import os

from six import iteritems
import requests

from tusclient.exceptions import TusUploadFailed
from tusclient.request import TusRequest


class Uploader(object):
    """
    Object to control upload related functions.

    :Attributes:
        - file_path (str):
            This is the path(absolute/relative) to the file that is intended for upload
            to the tus server. On instantiation this attribute is required.
        -  url (Optional[str]):
            If the upload url for the file is known, it can be passed to the constructor.
            This may happen when you resume an upload.
        - client (<tusclient.client.TusClient>):
            An instance of `tusclient.client.TusClient`. This would tell the uploader instance
            what client it is operating with. Although this argument is optional, it is only
            optional if the 'url' argument is specified.
        - chunk_size (int):
            This tells the uploader what chunk size(in bytes) should be uploaded when the
            method `upload_chunk` is called. This defaults to 2 * 1024 * 1024 i.e 2kb if not
            specified.
        - offset (int):
            The offset value of the upload indicates the current position of the file upload.
        - file_size (int):
            The size of the file.
        - stop_at (int):
            At what offset value the upload should stop.
        - request (<tusclient.request.TusRequest>):
            A http Request instance of the last chunk uploaded.

    :Constructor Args:
        - file_path (str)
        -  url (Optional[str])
        - client (Optional [<tusclient.client.TusClient>])
        - chunk_size (Optional[int])
    """
    DEFAULT_HEADERS = {"Content-Type": "application/offset+octet-stream",
                       "Tus-Resumable": "1.0.0"}
    DEFAULT_CHUNK_SIZE = 2 * 1024 * 1024  # 2kb

    def __init__(self, file_path, url=None, client=None, chunk_size=None):
        if not os.path.isfile(file_path):
            raise ValueError("invalid file {}".format(file_path))

        if url is None and client is None:
            raise ValueError("Either 'url' or 'client' cannot be None.")

        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.stop_at = self.file_size
        self.client = client
        self.url = url or self.create_url()
        self.offset = self.get_offset()
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        self.request = None

    # it is important to have this as a @property so it gets
    # updated client headers.
    @property
    def headers(self):
        """
        Return headers of the uploader instance. This would include the headers of the
        client insance.
        """
        client_headers = getattr(self.client, 'headers') or {}
        return dict(self.DEFAULT_HEADERS, **client_headers)

    @property
    def headers_as_list(self):
        """
        Does the same as 'headers' except it is returned as a list.
        """
        headers = self.headers
        headers_list = ['{}: {}'.format(key, value) for key, value in iteritems(headers)]
        return headers_list

    def get_offset(self):
        """
        Return offset from tus server.

        This is different from the instance attribute 'offset' because this makes an
        http request to the tus server to retrieve the offset.
        """
        resp = requests.head(self.url, headers=self.headers)
        return int(resp.headers["upload-offset"])

    def create_url(self):
        """
        Return upload url.

        Makes request to tus server to create a new upload url for the required file upload.
        """
        headers = self.headers
        headers['upload-length'] = str(self.file_size)
        resp = requests.post(self.client.url, headers=headers)
        return resp.headers.get("location")

    @property
    def request_length(self):
        """
        Return length of next chunk upload.
        """
        remainder = self.stop_at - self.offset
        return self.chunk_size if remainder > self.chunk_size else remainder

    def verify_upload(self):
        """
        Confirm that the last upload was sucessful.
        Raises TusUploadFailed exception if the upload was not sucessful.
        """
        if self.request.status_code == 204:
            msg = '{} bytes uploaded ...'.format(self.request.response_headers.get('upload-offset'))
            print(msg)
            return True
        else:
            raise TusUploadFailed

    def _do_request(self):
        # TODO: Maybe the request should not be re-created everytime.
        #      The request handle could be left open until upload is done instead.
        self.request = TusRequest(self)
        try:
            self.request.perform()
            self.verify_upload()
        finally:
            self.request.close()

    def upload(self, stop_at=None):
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
        else:
            print("maximum upload specified({} bytes) has been reached".format(self.stop_at))

    def upload_chunk(self):
        """
        Upload chunk of file.
        """
        self._do_request()
        self.offset += self.request_length
