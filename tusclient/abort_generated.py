# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

import time

from tusclient.exceptions import TusCommunicationError


DEFAULT_RETRY_DELAYS = [
    0,
    1000,
    3000,
    5000,
]
RETRY_ATTEMPT_INCREMENT_POLICY = 'after-retry-scheduled'
RETRY_CLIENT_ERROR_STATUS_CATEGORY = 400
RETRYABLE_CLIENT_STATUS_CODES = [
    409,
    423,
]


def normalized_retry_delays(retry_delays):
    if retry_delays is None:
        return list(DEFAULT_RETRY_DELAYS)
    return list(retry_delays)


def should_retry_status(status_code):
    if not status_code:
        return False
    is_client_error = (
        status_code >= RETRY_CLIENT_ERROR_STATUS_CATEGORY
        and status_code < RETRY_CLIENT_ERROR_STATUS_CATEGORY + 100
    )
    return not is_client_error or status_code in RETRYABLE_CLIENT_STATUS_CODES


def should_schedule_retry(on_should_retry, error, retry_attempt, retry_delays):
    if retry_attempt >= len(retry_delays) or not should_retry_status(error.status_code):
        return False
    if on_should_retry is not None:
        return bool(on_should_retry(error, retry_attempt))
    return True


def next_retry_attempt(retry_attempt):
    if RETRY_ATTEMPT_INCREMENT_POLICY == 'after-retry-scheduled':
        return retry_attempt + 1
    raise ValueError(
        'tus: unsupported retry increment policy {}'.format(
            RETRY_ATTEMPT_INCREMENT_POLICY,
        )
    )


def terminate_upload_with_retry(
    upload_url,
    send_terminate_request,
    retry_delays=None,
    on_should_retry=None,
):
    retry_delays = normalized_retry_delays(retry_delays)
    retry_attempt = 0

    while True:
        error = None
        try:
            response = send_terminate_request(upload_url)
        except TusCommunicationError as terminate_error:
            error = terminate_error
        if error is None:
            return response

        if not should_schedule_retry(on_should_retry, error, retry_attempt, retry_delays):
            raise error

        delay_ms = retry_delays[retry_attempt]
        if delay_ms > 0:
            time.sleep(delay_ms / 1000)
        retry_attempt = next_retry_attempt(retry_attempt)
