"""Recover a Transloadit devdock TUS upload offset after a retry."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus
from tusclient.request_lifecycle import RequestLifecycleHooks

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    fixed_chunk_size_bytes,
    load_scenario,
    retry_offset_recovery,
    scenario_bytes,
    scenario_id,
    tus_url,
    upload_metadata,
    write_result,
)


def int_header(response, header_name):
    value = response.headers.get(header_name)
    try:
        offset = int(value)
    except (TypeError, ValueError):
        fail(
            "retry offset recovery expected numeric {} response header, got {!r}".format(
                header_name,
                value,
            )
        )

    if offset < 0:
        fail("retry offset recovery expected non-negative offset, got {}".format(offset))

    return offset


def assert_request_methods(actual, expected):
    if actual != expected:
        fail("retry offset recovery expected request methods {}, got {}".format(expected, actual))


def upload_with_retry_offset_recovery(scenario, create_response):
    upload_config = scenario["upload"]
    retry = retry_offset_recovery(scenario)
    content = scenario_bytes(upload_config)
    chunk_size = fixed_chunk_size_bytes(scenario)
    recovered_offsets = []
    request_methods = []
    failure_candidate_count = 0
    simulated_failure_count = 0

    def before_request(context):
        request_methods.append(context.method)

    def after_response(context, response):
        nonlocal failure_candidate_count
        nonlocal simulated_failure_count

        if context.method == retry["recoveryResponse"]["method"]:
            recovered_offsets.append(
                int_header(response, retry["recoveryResponse"]["offsetHeader"])
            )

        if context.method != retry["failAfterResponse"]["method"]:
            return

        failure_candidate_count += 1
        if failure_candidate_count != retry["failAfterResponse"]["occurrence"]:
            return

        simulated_failure_count += 1
        response.status_code = 500
        response._content = retry["failAfterResponse"]["message"].encode("utf-8")

    client = tus.TusClient(
        tus_url(upload_config, scenario, create_response),
        request_hooks=RequestLifecycleHooks(
            before_request=before_request,
            after_response=after_response,
        ),
    )
    uploader = client.uploader(
        file_stream=BytesIO(content),
        chunk_size=chunk_size,
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
        retry_delay=0,
    )
    uploader.upload()

    if not uploader.url:
        fail("retry offset recovery TUS upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail("retry offset recovery upload offset {}, expected {}".format(uploader.offset, len(content)))
    if simulated_failure_count != retry["expectedFailureCount"]:
        fail(
            "retry offset recovery expected {} simulated failure(s), got {}".format(
                retry["expectedFailureCount"],
                simulated_failure_count,
            )
        )
    if len(recovered_offsets) != retry["expectedRecoveryRequestCount"]:
        fail(
            "retry offset recovery expected {} recovery request(s), got {}".format(
                retry["expectedRecoveryRequestCount"],
                len(recovered_offsets),
            )
        )
    if recovered_offsets[0] != retry["expectedRecoveredOffset"]:
        fail(
            "retry offset recovery expected recovered offset {}, got {}".format(
                retry["expectedRecoveredOffset"],
                recovered_offsets[0],
            )
        )
    assert_request_methods(request_methods, retry["expectedRequestMethods"])

    return {
        "recoveredOffsets": recovered_offsets,
        "recoveryRequestCount": len(recovered_offsets),
        "requestMethods": request_methods,
        "simulatedFailureCount": simulated_failure_count,
        "uploadUrl": uploader.url,
    }


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    result = upload_with_retry_offset_recovery(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} recovered offset for {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
