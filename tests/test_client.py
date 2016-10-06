import unittest

import responses

from tusclient import client
from tusclient.uploader import Uploader


class TusClientTest(unittest.TestCase):
    def setUp(self):
        self.client = client.TusClient('http://master.tus.io/files/',
                                       headers={'foo': 'bar'})

    def test_instance_attributes(self):
        self.assertEqual(self.client.url, 'http://master.tus.io/files/')
        self.assertEqual(self.client.headers, {'foo': 'bar'})

    def test_set_headers(self):
        self.client.set_headers({'foo': 'bar tender'})
        self.assertEqual(self.client.headers, {'foo': 'bar tender'})

        # uploader headers must update when client headers change
        self.client.set_headers({'food': 'at the bar'})
        self.assertEqual(self.client.headers, {'foo': 'bar tender', 'food': 'at the bar'})

    @responses.activate
    def test_uploader(self):
        url = 'http://master.tus.io/files/15acd89eabdf5738ffc'
        responses.add(responses.HEAD, url,
                      adding_headers={"upload-offset": "0"})

        uploader = self.client.uploader('./LICENSE', url=url)

        self.assertIsInstance(uploader, Uploader)
        self.assertEqual(uploader.client, self.client)
