import unittest
from unittest import mock
import asyncio

from aioresponses import aioresponses, CallbackResult
import responses
import pytest

from tusclient import exceptions, client


class AsyncUploaderTest(unittest.TestCase):
    @responses.activate
    def setUp(self):
        self.client = client.TusClient('http://tusd.tusdemo.net/files/')
        self.url = 'http://tusd.tusdemo.net/files/15acd89eabdf5738ffc'
        responses.add(responses.HEAD, self.url,
                      adding_headers={"upload-offset": "0"})
        self.loop = asyncio.new_event_loop()
        self.async_uploader = self.client.async_uploader(
            './LICENSE', url=self.url)

    def _validate_request(self, url, **kwargs):
        self.assertEqual(self.url, str(url))
        req_headers = kwargs['headers']
        self.assertEqual(req_headers.get('Tus-Resumable'), '1.0.0')

        body = kwargs['data']
        with open('./LICENSE', 'rb') as stream:
            expected_content = stream.read()
            self.assertEqual(expected_content, body)

        response_headers = {
            'upload-offset': str(self.async_uploader.offset + self.async_uploader.get_request_length())}

        return CallbackResult(status=204, headers=response_headers)

    def test_upload_chunk(self):
        with aioresponses() as resps:
            resps.patch(self.url, callback=self._validate_request)

            request_length = self.async_uploader.get_request_length()
            self.loop.run_until_complete(self.async_uploader.upload_chunk())
            self.assertEqual(self.async_uploader.offset, request_length)

    def test_upload(self):
        with aioresponses() as resps:
            resps.patch(self.url, callback=self._validate_request)

            self.loop.run_until_complete(self.async_uploader.upload())
            self.assertEqual(self.async_uploader.offset,
                             self.async_uploader.get_file_size())

    def test_upload_retry(self):
        num_of_retries = 3
        self.async_uploader.retries = num_of_retries
        self.async_uploader.retry_delay = 3
        with aioresponses() as resps:
            resps.patch(self.url, status=00)

            self.assertEqual(self.async_uploader._retried, 0)
            with pytest.raises(exceptions.TusCommunicationError):
                self.loop.run_until_complete(
                    self.async_uploader.upload_chunk())

            self.assertEqual(self.async_uploader._retried, num_of_retries)
