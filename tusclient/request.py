import pycurl
import certifi
import six

from tusclient.exceptions import TusUploadFailed


class TusRequest(object):
    """
    Http Request Abstraction.

    Sets up tus custom http request on instantiation.

    requires argument 'uploader' an instance of tusclient.uploader.Uploader
    on instantiation.

    :Attributes:
        - handle (<pycurl.Curl>)
        - response_headers (dict)
        - file (file):
            The file that is being uploaded.
    """

    def __init__(self, uploader):
        self.handle = pycurl.Curl()
        self.response_headers = {}
        self.output = six.StringIO()
        self.status_code = None

        self.handle.setopt(pycurl.CAINFO, certifi.where())
        self.handle.setopt(pycurl.URL, uploader.url)
        self.handle.setopt(pycurl.HEADERFUNCTION, self._prepare_response_header)
        self.handle.setopt(pycurl.UPLOAD, 1)
        self.handle.setopt(pycurl.CUSTOMREQUEST, 'PATCH')

        self.file = uploader.get_file_stream()
        self.file.seek(uploader.offset)
        self.handle.setopt(pycurl.READFUNCTION, self.file.read)
        self.handle.setopt(pycurl.WRITEFUNCTION, self.output.write)
        self.handle.setopt(pycurl.INFILESIZE, uploader.request_length)

        headers = ["upload-offset: {}".format(uploader.offset),
                   "Content-Type: application/offset+octet-stream"] + uploader.headers_as_list
        self.handle.setopt(pycurl.HTTPHEADER, headers)

    def _prepare_response_header(self, header_line):
        # prepares response header and adds it to 'response_headers'
        # attribute
        header_line = header_line.decode('iso-8859-1')
        if ':' not in header_line:
            return

        name, value = header_line.split(':', 1)
        name = name.strip()
        value = value.strip()
        self.response_headers[name.lower()] = value

    @property
    def response_content(self):
        """
        Return response data
        """
        return self.output.getvalue()

    def perform(self):
        """
        Perform actual request.
        """
        try:
            self.handle.perform()
            self._finish_request()
        except pycurl.error as e:
            raise TusUploadFailed(e)

    def _finish_request(self):
        self.status_code = self.handle.getinfo(pycurl.RESPONSE_CODE)

    def close(self):
        """
        close request handle and end request session
        """
        self.handle.close()
