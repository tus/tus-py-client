import io
import unittest
from urllib.parse import urljoin

import responses

from tests.generated_protocol_contract import (
    TUS_CLIENT_FEATURES,
    TUS_PROTOCOL_OPERATIONS,
    TUS_WIRE_VERSIONS,
)
from tusclient.client import TusClient
from tusclient.protocol_generated import (
    DEFAULT_PROTOCOL_VERSION,
    DEFAULT_REQUEST_HEADERS,
    DEFAULT_RESPONSE_HEADERS,
)
from tusclient.uploader.baseuploader import BaseUploader


def default_wire_version():
    versions = [version for version in TUS_WIRE_VERSIONS if version["default"]]
    if len(versions) != 1:
        raise AssertionError("Generated TUS protocol contract must have one default wire version")
    return versions[0]["value"]


def protocol_operation(operation_id):
    for operation in TUS_PROTOCOL_OPERATIONS:
        if operation["operationId"] == operation_id:
            return operation
    raise AssertionError("Missing generated TUS protocol operation: {}".format(operation_id))


def client_feature(feature_id):
    for feature in TUS_CLIENT_FEATURES:
        if feature["featureId"] == feature_id:
            return feature
    raise AssertionError("Missing generated TUS client feature: {}".format(feature_id))


def response_for(operation, status_code):
    for response in operation["responses"]:
        if response["statusCode"] == status_code:
            return response
    raise AssertionError(
        "Missing generated response status {} for {}".format(
            status_code,
            operation["operationId"],
        )
    )


def response_headers_for(response, overrides):
    headers = {}
    variant = response["headerVariants"][0]
    for field in variant["fields"]:
        if not field["required"]:
            continue
        if field["displayName"] in overrides:
            headers[field["displayName"]] = overrides[field["displayName"]]
            continue
        headers[field["displayName"]] = DEFAULT_RESPONSE_HEADERS[field["displayName"]]
    return headers


def request_header(request, field):
    return request.headers.get(field["displayName"]) or request.headers.get(field["name"])


class GeneratedProtocolContractTest(unittest.TestCase):
    def test_runtime_default_headers_are_generated_contract_headers(self):
        self.assertEqual(BaseUploader.DEFAULT_HEADERS, DEFAULT_REQUEST_HEADERS)

    @responses.activate
    def test_drives_create_and_patch_lifecycle_assertions_from_generated_contract(self):
        self.assertEqual(DEFAULT_PROTOCOL_VERSION, default_wire_version())

        lifecycle = client_feature("singleUploadLifecycle")
        create_operation = protocol_operation(lifecycle["operationIds"][0])
        patch_operation = protocol_operation(lifecycle["operationIds"][2])
        client = TusClient("http://tusd.tusdemo.net/files/")
        upload_url = urljoin(client.url, "generated-contract")

        create_response = response_for(create_operation, 201)
        responses.add(
            create_operation["method"],
            client.url,
            adding_headers=response_headers_for(
                create_response,
                {"Location": upload_url},
            ),
            status=create_response["statusCode"],
        )

        patch_response = response_for(patch_operation, 204)
        responses.add(
            patch_operation["method"],
            upload_url,
            adding_headers=response_headers_for(
                patch_response,
                {"Upload-Offset": "5"},
            ),
            status=patch_response["statusCode"],
        )

        uploader = client.uploader(
            file_stream=io.BytesIO(b"hello"),
            chunk_size=5,
            metadata={"filename": "hello.txt"},
        )
        uploader.upload()

        create_request = responses.calls[0].request
        self.assertEqual(create_request.method, create_operation["method"])
        for field in create_operation["request"]["headerVariants"][0]["fields"]:
            self.assertIsNotNone(request_header(create_request, field))
        self.assertEqual(
            request_header(
                create_request,
                {"displayName": "Tus-Resumable", "name": "tus-resumable"},
            ),
            default_wire_version(),
        )
        self.assertEqual(
            request_header(
                create_request,
                {"displayName": "Upload-Length", "name": "upload-length"},
            ),
            "5",
        )
        self.assertEqual(
            request_header(
                create_request,
                {"displayName": "Upload-Metadata", "name": "upload-metadata"},
            ),
            "filename aGVsbG8udHh0",
        )

        patch_request = responses.calls[1].request
        self.assertEqual(patch_request.method, patch_operation["method"])
        for field in patch_operation["request"]["headerVariants"][0]["fields"]:
            self.assertIsNotNone(request_header(patch_request, field))
        self.assertEqual(
            request_header(
                patch_request,
                {"displayName": "Content-Type", "name": "content-type"},
            ),
            patch_operation["request"]["contentType"],
        )
        self.assertEqual(
            request_header(
                patch_request,
                {"displayName": "Upload-Offset", "name": "upload-offset"},
            ),
            "0",
        )
        self.assertEqual(patch_request.body, b"hello")
        self.assertEqual(uploader.url, upload_url)
        self.assertEqual(uploader.offset, 5)
