from tusclient import upload


class EndPoint(object):

    def __init__(self, url, client=None):
        self.url = url
        self.uploads = {}
        self.client = client

    def file_upload(self, filename, url=None):
        if not url or not self.uploads.get(url):
            self.uploads[url] = upload.FileUpload(filename, end_point=self, url=url)
        return self.uploads[url]

    @property
    def headers(self):
        if self.client:
            return self.client.headers
        return {}
