# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

import io
import unittest

import responses

from tusclient.client import TusClient


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
        'requests': [
            {
                'method': 'POST',
                'responseHeaders': {
                    'Location': 'https://tus.io/uploads/generated-contract',
                },
                'statusCode': 201,
                'url': 'endpoint',
            },
            {
                'method': 'PATCH',
                'responseHeaders': {
                    'Upload-Offset': '11',
                },
                'statusCode': 204,
                'url': 'upload',
            },
        ],
        'scenarioId': 'singleUploadLifecycle',
        'uploadUrl': 'https://tus.io/uploads/generated-contract',
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
        'requests': [
            {
                'method': 'POST',
                'responseHeaders': {
                    'Location': 'relative-contract',
                },
                'statusCode': 201,
                'url': 'endpoint',
            },
            {
                'method': 'PATCH',
                'responseHeaders': {
                    'Upload-Offset': '11',
                },
                'statusCode': 204,
                'url': 'upload',
            },
        ],
        'scenarioId': 'relativeLocationResolution',
        'uploadUrl': 'https://tus.io/files/relative-contract',
    },
]


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
                on_progress=record_progress(events),
                on_chunk_complete=record_chunk_complete(events),
            )
            uploader.upload()

            self.assertEqual(events, case['eventKeys'], case['scenarioId'])
