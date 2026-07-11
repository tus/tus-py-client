from io import BytesIO

import pytest
import requests
import responses

from tusclient import client
from tusclient.exceptions import TusDetailedError
from tusclient.protocol_generated import CREATE_UPLOAD_METHOD, REQUEST_ID_HEADER_NAME


def uploader_for(tus_client):
    return tus_client.uploader(
        file_stream=BytesIO(b'hello world'),
        metadata={'filename': 'hello.txt'},
    )


@responses.activate
def test_create_upload_response_error_preserves_context():
    endpoint = 'https://tus.io/uploads'
    tus_client = client.TusClient(
        endpoint,
        headers={REQUEST_ID_HEADER_NAME: 'contract-request-id'},
    )
    responses.add(CREATE_UPLOAD_METHOD, endpoint, status=500, body='server_error')

    with pytest.raises(TusDetailedError) as error:
        uploader_for(tus_client).create_url()

    assert str(error.value) == (
        'tus: unexpected response while creating upload, originated from request '
        '(method: POST, url: https://tus.io/uploads, response code: 500, '
        'response text: server_error, request id: contract-request-id)'
    )
    assert error.value.causing_error is None
    assert error.value.original_request_method == CREATE_UPLOAD_METHOD
    assert error.value.original_request_url == endpoint
    assert error.value.original_request_id == 'contract-request-id'
    assert error.value.original_response_body == 'server_error'
    assert error.value.original_response_present is True
    assert error.value.original_response_status == 500
    assert error.value.status_code == 500
    assert error.value.response_content == b'server_error'


def test_create_upload_request_error_preserves_context(monkeypatch):
    endpoint = 'https://tus.io/uploads'
    tus_client = client.TusClient(
        endpoint,
        headers={REQUEST_ID_HEADER_NAME: 'contract-request-id'},
    )

    def failing_post(url, **kwargs):
        assert url == endpoint
        assert kwargs['headers'][REQUEST_ID_HEADER_NAME] == 'contract-request-id'
        raise requests.exceptions.ConnectionError('socket down')

    monkeypatch.setattr(requests, 'post', failing_post)

    with pytest.raises(TusDetailedError) as error:
        uploader_for(tus_client).create_url()

    assert str(error.value) == (
        'tus: failed to create upload, caused by Error: socket down, '
        'originated from request (method: POST, url: https://tus.io/uploads, '
        'response code: n/a, response text: n/a, request id: contract-request-id)'
    )
    assert str(error.value.causing_error) == 'socket down'
    assert error.value.original_request_method == CREATE_UPLOAD_METHOD
    assert error.value.original_request_url == endpoint
    assert error.value.original_request_id == 'contract-request-id'
    assert error.value.original_response_body is None
    assert error.value.original_response_present is False
    assert error.value.original_response_status is None
    assert error.value.status_code is None
    assert error.value.response_content is None
