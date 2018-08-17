import os
from base64 import b64encode

import six
import responses
import pytest
import mock

from tusclient import exceptions
from tusclient.storage import filestorage
from tests import mixin


class UploaderTest(mixin.Mixin):

    def mock_pycurl(self, request_mock):
        request_mock = request_mock.return_value
        request_mock.status_code = 204
        request_mock.response_headers = {
            'upload-offset': self.uploader.offset + self.uploader.request_length}
        request_mock.perform.return_value = None
        request_mock.close.return_value = None
        return request_mock

    def test_instance_attributes(self):
        self.assertEqual(self.uploader.chunk_size, self.uploader.DEFAULT_CHUNK_SIZE)
        self.assertEqual(self.uploader.client, self.client)
        self.assertEqual(self.uploader.offset, 0)

    def test_headers(self):
        self.assertEqual(self.uploader.headers, {"Tus-Resumable": "1.0.0"})

        self.client.set_headers({'foo': 'bar'})
        self.assertEqual(self.uploader.headers, {"Tus-Resumable": "1.0.0", 'foo': 'bar'})

    def test_headers_as_list(self):
        six.assertCountEqual(self, self.uploader.headers_as_list,
                             ["Tus-Resumable: 1.0.0"])

        self.client.set_headers({'foo': 'bar'})
        six.assertCountEqual(self, self.uploader.headers_as_list,
                             ['Tus-Resumable: 1.0.0', 'foo: bar'])

    @responses.activate
    def test_get_offset(self):
        responses.add(responses.HEAD, self.uploader.url,
                      adding_headers={"upload-offset": "300"})
        self.assertEqual(self.uploader.get_offset(), 300)

    def test_encode_metadata(self):
        self.uploader.metadata = {'foo': 'bar', 'red': 'blue'}
        encoded_metadata = ['foo' + ' ' + b64encode(b'bar').decode('ascii'),
                            'red' + ' ' + b64encode(b'blue').decode('ascii')]
        six.assertCountEqual(self, self.uploader.encode_metadata(), encoded_metadata)

        with pytest.raises(ValueError):
            self.uploader.metadata = {'foo, ': 'bar'}
            self.uploader.encode_metadata()

    @responses.activate
    def test_create_url_absolute(self):
        responses.add(responses.POST, self.client.url,
                      adding_headers={"location": 'http://master.tus.io/files/foo'})
        self.assertEqual(self.uploader.create_url(), 'http://master.tus.io/files/foo')

    @responses.activate
    def test_create_url_relative(self):
        responses.add(responses.POST, self.client.url,
                      adding_headers={"location": "/files/foo"})
        self.assertEqual(self.uploader.create_url(), 'http://master.tus.io/files/foo')

    @responses.activate 
    def test_get_url(self):
        responses.add(responses.POST, self.client.url,
                      adding_headers={"location": 'http://master.tus.io/files/foo'})
        self.assertEqual(self.uploader.get_url(), 'http://master.tus.io/files/foo')

        # test for stored urls
        responses.add(responses.HEAD, 'http://master.tus.io/files/foo_bar',
                      adding_headers={"upload-offset": "0"})
        storage_path = '{}/storage_file'.format(os.path.dirname(os.path.abspath(__file__)))
        resumable_uploader = self.client.uploader(
            file_path='./LICENSE', store_url=True, url_storage=filestorage.FileStorage(storage_path)
        )
        self.assertEqual(resumable_uploader.get_url(), 'http://master.tus.io/files/foo_bar')

    def test_request_length(self):
        self.uploader.chunk_size = 200
        self.assertEqual(self.uploader.request_length, 200)

        self.uploader.chunk_size = self.uploader.file_size + 3000
        self.assertEqual(self.uploader.request_length, self.uploader.file_size)

    @mock.patch('tusclient.uploader.TusRequest')
    def test_verify_upload(self, request_mock):
        request_mock = self.mock_pycurl(request_mock)
        request_mock.status_code = 00

        with pytest.raises(exceptions.TusUploadFailed):
            self.uploader.upload_chunk()
            self.uploader.verify_upload()

        request_mock.status_code = 204
        self.uploader.upload_chunk()
        self.assertIs(self.uploader.verify_upload(), True)

    def test_get_file_stream(self):
        with open('./LICENSE', 'rb') as fs:
            self.uploader.file_stream = fs
            self.uploader.file_path = None
            self.assertEqual(self.uploader.file_stream, self.uploader.get_file_stream())

        with open('./AUTHORS', 'rb') as fs:
            self.uploader.file_stream = None
            self.uploader.file_path = './AUTHORS'
            self.assertEqual(fs.read(), self.uploader.get_file_stream().read())

    def test_file_size(self):
        self.assertEqual(self.uploader.file_size, os.path.getsize(self.uploader.file_path))

        with open('./AUTHORS', 'rb') as fs:
            self.uploader.file_stream = fs
            self.uploader.file_path = None
            self.assertEqual(self.uploader.file_size, os.path.getsize('./AUTHORS'))

    @mock.patch('tusclient.uploader.TusRequest')
    def test_upload_chunk(self, request_mock):
        self.mock_pycurl(request_mock)

        self.uploader.offset = 0
        request_length = self.uploader.request_length
        self.uploader.upload_chunk()
        self.assertEqual(self.uploader.offset, request_length)

    @mock.patch('tusclient.uploader.TusRequest')
    def test_upload(self, request_mock):
        self.mock_pycurl(request_mock)

        self.uploader.upload()
        self.assertEqual(self.uploader.offset, self.uploader.file_size)

    @mock.patch('tusclient.uploader.TusRequest')
    def test_upload_retry(self, request_mock):
        NUM_OF_RETRIES = 3
        self.uploader.retries = NUM_OF_RETRIES
        self.uploader.retry_delay = 3

        request_mock = self.mock_pycurl(request_mock)
        request_mock.status_code = 00

        self.assertEqual(self.uploader._retried, 0)
        with pytest.raises(exceptions.TusCommunicationError):
            self.uploader.upload_chunk()
        self.assertEqual(self.uploader._retried, NUM_OF_RETRIES)

    @mock.patch('tusclient.uploader.TusRequest')
    def test_upload_checksum(self, request_mock):
        self.mock_pycurl(request_mock)

        self.uploader.checksum_algorithm_name = "sha1"
        self.uploader.upload()
        self.assertEqual(self.uploader.offset, self.uploader.file_size)
    
    def test_invalid_checksum_algorithm_name(self):
        with pytest.raises(ValueError):
            self.uploader.checksum_algorithm_name = \
                "hopefully not a support checksum algorithm name"