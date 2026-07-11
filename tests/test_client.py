import unittest
from io import BytesIO

import responses

from tusclient import client
from tusclient.exceptions import TusCommunicationError
from tusclient.fingerprint.interface import Fingerprint
from tusclient.protocol_generated import (
    DEFAULT_REQUEST_HEADERS,
    CREATE_UPLOAD_METHOD,
    LOCATION_HEADER_NAME,
    TERMINATE_UPLOAD_METHOD,
    TUS_PROTOCOL_REQUEST_HEADERS,
    UPLOAD_BODY_CONTENT_TYPE,
    UPLOAD_BODY_CONTENT_TYPE_HEADER_NAME,
    UPLOAD_LENGTH_HEADER_NAME,
    UPLOAD_OFFSET_HEADER_NAME,
    upload_body_headers,
)
from tusclient.request_lifecycle import RequestLifecycleHooks
from tusclient.storage.interface import Storage
from tusclient.uploader import Uploader, AsyncUploader


class MemoryStorage(Storage):
    def __init__(self):
        self.values = {}

    def get_item(self, key):
        return self.values.get(key)

    def set_item(self, key, value):
        self.values[key] = value

    def remove_item(self, key):
        self.values.pop(key, None)


class FixedFingerprint(Fingerprint):
    def __init__(self, value):
        self.value = value

    def get_fingerprint(self, fs):
        return self.value


class TusClientTest(unittest.TestCase):
    def setUp(self):
        self.client = client.TusClient('http://tusd.tusdemo.net/files/',
                                       headers={'foo': 'bar'})

    def test_instance_attributes(self):
        self.assertEqual(self.client.url, 'http://tusd.tusdemo.net/files/')
        self.assertEqual(self.client.headers, {'foo': 'bar'})
        self.assertFalse(self.client.add_request_id)

    def test_set_headers(self):
        self.client.set_headers({'foo': 'bar tender'})
        self.assertEqual(self.client.headers, {'foo': 'bar tender'})

        # uploader headers must update when client headers change
        self.client.set_headers({'food': 'at the bar'})
        self.assertEqual(self.client.headers, {'foo': 'bar tender', 'food': 'at the bar'})

    def test_request_id_header_toggle(self):
        self.client.enable_request_id_header()
        self.assertTrue(self.client.add_request_id)

        self.client.disable_request_id_header()
        self.assertFalse(self.client.add_request_id)

    @responses.activate
    def test_terminate_upload(self):
        url = 'http://tusd.tusdemo.net/files/15acd89eabdf5738ffc'
        events = []

        def before_request(context):
            events.append(('before', context.method, context.url))
            context.headers['x-hook'] = 'before'

        def after_response(context, response):
            events.append(('after', context.method, response.status_code))

        self.client.set_request_hooks(
            RequestLifecycleHooks(
                before_request=before_request,
                after_response=after_response,
            )
        )
        responses.add(TERMINATE_UPLOAD_METHOD, url, status=204)

        response = self.client.terminate_upload(url)
        request = responses.calls[0].request

        self.assertEqual(response.status_code, 204)
        self.assertEqual(request.method, TERMINATE_UPLOAD_METHOD)
        for header_name, header_value in DEFAULT_REQUEST_HEADERS.items():
            self.assertEqual(request.headers[header_name], header_value)
        self.assertEqual(request.headers['x-hook'], 'before')
        self.assertEqual(
            events,
            [
                ('before', TERMINATE_UPLOAD_METHOD, url),
                ('after', TERMINATE_UPLOAD_METHOD, 204),
            ],
        )

    @responses.activate
    def test_terminate_upload_non_success_status(self):
        url = 'http://tusd.tusdemo.net/files/15acd89eabdf5738ffc'
        responses.add(TERMINATE_UPLOAD_METHOD, url, status=404, body='gone')

        with self.assertRaises(TusCommunicationError) as context:
            self.client.terminate_upload(url)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.response_content, b'gone')

    @responses.activate
    def test_abort_upload_terminates_and_removes_stored_url(self):
        upload_url = 'http://tusd.tusdemo.net/files/abort'
        storage = MemoryStorage()
        uploader = self.client.uploader(
            file_stream=BytesIO(b'hello'),
            fingerprinter=FixedFingerprint('abort-fingerprint'),
            store_url=True,
            url_storage=storage,
        )
        uploader.set_url(upload_url)
        responses.add(TERMINATE_UPLOAD_METHOD, upload_url, status=204)

        response = self.client.abort_upload(uploader, terminate_upload=True)

        self.assertEqual(response.status_code, 204)
        self.assertTrue(uploader.is_aborted())
        self.assertIsNone(storage.get_item('abort-fingerprint'))

    @responses.activate
    def test_create_upload_with_data(self):
        upload_url = 'http://tusd.tusdemo.net/files/creation-with-upload'
        events = []

        def before_request(context):
            events.append(('before', context.method, context.url))
            context.headers['x-hook'] = 'before'

        def after_response(context, response):
            events.append(('after', context.method, response.status_code))

        def validate_create_request(request):
            self.assertEqual(request.body, b'hello')
            self.assertEqual(request.headers[UPLOAD_LENGTH_HEADER_NAME], '5')
            self.assertEqual(
                request.headers[UPLOAD_BODY_CONTENT_TYPE_HEADER_NAME],
                UPLOAD_BODY_CONTENT_TYPE,
            )
            self.assertEqual(request.headers['x-hook'], 'before')
            for header_name, header_value in DEFAULT_REQUEST_HEADERS.items():
                self.assertEqual(request.headers[header_name], header_value)

            return (
                201,
                {
                    LOCATION_HEADER_NAME: upload_url,
                    UPLOAD_OFFSET_HEADER_NAME: '5',
                },
                '',
            )

        self.client.set_request_hooks(
            RequestLifecycleHooks(
                before_request=before_request,
                after_response=after_response,
            )
        )
        responses.add_callback(
            CREATE_UPLOAD_METHOD,
            self.client.url,
            callback=validate_create_request,
        )

        uploader = self.client.create_upload_with_data(
            5,
            file_stream=BytesIO(b'hello'),
            chunk_size=5,
            metadata={},
        )

        self.assertIsInstance(uploader, Uploader)
        self.assertEqual(uploader.url, upload_url)
        self.assertEqual(uploader.offset, 5)
        self.assertEqual(
            events,
            [
                ('before', CREATE_UPLOAD_METHOD, self.client.url),
                ('after', CREATE_UPLOAD_METHOD, 201),
            ],
        )

    @responses.activate
    def test_create_upload_with_data_uses_selected_protocol_headers(self):
        upload_url = 'http://tusd.tusdemo.net/files/ietf-draft-05'
        protocol = 'ietf-draft-05'
        protocol_request_headers = TUS_PROTOCOL_REQUEST_HEADERS[protocol]
        body_headers = upload_body_headers(protocol, done=True)

        def validate_create_request(request):
            self.assertEqual(request.body, b'hello')
            self.assertNotIn('Tus-Resumable', request.headers)
            for header_name, header_value in protocol_request_headers.items():
                self.assertEqual(request.headers[header_name], header_value)
            for header_name, header_value in body_headers.items():
                self.assertEqual(request.headers[header_name], header_value)

            return (
                201,
                {
                    LOCATION_HEADER_NAME: upload_url,
                    UPLOAD_OFFSET_HEADER_NAME: '5',
                },
                '',
            )

        responses.add_callback(
            CREATE_UPLOAD_METHOD,
            self.client.url,
            callback=validate_create_request,
        )

        uploader = self.client.create_upload_with_data(
            5,
            file_stream=BytesIO(b'hello'),
            chunk_size=5,
            metadata={},
            protocol=protocol,
        )

        self.assertEqual(uploader.url, upload_url)
        self.assertEqual(uploader.offset, 5)

    @responses.activate
    def test_create_upload_with_data_non_success_status(self):
        responses.add(CREATE_UPLOAD_METHOD, self.client.url, status=400, body='bad')

        with self.assertRaises(TusCommunicationError) as context:
            self.client.create_upload_with_data(
                5,
                file_stream=BytesIO(b'hello'),
                chunk_size=5,
                metadata={},
            )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.response_content, b'bad')

    @responses.activate
    def test_uploader(self):
        url = 'http://tusd.tusdemo.net/files/15acd89eabdf5738ffc'
        responses.add(responses.HEAD, url,
                      adding_headers={"upload-offset": "0"})

        uploader = self.client.uploader('./LICENSE', url=url)

        self.assertIsInstance(uploader, Uploader)
        self.assertEqual(uploader.client, self.client)

    @responses.activate
    def test_async_uploader(self):
        url = 'http://tusd.tusdemo.net/files/15acd89eabdf5738ffc'
        responses.add(responses.HEAD, url,
                      adding_headers={"upload-offset": "0"})

        async_uploader = self.client.async_uploader('./LICENSE', url=url)

        self.assertIsInstance(async_uploader, AsyncUploader)
        self.assertEqual(async_uploader.client, self.client)
