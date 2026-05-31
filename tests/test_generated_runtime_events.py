# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

import io
import unittest

import responses

from tusclient.client import TusClient
from tusclient.fingerprint.interface import Fingerprint
from tusclient.storage.interface import Storage


CASES = [
    {
        'chunkSize': 11,
        'content': 'hello world',
        'endpointUrl': 'https://tus.io/uploads',
        'eventKeys': [
            'progress:0:11',
            'progress:11:11',
            'chunk-complete:11:11:11',
        ],
        'metadata': {
            'filename': 'hello.txt',
        },
        'removeFingerprintOnSuccess': False,
        'requests': [
            {
                'headers': {
                    'Upload-Length': '11',
                },
                'method': 'POST',
                'responseHeaders': {
                    'Location': 'https://tus.io/uploads/generated-contract',
                },
                'statusCode': 201,
                'url': 'endpoint',
            },
            {
                'headers': {
                    'Upload-Offset': '0',
                },
                'method': 'PATCH',
                'responseHeaders': {
                    'Upload-Offset': '11',
                },
                'statusCode': 204,
                'url': 'upload',
            },
        ],
        'scenarioId': 'singleUploadLifecycle',
        'storedUpload': None,
        'uploadLengthDeferred': False,
        'uploadUrl': 'https://tus.io/uploads/generated-contract',
    },
    {
        'chunkSize': 6,
        'content': 'hello world',
        'endpointUrl': 'https://tus.io/uploads',
        'eventKeys': [
            'progress:5:11',
            'progress:11:11',
            'chunk-complete:6:11:11',
        ],
        'metadata': {},
        'removeFingerprintOnSuccess': True,
        'requests': [
            {
                'headers': {},
                'method': 'HEAD',
                'responseHeaders': {
                    'Upload-Length': '11',
                    'Upload-Offset': '5',
                },
                'statusCode': 200,
                'url': 'upload',
            },
            {
                'headers': {
                    'Upload-Offset': '5',
                },
                'method': 'PATCH',
                'responseHeaders': {
                    'Upload-Offset': '11',
                },
                'statusCode': 204,
                'url': 'upload',
            },
        ],
        'scenarioId': 'resumeFromPreviousUpload',
        'storedUpload': {
            'fingerprint': 'contract-resume-fingerprint',
            'uploadUrl': 'https://tus.io/uploads/resume-contract',
            'urlStorageKey': 'tus::contract-resume-fingerprint::1337',
        },
        'uploadLengthDeferred': False,
        'uploadUrl': 'https://tus.io/uploads/resume-contract',
    },
    {
        'chunkSize': 11,
        'content': 'hello world',
        'endpointUrl': 'https://tus.io/files/',
        'eventKeys': [
            'progress:0:11',
            'progress:11:11',
            'chunk-complete:11:11:11',
        ],
        'metadata': {
            'filename': 'hello.txt',
        },
        'removeFingerprintOnSuccess': False,
        'requests': [
            {
                'headers': {
                    'Upload-Length': '11',
                },
                'method': 'POST',
                'responseHeaders': {
                    'Location': 'relative-contract',
                },
                'statusCode': 201,
                'url': 'endpoint',
            },
            {
                'headers': {
                    'Upload-Offset': '0',
                },
                'method': 'PATCH',
                'responseHeaders': {
                    'Upload-Offset': '11',
                },
                'statusCode': 204,
                'url': 'upload',
            },
        ],
        'scenarioId': 'relativeLocationResolution',
        'storedUpload': None,
        'uploadLengthDeferred': False,
        'uploadUrl': 'https://tus.io/files/relative-contract',
    },
    {
        'chunkSize': 100,
        'content': 'hello world',
        'endpointUrl': 'https://tus.io/uploads',
        'eventKeys': [
            'progress:0:11',
            'progress:11:11',
            'chunk-complete:11:11:11',
        ],
        'metadata': {
            'filename': 'hello.txt',
        },
        'removeFingerprintOnSuccess': False,
        'requests': [
            {
                'headers': {
                    'Upload-Defer-Length': '1',
                },
                'method': 'POST',
                'responseHeaders': {
                    'Location': 'https://tus.io/uploads/deferred-contract',
                },
                'statusCode': 201,
                'url': 'endpoint',
            },
            {
                'headers': {
                    'Upload-Length': '11',
                    'Upload-Offset': '0',
                },
                'method': 'PATCH',
                'responseHeaders': {
                    'Upload-Offset': '11',
                },
                'statusCode': 204,
                'url': 'upload',
            },
        ],
        'scenarioId': 'deferredLengthUpload',
        'storedUpload': None,
        'uploadLengthDeferred': True,
        'uploadUrl': 'https://tus.io/uploads/deferred-contract',
    },
]


class GeneratedTusStorage(Storage):
    def __init__(self, values):
        self.values = dict(values)

    def get_item(self, key):
        return self.values.get(key)

    def set_item(self, key, value):
        self.values[key] = value

    def remove_item(self, key):
        self.values.pop(key, None)


class GeneratedTusFingerprinter(Fingerprint):
    def __init__(self, fingerprint):
        self.fingerprint = fingerprint

    def get_fingerprint(self, fs):
        return self.fingerprint


def format_event_value(value):
    return 'null' if value is None else str(value)


def record_progress(events):
    def on_progress(bytes_sent, bytes_total):
        events.append(
            'progress:{}:{}'.format(bytes_sent, format_event_value(bytes_total))
        )
    return on_progress


def record_chunk_complete(events):
    def on_chunk_complete(chunk_size, bytes_accepted, bytes_total):
        events.append(
            'chunk-complete:{}:{}:{}'.format(
                chunk_size,
                bytes_accepted,
                format_event_value(bytes_total),
            )
        )
    return on_chunk_complete


class GeneratedTusRuntimeEventsTest(unittest.TestCase):
    @responses.activate
    def test_sync_uploader_emits_generated_progress_and_chunk_events(self):
        for case in CASES:
            events = []
            client = TusClient(case['endpointUrl'])
            storage = storage_for(case)
            first_call_index = len(responses.calls)

            for request in case['requests']:
                url = case['endpointUrl'] if request['url'] == 'endpoint' else case['uploadUrl']
                responses.add(
                    request['method'],
                    url,
                    adding_headers=request['responseHeaders'],
                    status=request['statusCode'],
                )

            uploader = client.uploader(
                file_stream=io.BytesIO(case['content'].encode('utf-8')),
                chunk_size=case['chunkSize'],
                metadata=case['metadata'],
                store_url=case['storedUpload'] is not None,
                url_storage=storage,
                fingerprinter=fingerprinter_for(case),
                remove_fingerprint_on_success=case['removeFingerprintOnSuccess'],
                upload_length_deferred=case['uploadLengthDeferred'],
                on_progress=record_progress(events),
                on_chunk_complete=record_chunk_complete(events),
            )
            uploader.upload()

            self.assertEqual(events, case['eventKeys'], case['scenarioId'])
            assert_request_sequence(self, case, responses.calls[first_call_index:])
            assert_stored_upload_state(self, case, storage)


def storage_for(case):
    if case['storedUpload'] is None:
        return None

    return GeneratedTusStorage({
        case['storedUpload']['fingerprint']: case['storedUpload']['uploadUrl'],
    })


def fingerprinter_for(case):
    if case['storedUpload'] is None:
        return None

    return GeneratedTusFingerprinter(case['storedUpload']['fingerprint'])


def request_header(request, name):
    return request.headers.get(name) or request.headers.get(name.lower())


def assert_request_sequence(test, case, calls):
    test.assertEqual(len(calls), len(case['requests']), case['scenarioId'])

    for index, expected_request in enumerate(case['requests']):
        actual_request = calls[index].request
        expected_url = (
            case['endpointUrl']
            if expected_request['url'] == 'endpoint'
            else case['uploadUrl']
        )

        test.assertEqual(actual_request.method, expected_request['method'], case['scenarioId'])
        test.assertEqual(actual_request.url, expected_url, case['scenarioId'])
        for name, value in expected_request['headers'].items():
            test.assertEqual(request_header(actual_request, name), value, case['scenarioId'])


def assert_stored_upload_state(test, case, storage):
    if case['storedUpload'] is None:
        return

    fingerprint = case['storedUpload']['fingerprint']
    if case['removeFingerprintOnSuccess']:
        test.assertIsNone(storage.get_item(fingerprint), case['scenarioId'])
    else:
        test.assertEqual(
            storage.get_item(fingerprint),
            case['storedUpload']['uploadUrl'],
            case['scenarioId'],
        )
