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
LOCATION_HEADER_NAME = 'Location'
METADATA_HEADER_NAME = 'Upload-Metadata'
OFFSET_DISCOVERY_METHOD = 'HEAD'
REQUEST_ID_HEADER_NAME = 'X-Request-ID'
SUCCESS_RESPONSE_STATUS_CATEGORY = 200
TERMINATE_UPLOAD_METHOD = 'DELETE'
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
