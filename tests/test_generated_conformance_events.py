# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

import unittest

from tests.generated_protocol_contract import (
    TUS_CLIENT_CONFORMANCE_SCENARIOS,
    TUS_CLIENT_FEATURES,
    TUS_MANAGED_UPLOAD,
    TUS_MANAGED_UPLOAD_PROOF_CASES,
)


CASES = [
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
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
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'singleUploadLifecycle',
        'scenarioId': 'singleUploadLifecycle',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
        'eventKeys': [
            'progress:0:11',
            'progress:11:11',
            'upload-url-available',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'creationWithUpload',
        'scenarioId': 'creationWithUpload',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
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
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'creationWithUpload',
        'scenarioId': 'creationWithUploadPartialChunk',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
        'eventKeys': [
            'progress:0:11',
            'progress:11:11',
            'upload-url-available',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'protocolVersionSelection',
        'scenarioId': 'ietfDraft05CreationWithUpload',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
        'eventKeys': [
            'upload-url-available',
            'progress:0:11',
            'progress:5:11',
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
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'protocolVersionSelection',
        'scenarioId': 'ietfDraft05ChunkedUploadComplete',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
        'eventKeys': [
            'upload-url-available',
            'progress:5:11',
            'progress:11:11',
            'chunk-complete:6:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'protocolVersionSelection',
        'scenarioId': 'ietfDraft03ResumeWithoutKnownLength',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
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
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'resumeUpload',
        'scenarioId': 'resumeFromPreviousUpload',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
        'eventKeys': [
            'upload-url-available',
            'progress:0:11',
            'progress:11:11',
            'chunk-complete:11:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'relativeLocationResolution',
        'scenarioId': 'relativeLocationResolution',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
        'eventKeys': [
            'upload-url-available',
            'progress:0:11',
            'progress:11:11',
            'chunk-complete:11:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'deferredLengthBytesTotal': 'allow-known-total-before-declaration',
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'deferredLengthUpload',
        'scenarioId': 'deferredLengthUpload',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [
                'progress:0:11',
            ],
            [
                'progress:5:11',
            ],
            [
                'chunk-complete:5:5:11',
            ],
            [
                'progress:5:11',
            ],
            [
                'progress:10:11',
            ],
            [
                'chunk-complete:5:10:11',
            ],
            [],
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
        'eventKeys': [
            'upload-url-available',
            'progress:0:null',
            'progress:5:null',
            'chunk-complete:5:5:null',
            'progress:5:null',
            'progress:10:null',
            'chunk-complete:5:10:null',
            'progress:10:11',
            'progress:11:11',
            'chunk-complete:1:11:11',
            'success',
            'source-close',
        ],
        'eventPolicy': {
            'deferredLengthBytesTotal': 'allow-known-total-before-declaration',
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'deferredLengthUpload',
        'scenarioId': 'deferredLengthChunkedUpload',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [
            'progress:',
        ],
        'eventKeys': [
            'progress:5:11',
            'chunk-complete:5:5:11',
            'progress:11:11',
            'chunk-complete:6:11:11',
        ],
        'eventPolicy': {
            'matching': 'exact-except-allowed-extra-events',
            'progress': 'milestone',
            'transportProgress': 'may-emit-extra-samples',
        },
        'featureId': 'parallelUploadConcat',
        'scenarioId': 'parallelUploadConcat',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
            [],
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
        ],
        'eventKeyExtraPrefixes': [],
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
        'eventKeyAlternativeGroups': [
            [],
        ],
        'eventKeyExtraPrefixes': [],
        'eventKeys': [
            'request-abort:1',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'abortUpload',
        'scenarioId': 'abortUploadAfterStoredUrl',
    },
    {
        'eventKeyAlternativeGroups': [
            [],
            [],
        ],
        'eventKeyExtraPrefixes': [],
        'eventKeys': [
            'should-retry:0:true',
            'retry-schedule:0',
        ],
        'eventPolicy': {
            'matching': 'exact',
        },
        'featureId': 'terminateUpload',
        'scenarioId': 'terminateWithRetry',
    },
]

PROOF_CASES = [
    {
        'behavior': 'single-upload-lifecycle',
        'completionKind': 'success',
        'featureId': 'singleUploadLifecycle',
        'operationIds': [
            'createTusUpload',
            'patchTusUpload',
        ],
        'primitives': [
            'open-input-source',
            'fingerprint-input',
            'store-resume-url',
            'retry-with-backoff',
            'emit-progress',
            'abort-current-request',
        ],
        'profile': 'urlStorageCreateFlow',
        'scenarioId': 'singleUploadLifecycle',
    },
    {
        'behavior': 'custom-request-headers',
        'completionKind': 'success',
        'featureId': 'customRequestHeaders',
        'operationIds': [
            'createTusUpload',
            'patchTusUpload',
        ],
        'primitives': [
            'apply-custom-request-headers',
        ],
        'profile': 'customRequestHeaders',
        'scenarioId': 'customRequestHeaders',
    },
    {
        'behavior': 'override-patch-method',
        'completionKind': 'success',
        'featureId': 'overridePatchMethod',
        'operationIds': [
            'getTusUploadOffset',
            'patchTusUpload',
        ],
        'primitives': [
            'override-patch-method',
        ],
        'profile': 'overridePatchMethod',
        'scenarioId': 'overridePatchMethod',
    },
    {
        'behavior': 'node-path-input',
        'completionKind': 'success',
        'featureId': 'inputSources',
        'operationIds': [
            'createTusUpload',
            'patchTusUpload',
        ],
        'primitives': [
            'read-node-file',
        ],
        'profile': 'nodePathFileUpload',
        'scenarioId': 'nodePathInput',
    },
    {
        'behavior': 'resume-from-previous-upload',
        'completionKind': 'success',
        'featureId': 'resumeUpload',
        'operationIds': [
            'getTusUploadOffset',
            'patchTusUpload',
        ],
        'primitives': [
            'fingerprint-input',
            'resume-from-previous-upload',
            'store-resume-url',
        ],
        'profile': 'resumeFromPreviousUpload',
        'scenarioId': 'resumeFromPreviousUpload',
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


def managed_upload_scenario(scenario_id):
    for scenario in TUS_MANAGED_UPLOAD["scenarios"]:
        if scenario["scenarioId"] == scenario_id:
            return scenario
    raise AssertionError("Missing generated TUS managed-upload scenario: {}".format(scenario_id))


class GeneratedTusConformanceEventsTest(unittest.TestCase):
    def test_generated_scenario_event_keys(self):
        for case in CASES:
            scenario = client_scenario(case["scenarioId"])
            feature = client_feature(case["featureId"])

            self.assertEqual(scenario["featureId"], case["featureId"])
            self.assertIn(scenario["scenarioId"], feature["conformance"]["scenarioIds"])
            self.assertEqual(
                scenario["eventKeys"],
                case["eventKeys"],
            )
            self.assertEqual(
                scenario["eventKeyAlternativeGroups"],
                case["eventKeyAlternativeGroups"],
            )
            self.assertEqual(
                scenario["eventKeyExtraPrefixes"],
                case["eventKeyExtraPrefixes"],
            )
            self.assertEqual(
                scenario["eventPolicy"],
                case["eventPolicy"],
            )

    def test_generated_proof_profile_scenarios(self):
        for case in PROOF_CASES:
            scenario = client_scenario(case["scenarioId"])
            feature = client_feature(case["featureId"])

            self.assertEqual(scenario["behavior"], case["behavior"])
            self.assertEqual(scenario["completion"]["kind"], case["completionKind"])
            self.assertEqual(scenario["featureId"], case["featureId"])
            self.assertIn(scenario["scenarioId"], feature["conformance"]["scenarioIds"])
            self.assertEqual(scenario["operationIds"], case["operationIds"])
            self.assertEqual(scenario["primitives"], case["primitives"])

    def test_generated_managed_upload_proof_scenarios(self):
        for case in TUS_MANAGED_UPLOAD_PROOF_CASES:
            scenario = managed_upload_scenario(case["scenarioId"])

            self.assertEqual(TUS_MANAGED_UPLOAD["featureId"], case["featureId"])
            self.assertEqual(TUS_MANAGED_UPLOAD["layer"], case["layer"])
            self.assertEqual(scenario["requiredPrimitives"], case["requiredPrimitives"])
            for primitive in case["requiredPrimitives"]:
                self.assertIn(primitive, TUS_MANAGED_UPLOAD["primitives"])
            for feature_id in case["protocolFeatureIds"]:
                client_feature(feature_id)
            self.assertEqual(
                [profile["runtime"] for profile in TUS_MANAGED_UPLOAD["runtimeProfiles"]],
                case["runtimeProfiles"],
            )
