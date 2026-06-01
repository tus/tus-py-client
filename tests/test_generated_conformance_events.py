# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

import unittest

from tests.generated_protocol_contract import (
    TUS_CLIENT_CONFORMANCE_SCENARIOS,
    TUS_CLIENT_FEATURES,
)


CASES = [
    {
        'eventKeys': [
            'fingerprint:contract-single-fingerprint',
            'upload-url-available',
            'url-storage-add:contract-single-fingerprint:https://tus.io/uploads/generated-contract',
            'progress:0:11',
            'progress:11:11',
            'chunk-complete:11:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'singleUploadLifecycle',
        'scenarioId': 'singleUploadLifecycle',
    },
    {
        'eventKeys': [
            'progress:0:11',
            'progress:11:11',
            'upload-url-available',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'creationWithUpload',
        'scenarioId': 'creationWithUpload',
    },
    {
        'eventKeys': [
            'progress:0:11',
            'progress:5:11',
            'upload-url-available',
            'chunk-complete:5:5:11',
            'progress:5:11',
            'progress:10:11',
            'chunk-complete:5:10:11',
            'progress:10:11',
            'progress:11:11',
            'chunk-complete:1:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'creationWithUpload',
        'scenarioId': 'creationWithUploadPartialChunk',
    },
    {
        'eventKeys': [
            'progress:0:11',
            'progress:11:11',
            'upload-url-available',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'protocolVersionSelection',
        'scenarioId': 'ietfDraft05CreationWithUpload',
    },
    {
        'eventKeys': [
            'upload-url-available',
            'progress:5:11',
            'progress:11:11',
            'chunk-complete:6:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'protocolVersionSelection',
        'scenarioId': 'ietfDraft03ResumeWithoutKnownLength',
    },
    {
        'eventKeys': [
            'fingerprint:contract-resume-fingerprint',
            'url-storage-find:contract-resume-fingerprint:1',
            'fingerprint:contract-resume-fingerprint',
            'upload-url-available',
            'progress:5:11',
            'progress:11:11',
            'chunk-complete:6:11:11',
            'url-storage-remove:tus::contract-resume-fingerprint::1337',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'resumeUpload',
        'scenarioId': 'resumeFromPreviousUpload',
    },
    {
        'eventKeys': [
            'upload-url-available',
            'progress:0:11',
            'progress:11:11',
            'chunk-complete:11:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'relativeLocationResolution',
        'scenarioId': 'relativeLocationResolution',
    },
    {
        'eventKeys': [
            'source-open:array-buffer:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'inputSources',
        'scenarioId': 'arrayBufferInput',
    },
    {
        'eventKeys': [
            'source-open:array-buffer-view:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'inputSources',
        'scenarioId': 'arrayBufferViewInput',
    },
    {
        'eventKeys': [
            'source-open:web-readable-stream:null',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'inputSources',
        'scenarioId': 'webReadableStreamInput',
    },
    {
        'eventKeys': [
            'source-open:node-readable-stream:null',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'inputSources',
        'scenarioId': 'nodeReadableStreamInput',
    },
    {
        'eventKeys': [
            'source-open:node-path-reference:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'inputSources',
        'scenarioId': 'nodePathInput',
    },
    {
        'eventKeys': [
            'upload-url-available',
            'progress:0:11',
            'progress:11:11',
            'chunk-complete:11:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'deferredLengthUpload',
        'scenarioId': 'deferredLengthUpload',
    },
    {
        'eventKeys': [
            'progress:5:11',
            'chunk-complete:5:5:11',
            'progress:11:11',
            'chunk-complete:6:11:11',
        ],
        'eventPolicy': {
            'matching': 'exact-except-extra-progress',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'parallelUploadConcat',
        'scenarioId': 'parallelUploadConcat',
    },
    {
        'eventKeys': [
            'request-abort:3',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'parallelUploadConcat',
        'scenarioId': 'parallelUploadAbortCleanup',
    },
    {
        'eventKeys': [
            'should-retry:0:true',
            'retry-schedule:0',
            'should-retry:0:true',
            'retry-schedule:0',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'retryOffsetRecovery',
        'scenarioId': 'retryPatchAfterOffsetRecovery',
    },
    {
        'eventKeys': [
            'before-request:0',
            'after-response:0',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'requestLifecycleHooks',
        'scenarioId': 'requestLifecycleHooks',
    },
    {
        'eventKeys': [
            'request-abort:0',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'abortUpload',
        'scenarioId': 'abortUpload',
    },
    {
        'eventKeys': [
            'request-abort:1',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'abortUpload',
        'scenarioId': 'abortUploadAfterStoredUrl',
    },
]


def client_feature(feature_id):
    for feature in TUS_CLIENT_FEATURES:
        if feature["featureId"] == feature_id:
            return feature
    raise AssertionError("Missing generated TUS client feature: {}".format(feature_id))


def client_scenario(scenario_id):
    for scenario in TUS_CLIENT_CONFORMANCE_SCENARIOS:
        if scenario["scenarioId"] == scenario_id:
            return scenario
    raise AssertionError("Missing generated TUS client scenario: {}".format(scenario_id))


class GeneratedTusConformanceEventsTest(unittest.TestCase):
    def test_generated_scenario_event_keys(self):
        for case in CASES:
            scenario = client_scenario(case["scenarioId"])
            feature = client_feature(case["featureId"])

            self.assertEqual(scenario["featureId"], case["featureId"])
            self.assertIn(scenario["scenarioId"], feature["conformance"]["scenarioIds"])
            self.assertEqual(
                [event["key"] for event in scenario["events"]],
                case["eventKeys"],
            )
            self.assertEqual(
                scenario.get("eventPolicy", {"matching": "exact"}),
                case["eventPolicy"],
            )
