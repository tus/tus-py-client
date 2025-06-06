import os
import io
import tempfile
from base64 import b64encode
from unittest import mock

import responses
from responses import matchers
from parametrize import parametrize
import pytest

from tusclient import exceptions
from tusclient.storage import filestorage
from tests import mixin


FILEPATH_TEXT = "tests/sample_files/text.txt"
FILEPATH_BINARY = "tests/sample_files/binary.png"


class UploaderTest(mixin.Mixin):

    def mock_request(self, request_mock):
        request_mock = request_mock.return_value
        request_mock.status_code = 204
        request_mock.response_headers = {
            'upload-offset': self.uploader.offset + self.uploader.get_request_length()}
        request_mock.perform.return_value = None
        return request_mock

    def test_instance_attributes(self):
        self.assertEqual(self.uploader.chunk_size, self.uploader.DEFAULT_CHUNK_SIZE)
        self.assertEqual(self.uploader.client, self.client)
        self.assertEqual(self.uploader.offset, 0)

    def test_headers(self):
        self.assertEqual(self.uploader.get_headers(), {"Tus-Resumable": "1.0.0"})

        self.client.set_headers({'foo': 'bar'})
        self.assertEqual(self.uploader.get_headers(), {"Tus-Resumable": "1.0.0", 'foo': 'bar'})

    @responses.activate
    def test_get_offset(self):
        responses.add(responses.HEAD, self.uploader.url,
                      adding_headers={"upload-offset": "300"})
        self.assertEqual(self.uploader.get_offset(), 300)

    def test_encode_metadata(self):
        self.uploader.metadata = {'foo': 'bar', 'red': 'blue'}
        encoded_metadata = ['foo' + ' ' + b64encode(b'bar').decode('ascii'),
                            'red' + ' ' + b64encode(b'blue').decode('ascii')]
        self.assertCountEqual(self.uploader.encode_metadata(), encoded_metadata)

        with pytest.raises(ValueError):
            self.uploader.metadata = {'foo, ': 'bar'}
            self.uploader.encode_metadata()

    def test_encode_metadata_utf8(self):
        self.uploader.metadata = {'foo': 'bär', 'red': '🔵'}
        self.uploader.metadata_encoding = 'utf-8'
        encoded_metadata = [
            'foo ' + b64encode('bär'.encode('utf-8')).decode('ascii'),
            'red ' + b64encode('🔵'.encode('utf-8')).decode('ascii')
        ]
        self.assertCountEqual(self.uploader.encode_metadata(), encoded_metadata)

    @responses.activate
    def test_create_url_absolute(self):
        responses.add(responses.POST, self.client.url,
                      adding_headers={"location": 'http://tusd.tusdemo.net/files/foo'})
        self.assertEqual(self.uploader.create_url(), 'http://tusd.tusdemo.net/files/foo')

    @responses.activate
    def test_create_url_relative(self):
        responses.add(responses.POST, self.client.url,
                      adding_headers={"location": "/files/foo"})
        self.assertEqual(self.uploader.create_url(), 'http://tusd.tusdemo.net/files/foo')

    @parametrize(
        "filename",
        [FILEPATH_TEXT, FILEPATH_BINARY],
    )
    @responses.activate
    def test_url(self, filename: str):
        # test for stored urls
        responses.add(responses.HEAD, 'http://tusd.tusdemo.net/files/foo_bar',
                      adding_headers={"upload-offset": "10"})
        storage_path = '{}/storage_file'.format(os.path.dirname(os.path.abspath(__file__)))
        resumable_uploader = self.client.uploader(
            file_path=filename, store_url=True, url_storage=filestorage.FileStorage(storage_path)
        )
        self.assertEqual(resumable_uploader.url, "http://tusd.tusdemo.net/files/foo_bar")
        self.assertEqual(resumable_uploader.offset, 10)

    @parametrize(
        "filename",
        [FILEPATH_TEXT, FILEPATH_BINARY],
    )
    @responses.activate
    def test_url_voided(self, filename: str):
        # Test that voided stored url are cleared
        responses.add(
            responses.POST,
            self.client.url,
            adding_headers={"location": "http://tusd.tusdemo.net/files/foo"},
        )
        responses.add(
            responses.HEAD,
            "http://tusd.tusdemo.net/files/foo",
            status=404,
        )

        # Create temporary storage file.
        temp_fp = tempfile.NamedTemporaryFile(delete=False)
        storage = filestorage.FileStorage(temp_fp.name)
        uploader = self.client.uploader(
            file_path=filename, store_url=True, url_storage=storage
        )

        # Conduct only POST creation so that we'd get a storage entry.
        uploader.upload(stop_at=-1)
        key = uploader._get_fingerprint()
        # First ensure that an entry was created and stored.
        self.assertIsNotNone(uploader.url)
        self.assertIsNotNone(storage.get_item(key))

        # Now start a new upload, resuming where we left off.
        resumed_uploader = self.client.uploader(
            file_path=filename, store_url=True, url_storage=storage
        )
        # HEAD response was 404 so url and storage has to be voided.
        self.assertIsNone(resumed_uploader.url)
        self.assertIsNone(storage.get_item(key))

        # Remove the temporary storage file.
        storage.close()
        temp_fp.close()
        os.remove(temp_fp.name)

    def test_request_length(self):
        self.uploader.chunk_size = 200
        self.assertEqual(self.uploader.get_request_length(), 200)

        self.uploader.chunk_size = self.uploader.get_file_size() + 3000
        self.assertEqual(self.uploader.get_request_length(), self.uploader.get_file_size())

    @parametrize(
        "filename",
        [FILEPATH_TEXT, FILEPATH_BINARY],
    )
    def test_get_file_stream(self, filename: str):
        with open(filename, "rb") as fs:
            self.uploader.file_stream = fs
            self.uploader.file_path = None
            self.assertEqual(self.uploader.file_stream, self.uploader.get_file_stream())

        with open(filename, "rb") as fs:
            self.uploader.file_stream = None
            self.uploader.file_path = filename
            with self.uploader.get_file_stream() as stream:
                self.assertEqual(fs.read(), stream.read())

    @parametrize(
        "filename",
        [FILEPATH_TEXT, FILEPATH_BINARY],
    )
    def test_file_size(self, filename: str):
        self.assertEqual(self.uploader.get_file_size(), os.path.getsize(self.uploader.file_path))

        with open(filename, "rb") as fs:
            self.uploader.file_stream = fs
            self.uploader.file_path = None
            self.assertEqual(self.uploader.get_file_size(), os.path.getsize(filename))

    @mock.patch('tusclient.uploader.uploader.TusRequest')
    def test_upload_chunk(self, request_mock):
        self.mock_request(request_mock)

        self.uploader.offset = 0
        request_length = self.uploader.get_request_length()
        self.uploader.upload_chunk()
        self.assertEqual(self.uploader.offset, request_length)

    @responses.activate
    def test_upload_chunk_with_creation(self):
        responses.add(
            responses.POST, self.client.url,
            adding_headers={
                "location": f"{self.client.url}hello"
            }
        )
        responses.add(
            responses.PATCH,
            f"{self.client.url}hello",
            adding_headers={
                "upload-offset": "5"
            }
        )

        uploader = self.client.uploader(
            file_stream=io.BytesIO(b"hello")
        )
        uploader.upload_chunk()

        self.assertEqual(uploader.url, f"{self.client.url}hello")

    @mock.patch('tusclient.uploader.uploader.TusRequest')
    def test_upload(self, request_mock):
        self.mock_request(request_mock)

        self.uploader.upload()
        self.assertEqual(self.uploader.offset, self.uploader.get_file_size())

    @mock.patch('tusclient.uploader.uploader.TusRequest')
    def test_upload_retry(self, request_mock):
        num_of_retries = 3
        self.uploader.retries = num_of_retries
        self.uploader.retry_delay = 3

        request_mock = self.mock_request(request_mock)
        request_mock.status_code = 00

        self.assertEqual(self.uploader._retried, 0)
        with pytest.raises(exceptions.TusCommunicationError):
            self.uploader.upload_chunk()
        self.assertEqual(self.uploader._retried, num_of_retries)

    @responses.activate
    def test_upload_empty(self):
        responses.add(
            responses.POST, self.client.url,
            adding_headers={
                "upload-offset": "0",
                "location": f"{self.client.url}this-is-not-used"
            }
        )
        responses.add(
            responses.PATCH,
            f"{self.client.url}this-is-not-used",
            body=ValueError("PATCH request not allowed for empty file")
        )

        # Upload an empty file
        uploader = self.client.uploader(
            file_stream=io.BytesIO(b"")
        )
        uploader.upload()

        # Upload URL being set means the POST request was sent and the empty
        # file was uploaded without a single PATCH request.
        self.assertTrue(uploader.url)

    @mock.patch('tusclient.uploader.uploader.TusRequest')
    def test_upload_checksum(self, request_mock):
        self.mock_request(request_mock)
        self.uploader.upload_checksum = True
        self.uploader.upload()
        self.assertEqual(self.uploader.offset, self.uploader.get_file_size())

    @parametrize("chunk_size", [1, 2, 3, 4, 5, 6])
    @responses.activate
    def test_upload_length_deferred(self, chunk_size: int):
        upload_url = f"{self.client.url}test_upload_length_deferred"

        responses.head(
            upload_url,
            adding_headers={"upload-offset": "0", "Upload-Defer-Length": "1"},
        )
        uploader = self.client.uploader(
            file_stream=io.BytesIO(b"hello"),
            url=upload_url,
            chunk_size=chunk_size,
            upload_length_deferred=True,
        )
        self.assertTrue(uploader.upload_length_deferred)
        self.assertTrue(uploader.stop_at is None)

        offset = 0
        while not (offset + chunk_size > 5):
            next_offset = min(offset + chunk_size, 5)
            responses.patch(
                upload_url,
                adding_headers={"upload-offset": str(next_offset)},
                match=[matchers.header_matcher({"upload-offset": str(offset)})],
            )
            offset = next_offset
        last_req_headers = {"upload-offset": str(offset)}
        last_req_headers["upload-length"] = "5"
        responses.patch(
            upload_url,
            adding_headers={"upload-offset": "5"},
            match=[matchers.header_matcher(last_req_headers)],
        )

        uploader.upload()
        self.assertEqual(uploader.offset, 5)
        self.assertEqual(uploader.stop_at, 5)
