import unittest

import responses

from tusclient import client


class Mixin(unittest.TestCase):
    @responses.activate
    def setUp(self):
        self.client = client.TusClient('http://master.tus.io/files/')
        url = 'http://master.tus.io/files/15acd89eabdf5738ffc'
        responses.add(responses.HEAD, url,
                      adding_headers={"upload-offset": "0"})
        self.uploader = self.client.uploader('./LICENSE', url)
