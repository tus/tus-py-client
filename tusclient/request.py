import pycurl


class TusRequest(object):
    def __init__(self, uploader):
        self.handle = pycurl.Curl()
        self.response_headers = {}

        self.handle.setopt(pycurl.URL, uploader.url)
        self.handle.setopt(pycurl.HEADERFUNCTION, self._prepare_response_header)
        self.handle.setopt(pycurl.UPLOAD, 1)
        self.handle.setopt(pycurl.CUSTOMREQUEST, 'PATCH')

        self.file = open(uploader.file_name, 'rb')
        self.file.seek(uploader.offset)
        self.handle.setopt(pycurl.READFUNCTION, self.file.read)
        self.handle.setopt(pycurl.INFILESIZE, uploader.request_length)

        headers = ["upload-offset: {}".format(uploader.offset)] + uploader.headers_as_list()
        self.handle.setopt(pycurl.HTTPHEADER, headers)

    def _prepare_response_header(self, header_line):
        header_line = header_line.decode('iso-8859-1')
        if ':' not in header_line:
            return

        name, value = header_line.split(':', 1)
        name = name.strip()
        value = value.strip()
        self.response_headers[name.lower()] = value

    @property
    def status_code(self):
        return self.handle.getinfo(pycurl.RESPONSE_CODE)

    def perform(self):
        self.handle.perform()

    def close(self):
        self.handle.close()
        self.file.close()
