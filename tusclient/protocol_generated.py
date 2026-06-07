# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

DEFAULT_PROTOCOL_VERSION = '1.0.0'
DEFAULT_REQUEST_HEADERS = {
    'Tus-Resumable': '1.0.0',
}
DEFAULT_RESPONSE_HEADERS = {
    'Tus-Resumable': '1.0.0',
}
REQUEST_ID_HEADER_NAME = 'X-Request-ID'


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
