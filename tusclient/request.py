import errno
import base64
import requests

from tusclient.exceptions import TusUploadFailed


class TusRequest(object):
    """
    Http Request Abstraction.

    Sets up tus custom http request on instantiation.

    requires argument 'uploader' an instance of tusclient.uploader.Uploader
    on instantiation.

    :Attributes:
        - handle (<requests.Session>)
        - response_headers (dict)
        - file (file):
            The file that is being uploaded.
    """

    def __init__(self, uploader):
        self.handle = requests.Session()
        self._url = uploader.url

        self.response_headers = {}
        self.status_code = None
        self.file = uploader.get_file_stream()
        self.file.seek(uploader.offset)

        self._request_headers = {
            'upload-offset': str(uploader.offset),
            'Content-Type': 'application/offset+octet-stream'
        }
        self._request_headers.update(uploader.headers)
        self._content_length = uploader.request_length
        self._upload_checksum = uploader.upload_checksum
        self._checksum_algorithm = uploader.checksum_algorithm
        self._checksum_algorithm_name = uploader.checksum_algorithm_name
        self._response = None

    @property
    def response_content(self):
        """
        Return response data
        """
        return self._response.content

    def perform(self):
        """
        Perform actual request.
        """
        try:
            chunk = self.file.read(self._content_length)
            if self._upload_checksum:
                self._request_headers["upload-checksum"] = \
                    " ".join((
                        self._checksum_algorithm_name,
                        base64.b64encode(
                            self._checksum_algorithm(chunk).digest()
                        ).decode("ascii"),
                    ))
            self._response = self.handle.patch(self._url, data=chunk, headers=self._request_headers)
            self.status_code = self._response.status_code
            self.response_headers = {k.lower(): v for k, v in self._response.headers.items()}
        except requests.exceptions.RequestException as e:
            raise TusUploadFailed(e)

    def close(self):
        """
        close request handle and end request session
        """
        self.handle.close()