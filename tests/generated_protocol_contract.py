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
        'featureId': 'singleUploadLifecycle',
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
        'featureId': 'terminateUpload',
        'operationIds': [
            'terminateTusUpload',
        ],
        'primitives': [
            'retry-with-backoff',
        ],
    },
]
