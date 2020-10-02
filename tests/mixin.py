import unittest

import responses

from tusclient import client


class Mixin(unittest.TestCase):
    @responses.activate
    def setUp(self):
        self.client = client.TusClient('http://tusd.tusdemo.net/files/')
        self.url = 'http://tusd.tusdemo.net/files/15acd89eabdf5738ffc'
        responses.add(responses.HEAD, self.url,
                      adding_headers={"upload-offset": "0"})
        self.uploader = self.client.uploader('./LICENSE', url=self.url)
