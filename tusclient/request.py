import pycurl


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

        self.handle.setopt(pycurl.URL, uploader.url)
        self.handle.setopt(pycurl.HEADERFUNCTION, self._prepare_response_header)
        self.handle.setopt(pycurl.UPLOAD, 1)
        self.handle.setopt(pycurl.CUSTOMREQUEST, 'PATCH')

        self.file = open(uploader.file_path, 'rb')
        self.file.seek(uploader.offset)
        self.handle.setopt(pycurl.READFUNCTION, self.file.read)
        self.handle.setopt(pycurl.INFILESIZE, uploader.request_length)

        headers = ["upload-offset: {}".format(uploader.offset)] + uploader.headers_as_list
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
    def status_code(self):
        """
        Return request status code.
        """
        return self.handle.getinfo(pycurl.RESPONSE_CODE)

    def perform(self):
        """
        Perform actual request.
        """
        self.handle.perform()

    def close(self):
        """
        close request handle and end request session
        """
        self.handle.close()
        self.file.close()
