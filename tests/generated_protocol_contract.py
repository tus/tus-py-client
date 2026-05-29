# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

TUS_WIRE_VERSIONS = [
    {
        'default': True,
        'value': '1.0.0',
    },
]

TUS_PROTOCOL_OPERATIONS = [
    {
        'operationId': 'discoverTusCapabilities',
        'role': 'capability-discovery',
        'method': 'OPTIONS',
        'path': '/resumable/files/',
        'request': {
            'bodyKind': 'empty',
            'contentType': None,
            'headerVariants': [],
        },
        'responses': [
            {
                'statusCode': 200,
                'bodyKind': 'empty',
                'headerVariants': [
                    {
                        'fields': [
                            {
                                'displayName': 'Tus-Extension',
                                'name': 'tus-extension',
                                'required': True,
                            },
                            {
                                'displayName': 'Tus-Max-Size',
                                'name': 'tus-max-size',
                                'required': True,
                            },
                            {
                                'displayName': 'Tus-Resumable',
                                'name': 'tus-resumable',
                                'required': True,
                            },
                            {
                                'displayName': 'Tus-Version',
                                'name': 'tus-version',
                                'required': True,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        'operationId': 'createTusUpload',
        'role': 'creation',
        'method': 'POST',
        'path': '/resumable/files/',
        'request': {
            'bodyKind': 'empty',
            'contentType': None,
            'headerVariants': [
                {
                    'fields': [
                        {
                            'displayName': 'Tus-Resumable',
                            'name': 'tus-resumable',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Length',
                            'name': 'upload-length',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Metadata',
                            'name': 'upload-metadata',
                            'required': True,
                        },
                    ],
                },
                {
                    'fields': [
                        {
                            'displayName': 'Tus-Resumable',
                            'name': 'tus-resumable',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Defer-Length',
                            'name': 'upload-defer-length',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Metadata',
                            'name': 'upload-metadata',
                            'required': True,
                        },
                    ],
                },
                {
                    'fields': [
                        {
                            'displayName': 'Tus-Resumable',
                            'name': 'tus-resumable',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Concat',
                            'name': 'upload-concat',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Length',
                            'name': 'upload-length',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Metadata',
                            'name': 'upload-metadata',
                            'required': False,
                        },
                    ],
                },
                {
                    'fields': [
                        {
                            'displayName': 'Tus-Resumable',
                            'name': 'tus-resumable',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Concat',
                            'name': 'upload-concat',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Metadata',
                            'name': 'upload-metadata',
                            'required': False,
                        },
                    ],
                },
            ],
        },
        'responses': [
            {
                'statusCode': 201,
                'bodyKind': 'empty',
                'headerVariants': [
                    {
                        'fields': [
                            {
                                'displayName': 'Location',
                                'name': 'location',
                                'required': True,
                            },
                            {
                                'displayName': 'Tus-Resumable',
                                'name': 'tus-resumable',
                                'required': True,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        'operationId': 'getTusUploadOffset',
        'role': 'offset-discovery',
        'method': 'HEAD',
        'path': '/resumable/files/{upload_id}',
        'request': {
            'bodyKind': 'empty',
            'contentType': None,
            'headerVariants': [
                {
                    'fields': [
                        {
                            'displayName': 'Tus-Resumable',
                            'name': 'tus-resumable',
                            'required': True,
                        },
                    ],
                },
            ],
        },
        'responses': [
            {
                'statusCode': 200,
                'bodyKind': 'empty',
                'headerVariants': [
                    {
                        'fields': [
                            {
                                'displayName': 'Tus-Resumable',
                                'name': 'tus-resumable',
                                'required': True,
                            },
                            {
                                'displayName': 'Upload-Length',
                                'name': 'upload-length',
                                'required': True,
                            },
                            {
                                'displayName': 'Upload-Offset',
                                'name': 'upload-offset',
                                'required': True,
                            },
                        ],
                    },
                    {
                        'fields': [
                            {
                                'displayName': 'Tus-Resumable',
                                'name': 'tus-resumable',
                                'required': True,
                            },
                            {
                                'displayName': 'Upload-Defer-Length',
                                'name': 'upload-defer-length',
                                'required': True,
                            },
                            {
                                'displayName': 'Upload-Offset',
                                'name': 'upload-offset',
                                'required': True,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        'operationId': 'patchTusUpload',
        'role': 'upload-chunk',
        'method': 'PATCH',
        'path': '/resumable/files/{upload_id}',
        'request': {
            'bodyKind': 'binary',
            'contentType': 'application/offset+octet-stream',
            'headerVariants': [
                {
                    'fields': [
                        {
                            'displayName': 'Content-Type',
                            'name': 'content-type',
                            'required': True,
                        },
                        {
                            'displayName': 'Tus-Resumable',
                            'name': 'tus-resumable',
                            'required': True,
                        },
                        {
                            'displayName': 'Upload-Offset',
                            'name': 'upload-offset',
                            'required': True,
                        },
                    ],
                },
            ],
        },
        'responses': [
            {
                'statusCode': 204,
                'bodyKind': 'empty',
                'headerVariants': [
                    {
                        'fields': [
                            {
                                'displayName': 'Tus-Resumable',
                                'name': 'tus-resumable',
                                'required': True,
                            },
                            {
                                'displayName': 'Upload-Offset',
                                'name': 'upload-offset',
                                'required': True,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        'operationId': 'terminateTusUpload',
        'role': 'termination',
        'method': 'DELETE',
        'path': '/resumable/files/{upload_id}',
        'request': {
            'bodyKind': 'empty',
            'contentType': None,
            'headerVariants': [
                {
                    'fields': [
                        {
                            'displayName': 'Tus-Resumable',
                            'name': 'tus-resumable',
                            'required': True,
                        },
                    ],
                },
            ],
        },
        'responses': [
            {
                'statusCode': 204,
                'bodyKind': 'empty',
                'headerVariants': [
                    {
                        'fields': [
                            {
                                'displayName': 'Tus-Resumable',
                                'name': 'tus-resumable',
                                'required': True,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        'operationId': 'downloadTusUpload',
        'role': 'download',
        'method': 'GET',
        'path': '/resumable/files/{upload_id}',
        'request': {
            'bodyKind': 'empty',
            'contentType': None,
            'headerVariants': [],
        },
        'responses': [
            {
                'statusCode': 200,
                'bodyKind': 'binary',
                'headerVariants': [],
            },
        ],
    },
]

TUS_CLIENT_FEATURES = [
    {
        'conformance': {
            'scenarioIds': [
                'singleUploadLifecycle',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Create an upload, store its URL, upload bytes, and finish successfully.',
        'featureId': 'singleUploadLifecycle',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'open-input-source',
                'summary': 'Open the caller input as a sliceable source.',
            },
            {
                'kind': 'operation',
                'operationId': 'createTusUpload',
                'summary': 'Create the remote upload resource.',
            },
            {
                'kind': 'operation',
                'operationId': 'patchTusUpload',
                'summary': 'Upload bytes until the accepted offset reaches the known length.',
            },
        ],
        'operationIds': [
            'createTusUpload',
            'getTusUploadOffset',
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
    },
    {
        'conformance': {
            'scenarioIds': [
                'resumeFromPreviousUpload',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Resume a stored upload URL by discovering the remote offset before patching.',
        'featureId': 'resumeUpload',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'resume-from-previous-upload',
                'summary': 'Load a stored upload URL selected by fingerprint.',
            },
            {
                'kind': 'operation',
                'operationId': 'getTusUploadOffset',
                'summary': 'Read the server offset for the stored upload URL.',
            },
            {
                'kind': 'operation',
                'operationId': 'patchTusUpload',
                'summary': 'Continue uploading from the discovered offset.',
            },
        ],
        'operationIds': [
            'getTusUploadOffset',
            'patchTusUpload',
        ],
        'primitives': [
            'fingerprint-input',
            'resume-from-previous-upload',
            'store-resume-url',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'deferredLengthUpload',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Create an upload without a known length and declare the length on final PATCH.',
        'featureId': 'deferredLengthUpload',
        'flow': [
            {
                'kind': 'operation',
                'operationId': 'createTusUpload',
                'summary': 'Create the upload with deferred length.',
            },
            {
                'kind': 'primitive',
                'primitive': 'defer-upload-length',
                'summary': 'Track the source until the final chunk reveals the total size.',
            },
            {
                'kind': 'operation',
                'operationId': 'patchTusUpload',
                'summary': 'Declare Upload-Length on the final chunk request.',
            },
        ],
        'operationIds': [
            'createTusUpload',
            'patchTusUpload',
        ],
        'primitives': [
            'defer-upload-length',
            'emit-progress',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'creationWithUpload',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Send the first bytes on the creation request when the server/client support it.',
        'featureId': 'creationWithUpload',
        'flow': [
            {
                'kind': 'operation',
                'operationId': 'createTusUpload',
                'summary': 'Create the upload while streaming the initial body.',
            },
            {
                'kind': 'primitive',
                'primitive': 'upload-during-creation',
                'summary': 'Interpret the creation response as an accepted offset.',
            },
        ],
        'operationIds': [
            'createTusUpload',
        ],
        'primitives': [
            'upload-during-creation',
            'emit-progress',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'uploadBodyHeaders',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Send protocol-specific upload body headers whenever the client transmits file bytes.',
        'featureId': 'uploadBodyHeaders',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'send-upload-body-headers',
                'summary': 'Attach the protocol-specific upload body content type when a request has bytes.',
            },
            {
                'kind': 'operation',
                'operationId': 'patchTusUpload',
                'summary': 'Upload bytes with the protocol-specific body headers.',
            },
        ],
        'operationIds': [
            'createTusUpload',
            'patchTusUpload',
        ],
        'primitives': [
            'send-upload-body-headers',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'overridePatchMethod',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Tunnel PATCH through POST with the method-override header.',
        'featureId': 'overridePatchMethod',
        'flow': [
            {
                'kind': 'operation',
                'operationId': 'getTusUploadOffset',
                'summary': 'Resume from the upload URL before sending bytes.',
            },
            {
                'kind': 'primitive',
                'primitive': 'override-patch-method',
                'summary': 'Replace PATCH with POST while preserving the protocol operation intent.',
            },
            {
                'kind': 'operation',
                'operationId': 'patchTusUpload',
                'summary': 'Upload bytes through the overridden request.',
            },
        ],
        'operationIds': [
            'getTusUploadOffset',
            'patchTusUpload',
        ],
        'primitives': [
            'override-patch-method',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'parallelUploadConcat',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Split one input into partial uploads and concatenate their upload URLs.',
        'featureId': 'parallelUploadConcat',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'split-parallel-upload-boundaries',
                'summary': 'Split the input into stable byte ranges.',
            },
            {
                'kind': 'operation',
                'operationId': 'createTusUpload',
                'summary': 'Create partial uploads for each range.',
            },
            {
                'kind': 'primitive',
                'primitive': 'concatenate-partial-uploads',
                'summary': 'Create the final upload from completed partial upload URLs.',
            },
        ],
        'operationIds': [
            'createTusUpload',
            'patchTusUpload',
        ],
        'primitives': [
            'concatenate-partial-uploads',
            'emit-progress',
            'split-parallel-upload-boundaries',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'retryPatchAfterOffsetRecovery',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Recover from a failed chunk by reading the server offset before retrying.',
        'featureId': 'retryOffsetRecovery',
        'flow': [
            {
                'kind': 'operation',
                'operationId': 'patchTusUpload',
                'summary': 'Attempt the chunk upload.',
            },
            {
                'kind': 'primitive',
                'primitive': 'recover-offset-after-error',
                'summary': 'Discover the accepted offset after a retryable failure.',
            },
            {
                'kind': 'operation',
                'operationId': 'getTusUploadOffset',
                'summary': 'Use HEAD to recover the offset before retrying PATCH.',
            },
        ],
        'operationIds': [
            'createTusUpload',
            'getTusUploadOffset',
            'patchTusUpload',
        ],
        'primitives': [
            'retry-with-backoff',
            'recover-offset-after-error',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'terminateWithRetry',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Terminate an upload resource and retry retryable termination failures.',
        'featureId': 'terminateUpload',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'terminate-upload',
                'summary': 'Choose server-side termination for an upload URL.',
            },
            {
                'kind': 'operation',
                'operationId': 'terminateTusUpload',
                'summary': 'Delete the upload resource.',
            },
        ],
        'operationIds': [
            'terminateTusUpload',
        ],
        'primitives': [
            'terminate-upload',
            'retry-with-backoff',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'abortUpload',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Abort the active request, pending retry timer, and any partial uploads.',
        'featureId': 'abortUpload',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'abort-current-request',
                'summary': 'Cancel in-flight transport work without emitting user callbacks after abort.',
            },
        ],
        'operationIds': [],
        'primitives': [
            'abort-current-request',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'singleUploadLifecycle',
                'creationWithUpload',
                'resumeFromPreviousUpload',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Expose progress and accepted-chunk callbacks from runtime upload activity.',
        'featureId': 'uploadCallbacks',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'emit-progress',
                'summary': 'Report bytes sent against known or deferred length.',
            },
            {
                'kind': 'primitive',
                'primitive': 'emit-chunk-complete',
                'summary': 'Report chunk size, accepted offset, and total size after server acceptance.',
            },
            {
                'kind': 'primitive',
                'primitive': 'emit-upload-url',
                'summary': 'Notify once a usable upload URL is known.',
            },
        ],
        'operationIds': [],
        'primitives': [
            'emit-progress',
            'emit-chunk-complete',
            'emit-upload-url',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'requestLifecycleHooks',
                'retryPatchAfterOffsetRecovery',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Run before-request, after-response, and custom retry hooks around transport.',
        'featureId': 'requestLifecycleHooks',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'run-request-hooks',
                'summary': 'Call user hooks around each HTTP request/response pair.',
            },
            {
                'kind': 'primitive',
                'primitive': 'customize-retry',
                'summary': 'Let user retry policy override default retry decisions.',
            },
        ],
        'operationIds': [],
        'primitives': [
            'customize-retry',
            'run-request-hooks',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'singleUploadLifecycle',
                'resumeFromPreviousUpload',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Persist, find, resume, and optionally remove upload URLs by fingerprint.',
        'featureId': 'resumeUrlStorage',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'fingerprint-input',
                'summary': 'Derive a stable key for the input when possible.',
            },
            {
                'kind': 'primitive',
                'primitive': 'store-resume-url',
                'summary': 'Persist upload URLs and partial-upload URLs for future resumption.',
            },
            {
                'kind': 'primitive',
                'primitive': 'remove-stored-url-on-success',
                'summary': 'Remove stored upload URLs when configured after success or invalidation.',
            },
        ],
        'operationIds': [],
        'primitives': [
            'fingerprint-input',
            'store-resume-url',
            'remove-stored-url-on-success',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'arrayBufferInput',
                'arrayBufferViewInput',
                'webReadableStreamInput',
                'nodeReadableStreamInput',
                'nodePathInput',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Support the reference client input/source families across runtimes.',
        'featureId': 'inputSources',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'read-browser-file',
                'summary': 'Read browser Blob/File and ArrayBuffer-family inputs.',
            },
            {
                'kind': 'primitive',
                'primitive': 'read-node-stream',
                'summary': 'Read Node streams when size and chunk constraints are satisfied.',
            },
            {
                'kind': 'primitive',
                'primitive': 'read-web-stream',
                'summary': 'Read Web Streams with deferred or configured size.',
            },
            {
                'kind': 'primitive',
                'primitive': 'read-node-file',
                'summary': 'Read filesystem paths and fs streams, including parallel ranges.',
            },
        ],
        'operationIds': [],
        'primitives': [
            'read-browser-file',
            'read-node-file',
            'read-node-stream',
            'read-web-stream',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [],
            'status': 'needs-generated-scenario',
        },
        'description': 'Support browser and file-backed URL storage implementations.',
        'featureId': 'urlStorageBackends',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'store-browser-url',
                'summary': 'Persist upload records in browser localStorage.',
            },
            {
                'kind': 'primitive',
                'primitive': 'store-file-url',
                'summary': 'Persist upload records in the Node file store.',
            },
        ],
        'operationIds': [],
        'primitives': [
            'store-browser-url',
            'store-file-url',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [],
            'status': 'needs-generated-scenario',
        },
        'description': 'Select between tus v1 and supported IETF draft client protocol modes.',
        'featureId': 'protocolVersionSelection',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'select-client-protocol',
                'summary': 'Choose request headers and response expectations for the selected protocol.',
            },
        ],
        'operationIds': [
            'createTusUpload',
            'getTusUploadOffset',
            'patchTusUpload',
        ],
        'primitives': [
            'select-client-protocol',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [
                'relativeLocationResolution',
            ],
            'status': 'covered-by-generated-scenario',
        },
        'description': 'Normalize relative Location headers against the request endpoint.',
        'featureId': 'relativeLocationResolution',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'resolve-relative-location',
                'summary': 'Resolve server Location headers with the creation endpoint as origin.',
            },
        ],
        'operationIds': [
            'createTusUpload',
        ],
        'primitives': [
            'resolve-relative-location',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [],
            'status': 'needs-generated-scenario',
        },
        'description': 'Validate option combinations before starting runtime work.',
        'featureId': 'startOptionValidation',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'validate-start-options',
                'summary': 'Reject missing inputs and incompatible parallel/deferred/resume options.',
            },
        ],
        'operationIds': [],
        'primitives': [
            'validate-start-options',
        ],
    },
    {
        'conformance': {
            'scenarioIds': [],
            'status': 'needs-generated-scenario',
        },
        'description': 'Attach request, response, status, body, and request ID context to errors.',
        'featureId': 'detailedErrors',
        'flow': [
            {
                'kind': 'primitive',
                'primitive': 'report-detailed-errors',
                'summary': 'Return user-facing errors with enough transport context for debugging.',
            },
        ],
        'operationIds': [],
        'primitives': [
            'report-detailed-errors',
        ],
    },
]
