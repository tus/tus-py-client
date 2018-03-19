import http.client
from future.moves.urllib.parse import urlparse

from tusclient.exceptions import TusUploadFailed


class TusRequest(object):
    """
    Http Request Abstraction.

    Sets up tus custom http request on instantiation.

    requires argument 'uploader' an instance of tusclient.uploader.Uploader
    on instantiation.

    :Attributes:
        - handle (<http.client.HTTPConnection>)
        - response_headers (dict)
        - file (file):
            The file that is being uploaded.
    """

    def __init__(self, uploader):
        url = urlparse(uploader.url)
        if url.scheme == 'https':
            self.handle = http.client.HTTPSConnection(url.hostname, url.port)
        else:
            self.handle = http.client.HTTPConnection(url.hostname, url.port)
        self._url = url

        self.response_headers = {}
        self.status_code = None
        self.file = uploader.get_file_stream()
        self.file.seek(uploader.offset)

        self._request_headers = {
            'upload-offset': uploader.offset,
            'Content-Type': 'application/offset+octet-stream'
        }
        self._request_headers.update(uploader.headers)
        self._content_length = uploader.request_length
        self._response = None

    @property
    def response_content(self):
        """
        Return response data
        """
        return self._response.read()

    def perform(self):
        """
        Perform actual request.
        """
        try:
            host = '{}://{}'.format(self._url.scheme, self._url.netloc)
            path = self._url.geturl().replace(host, '', 1)

            self.handle.request("PATCH", path, self.file.read(self._content_length), self._request_headers)
            self._response = self.handle.getresponse()
            self.status_code = self._response.status
            self.response_headers = {k.lower(): v for k, v in self._response.getheaders()}
        except http.client.HTTPException as e:
            raise TusUploadFailed(e)

    def close(self):
        """
        close request handle and end request session
        """
        self.handle.close()
