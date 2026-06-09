from tusclient.exceptions import TusDetailedError
from tusclient.protocol_generated import (
    DETAILED_ERROR_CAUSE_STRING_TEMPLATE,
    DETAILED_ERROR_CAUSED_BY_TEMPLATE,
    DETAILED_ERROR_CREATE_UPLOAD_REQUEST_FAILED,
    DETAILED_ERROR_EMPTY_RESPONSE_BODY,
    DETAILED_ERROR_MISSING_VALUE,
    DETAILED_ERROR_REQUEST_CONTEXT_TEMPLATE,
    DETAILED_ERROR_UNEXPECTED_CREATE_RESPONSE,
    REQUEST_ID_HEADER_NAME,
)


def create_upload_response_error(context, response):
    body = response_body(response)
    message = detailed_error_message(
        DETAILED_ERROR_UNEXPECTED_CREATE_RESPONSE,
        request_context={
            'body': body,
            'method': context.method,
            'requestId': request_id(context),
            'status': response.status_code,
            'url': context.url,
        },
    )
    return TusDetailedError(
        message,
        status_code=response.status_code,
        response_content=response.content,
        original_request_method=context.method,
        original_request_url=context.url,
        original_request_id=request_id(context),
        original_response_body=body,
        original_response_present=True,
        original_response_status=response.status_code,
    )


def create_upload_request_error(context, error):
    message = detailed_error_message(
        DETAILED_ERROR_CREATE_UPLOAD_REQUEST_FAILED,
        cause=error,
        request_context={
            'body': DETAILED_ERROR_MISSING_VALUE,
            'method': context.method,
            'requestId': request_id(context),
            'status': DETAILED_ERROR_MISSING_VALUE,
            'url': context.url,
        },
    )
    return TusDetailedError(
        message,
        causing_error=error,
        original_request_method=context.method,
        original_request_url=context.url,
        original_request_id=request_id(context),
    )


def detailed_error_message(base_message, cause=None, request_context=None):
    message = base_message
    if cause is not None:
        cause_message = format_flow_message(
            DETAILED_ERROR_CAUSE_STRING_TEMPLATE,
            {'message': missing_if_empty(str(cause))},
        )
        message += format_flow_message(
            DETAILED_ERROR_CAUSED_BY_TEMPLATE,
            {'cause': cause_message},
        )

    if request_context is not None:
        message += format_flow_message(
            DETAILED_ERROR_REQUEST_CONTEXT_TEMPLATE,
            request_context,
        )

    return message


def format_flow_message(template, values):
    message = template
    for key, value in values.items():
        message = message.replace('{{{}}}'.format(key), str(value))
    return message


def missing_if_empty(value):
    if value is None or value == '':
        return DETAILED_ERROR_MISSING_VALUE
    return value


def request_id(context):
    return missing_if_empty(context.headers.get(REQUEST_ID_HEADER_NAME))


def response_body(response):
    body = response.content
    if body is None:
        return DETAILED_ERROR_MISSING_VALUE
    if body == b'':
        return DETAILED_ERROR_EMPTY_RESPONSE_BODY
    if isinstance(body, bytes):
        return body.decode('utf-8', 'replace')
    return str(body)
