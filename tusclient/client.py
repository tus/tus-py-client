from tusclient.uploader import Uploader


class TusClient(object):

    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}

    # you can set authentication headers with this.
    def set_headers(self, headers):
        self.headers.update(headers)

    def uploader(self, *args, **kwargs):
        kwargs['client'] = self
        return Uploader(*args, **kwargs)
