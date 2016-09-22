import os

import requests

from tusclient import upload


class EndPoint(object):

    def __init__(self, url):
        self.url = url
        self.uploads = {}

    def file_upload(self, filename, url=None):
        if not url:
            url = self.create_url(filename)
            self.uploads[url] = upload.FileUpload(filename, url)
        return self.uploads[url]

    def create_url(self, filename):
        filesize = os.path.getsize(filename)
        resp = requests.post(self.url, headers={
            "Upload-Length": str(filesize), "Tus-Resumable": "1.0.0"})
        if resp.status_code != 201:
            # fail here
            pass
        return str(resp.headers["Location"])
