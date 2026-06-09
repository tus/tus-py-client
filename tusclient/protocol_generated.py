# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

CREATE_UPLOAD_METHOD = 'POST'
DEFAULT_PROTOCOL_VERSION = '1.0.0'
DEFAULT_REQUEST_HEADERS = {
    'Tus-Resumable': '1.0.0',
}
DEFAULT_RESPONSE_HEADERS = {
    'Tus-Resumable': '1.0.0',
}
DETAILED_ERROR_CAUSE_STRING_TEMPLATE = 'Error: {message}'
DETAILED_ERROR_CAUSED_BY_TEMPLATE = ', caused by {cause}'
DETAILED_ERROR_CREATE_UPLOAD_REQUEST_FAILED = 'tus: failed to create upload'
DETAILED_ERROR_EMPTY_RESPONSE_BODY = ''
DETAILED_ERROR_MISSING_VALUE = 'n/a'
DETAILED_ERROR_REQUEST_CONTEXT_TEMPLATE = ', originated from request (method: {method}, url: {url}, response code: {status}, response text: {body}, request id: {requestId})'
DETAILED_ERROR_UNEXPECTED_CREATE_RESPONSE = 'tus: unexpected response while creating upload'
LOCATION_HEADER_NAME = 'Location'
METADATA_HEADER_NAME = 'Upload-Metadata'
OFFSET_DISCOVERY_METHOD = 'HEAD'
REQUEST_ID_HEADER_NAME = 'X-Request-ID'
START_VALIDATION_CLIENT_FLOW_VALUES = {
    'minimumParallelUploads': 2,
}
START_VALIDATION_MESSAGES = {
    'configuredUploadSizeMismatch': 'upload was configured with a size of {expectedSize} bytes, but the source is done after {actualSize} bytes',
    'cannotDeriveUploadSize': 'tus: cannot automatically derive upload\'s size from input. Specify it manually using the `uploadSize` option or use the `uploadLengthDeferred` option',
    'createMissingEndpoint': 'tus: unable to create upload because no endpoint is provided',
    'createMissingSize': 'tus: expected _size to be set',
    'createUploadRequestFailed': 'tus: failed to create upload',
    'createdUpload': 'Created upload at {uploadUrl}',
    'finalUploadMissingPartialUrls': 'tus: Expected _parallelUploadUrls to be set',
    'finalUploadRequestFailed': 'tus: failed to concatenate parallel uploads',
    'fingerprintCalculated': 'Calculated fingerprint: {fingerprint}',
    'fingerprintUnavailable': 'tus: unable to calculate fingerprint for this input file',
    'fingerprintUnavailableForStorage': 'No fingerprint was calculated meaning that the upload cannot be stored in the URL storage.',
    'invalidUploadSize': 'tus: cannot convert `uploadSize` option into a number',
    'invalidChunkOffset': 'tus: invalid or missing offset value',
    'invalidResumeLength': 'tus: invalid or missing length value',
    'invalidResumeOffset': 'tus: invalid Upload-Offset header',
    'lockedUpload': 'tus: upload is currently locked; retry later',
    'nonErrorThrownValue': 'tus: value thrown that is not an error: {value}',
    'missingEndpointOrUploadUrl': 'tus: neither an endpoint or an upload URL is provided',
    'missingInput': 'tus: no file or stream to upload provided',
    'missingPatchUrl': 'tus: Expected url to be set',
    'missingResumeOffset': 'tus: missing Upload-Offset header',
    'removedResumeOption': 'tus: The `resume` option has been removed in tus-js-client v2. Please use the URL storage API instead.',
    'parallelBoundariesLengthMismatch': 'tus: the `parallelUploadBoundaries` must have the same length as the value of `parallelUploads`',
    'parallelBoundariesWithoutParallelUploads': 'tus: cannot use the `parallelUploadBoundaries` option when `parallelUploads` is disabled',
    'parallelUploadMissingSize': 'tus: Expected _size to be set',
    'parallelUploadsWithDeferredLength': 'tus: cannot use the `uploadLengthDeferred` option when parallelUploads is enabled',
    'parallelUploadsWithUploadDataDuringCreation': 'tus: cannot use the `uploadDataDuringCreation` option when parallelUploads is enabled',
    'parallelUploadsWithUploadSize': 'tus: cannot use the `uploadSize` option when parallelUploads is enabled',
    'parallelUploadsWithUploadUrl': 'tus: cannot use the `uploadUrl` option when parallelUploads is enabled',
    'parallelUploadSliceMissingValue': 'tus: no value returned while slicing file for parallel uploads',
    'reactNativeUriBlobFetchFailed': 'tus: cannot fetch `file.uri` as Blob, make sure the uri is correct and accessible. {error}',
    'reactNativeUriUnsupported': 'tus: file objects with `uri` property is only supported in React Native',
    'resumeUploadRequestFailed': 'tus: failed to resume upload',
    'resumeWithoutEndpoint': 'tus: unable to resume upload (new upload cannot be created without an endpoint)',
    'retryDelaysNotArray': 'tus: the `retryDelays` option must either be an array or null',
    'storageMissingParallelUploadUrls': 'tus: cannot store parallel upload because no partial upload URLs are available',
    'storageMissingUploadUrl': 'tus: cannot store upload because no upload URL is available',
    'terminateUploadRequestFailed': 'tus: failed to terminate upload',
    'unexpectedChunkResponse': 'tus: unexpected response while uploading chunk',
    'unexpectedCreateResponse': 'tus: unexpected response while creating upload',
    'unexpectedResumeResponse': 'tus: unexpected response while resuming upload',
    'unexpectedTerminateResponse': 'tus: unexpected response while terminating upload',
    'uploadChunkRequestFailed': 'tus: failed to upload chunk at offset {offset}',
    'uploadLocationMissing': 'tus: invalid or missing Location header',
    'unsupportedProtocolPrefix': 'tus: unsupported protocol ',
}
START_VALIDATION_RULES = [
    {
        'message': {
            'key': 'missingInput',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'equals': False,
            'input': 'hasFile',
            'kind': 'boolean-input',
        },
        'reason': 'missingInput',
        'expectedError': 'tus: no file or stream to upload provided',
        'scenarioId': 'startValidationMissingInput',
    },
    {
        'message': {
            'input': 'protocol',
            'key': 'unsupportedProtocolPrefix',
            'kind': 'client-flow-message-with-input-suffix',
        },
        'predicate': {
            'equals': False,
            'input': 'protocol',
            'kind': 'supported-protocol',
        },
        'reason': 'unsupportedProtocol',
        'expectedError': 'tus: unsupported protocol tus-v9',
        'scenarioId': 'startValidationUnsupportedProtocol',
    },
    {
        'message': {
            'key': 'missingEndpointOrUploadUrl',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'kind': 'all',
            'predicates': [
                {
                    'equals': False,
                    'input': 'hasEndpoint',
                    'kind': 'boolean-input',
                },
                {
                    'equals': False,
                    'input': 'hasUploadUrl',
                    'kind': 'boolean-input',
                },
                {
                    'equals': False,
                    'input': 'hasCurrentUrl',
                    'kind': 'boolean-input',
                },
            ],
        },
        'reason': 'missingEndpointOrUploadUrl',
        'expectedError': 'tus: neither an endpoint or an upload URL is provided',
        'scenarioId': 'startValidationMissingEndpointOrUploadUrl',
    },
    {
        'message': {
            'key': 'retryDelaysNotArray',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'equals': False,
            'input': 'retryDelays',
            'kind': 'array-or-null',
        },
        'reason': 'retryDelaysNotArray',
        'expectedError': 'tus: the `retryDelays` option must either be an array or null',
        'scenarioId': 'startValidationRetryDelaysNotArray',
    },
    {
        'message': {
            'key': 'parallelUploadsWithUploadUrl',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'kind': 'all',
            'predicates': [
                {
                    'input': 'parallelUploads',
                    'kind': 'number-input-gte-client-flow-value',
                    'value': 'minimumParallelUploads',
                },
                {
                    'equals': True,
                    'input': 'hasUploadUrl',
                    'kind': 'boolean-input',
                },
            ],
        },
        'reason': 'parallelUploadsWithUploadUrl',
        'expectedError': 'tus: cannot use the `uploadUrl` option when parallelUploads is enabled',
        'scenarioId': 'startValidationParallelUploadsWithUploadUrl',
    },
    {
        'message': {
            'key': 'parallelUploadsWithUploadSize',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'kind': 'all',
            'predicates': [
                {
                    'input': 'parallelUploads',
                    'kind': 'number-input-gte-client-flow-value',
                    'value': 'minimumParallelUploads',
                },
                {
                    'equals': True,
                    'input': 'hasUploadSize',
                    'kind': 'boolean-input',
                },
            ],
        },
        'reason': 'parallelUploadsWithUploadSize',
        'expectedError': 'tus: cannot use the `uploadSize` option when parallelUploads is enabled',
        'scenarioId': 'startValidationParallelUploadsWithUploadSize',
    },
    {
        'message': {
            'key': 'parallelUploadsWithDeferredLength',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'kind': 'all',
            'predicates': [
                {
                    'input': 'parallelUploads',
                    'kind': 'number-input-gte-client-flow-value',
                    'value': 'minimumParallelUploads',
                },
                {
                    'equals': True,
                    'input': 'uploadLengthDeferred',
                    'kind': 'boolean-input',
                },
            ],
        },
        'reason': 'parallelUploadsWithDeferredLength',
        'expectedError': 'tus: cannot use the `uploadLengthDeferred` option when parallelUploads is enabled',
        'scenarioId': 'startValidationParallelUploadsWithDeferredLength',
    },
    {
        'message': {
            'key': 'parallelUploadsWithUploadDataDuringCreation',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'kind': 'all',
            'predicates': [
                {
                    'input': 'parallelUploads',
                    'kind': 'number-input-gte-client-flow-value',
                    'value': 'minimumParallelUploads',
                },
                {
                    'equals': True,
                    'input': 'uploadDataDuringCreation',
                    'kind': 'boolean-input',
                },
            ],
        },
        'reason': 'parallelUploadsWithUploadDataDuringCreation',
        'expectedError': 'tus: cannot use the `uploadDataDuringCreation` option when parallelUploads is enabled',
        'scenarioId': 'startValidationParallelUploadsWithUploadDataDuringCreation',
    },
    {
        'message': {
            'key': 'parallelBoundariesWithoutParallelUploads',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'kind': 'all',
            'predicates': [
                {
                    'input': 'parallelUploadBoundariesCount',
                    'kind': 'number-input-not-null',
                },
                {
                    'input': 'parallelUploads',
                    'kind': 'number-input-lt-client-flow-value',
                    'value': 'minimumParallelUploads',
                },
            ],
        },
        'reason': 'parallelBoundariesWithoutParallelUploads',
        'expectedError': 'tus: cannot use the `parallelUploadBoundaries` option when `parallelUploads` is disabled',
        'scenarioId': 'startValidationParallelBoundariesWithoutParallelUploads',
    },
    {
        'message': {
            'key': 'parallelBoundariesLengthMismatch',
            'kind': 'client-flow-message',
        },
        'predicate': {
            'kind': 'all',
            'predicates': [
                {
                    'input': 'parallelUploadBoundariesCount',
                    'kind': 'number-input-not-null',
                },
                {
                    'kind': 'number-input-not-equals-number-input',
                    'left': 'parallelUploads',
                    'right': 'parallelUploadBoundariesCount',
                },
            ],
        },
        'reason': 'parallelBoundariesLengthMismatch',
        'expectedError': 'tus: the `parallelUploadBoundaries` must have the same length as the value of `parallelUploads`',
        'scenarioId': 'startValidationParallelBoundariesLengthMismatch',
    },
]
SUCCESS_RESPONSE_STATUS_CATEGORY = 200
TERMINATE_UPLOAD_METHOD = 'DELETE'
TUS_SUPPORTED_PROTOCOLS = [
    'tus-v1',
    'ietf-draft-03',
    'ietf-draft-05',
]
UPLOAD_BODY_CONTENT_TYPE = 'application/offset+octet-stream'
UPLOAD_BODY_CONTENT_TYPE_HEADER_NAME = 'Content-Type'
UPLOAD_CHUNK_METHOD = 'PATCH'
UPLOAD_DEFER_LENGTH_HEADER_NAME = 'Upload-Defer-Length'
UPLOAD_LENGTH_HEADER_NAME = 'Upload-Length'
UPLOAD_OFFSET_HEADER_NAME = 'Upload-Offset'


def is_successful_response_status(response_status_code):
    return (
        response_status_code >= SUCCESS_RESPONSE_STATUS_CATEGORY
        and response_status_code < SUCCESS_RESPONSE_STATUS_CATEGORY + 100
    )


def prepare_request_headers(operation_headers=None, custom_headers=None, add_request_id=False):
    headers = {}
    add_operation_request_headers(headers, operation_headers)
    add_custom_request_headers(headers, custom_headers)
    add_request_id_header(headers, add_request_id)
    return headers


def add_operation_request_headers(headers, operation_headers):
    headers.update(DEFAULT_REQUEST_HEADERS)
    if operation_headers:
        headers.update(operation_headers)


def add_custom_request_headers(headers, custom_headers):
    if custom_headers:
        headers.update(custom_headers)


def add_request_id_header(headers, add_request_id):
    if not add_request_id:
        return
    headers[REQUEST_ID_HEADER_NAME] = generated_request_id()


def generated_request_id():
    import uuid

    return str(uuid.uuid4())
