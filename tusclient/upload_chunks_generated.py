# Code generated from Transloadit API2 TUS protocol contracts; DO NOT EDIT.
# If it looks wrong, please report the issue instead of editing this file by hand;
# the source fix belongs in the protocol contract generator so all TUS clients stay in sync.

import time

from tusclient.abort_generated import next_retry_attempt
from tusclient.exceptions import TusCommunicationError, TusUploadFailed


RETRY_ATTEMPT_RESET_POLICY = 'when-offset-advanced-since-last-retry'


def effective_retry_attempt(retry_attempt, offset, offset_before_retry):
    if RETRY_ATTEMPT_RESET_POLICY == 'when-offset-advanced-since-last-retry':
        if offset > offset_before_retry:
            return 0
        return retry_attempt
    raise ValueError(
        'tus: unsupported retry reset policy {}'.format(
            RETRY_ATTEMPT_RESET_POLICY,
        )
    )


def should_schedule_upload_retry(on_should_retry, error, retry_attempt, retry_delays):
    if retry_attempt >= len(retry_delays):
        return False
    if on_should_retry is not None:
        return bool(on_should_retry(error, retry_attempt))
    return True


def upload_chunk_with_retry(
    uploader,
    perform_patch_request,
    retry_delays,
    on_should_retry=None,
):
    uploader._retried = 0
    offset_before_retry = uploader.offset
    start_offset = uploader.offset

    if not uploader.upload_length_deferred:
        uploader.notify_progress(start_offset)

    while True:
        error = None
        try:
            perform_patch_request()
        except TusUploadFailed as patch_error:
            error = patch_error
        if error is None:
            if uploader.upload_length_deferred:
                uploader.notify_progress(start_offset)
            uploader.notify_progress(uploader.offset)
            uploader.notify_chunk_complete(uploader.offset - start_offset, uploader.offset)
            return

        while error is not None:
            effective_attempt = effective_retry_attempt(
                uploader._retried,
                uploader.offset,
                offset_before_retry,
            )
            if not should_schedule_upload_retry(
                on_should_retry,
                error,
                effective_attempt,
                retry_delays,
            ):
                raise error

            delay_ms = retry_delays[effective_attempt]
            if delay_ms > 0:
                time.sleep(delay_ms / 1000)
            uploader._retried = next_retry_attempt(effective_attempt)
            offset_before_retry = uploader.offset
            error = None
            try:
                uploader.offset = uploader.get_offset()
            except TusCommunicationError as sync_error:
                error = sync_error
            continue
