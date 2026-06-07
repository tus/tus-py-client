"""Terminate a Transloadit devdock TUS upload."""

import sys
from io import BytesIO
from pathlib import Path

import requests
from tusclient import client as tus
from tusclient.protocol_generated import DEFAULT_REQUEST_HEADERS
from tusclient.request_lifecycle import RequestLifecycleHooks

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    fixed_chunk_size_bytes,
    load_scenario,
    scenario_bytes,
    scenario_id,
    termination,
    tus_url,
    upload_metadata,
    write_result,
)


def count_method(methods, expected_method):
    count = 0
    for method in methods:
        if method == expected_method:
            count += 1
    return count


def verify_terminated_upload(termination_plan, upload_url):
    response = requests.request(
        termination_plan["verificationMethod"],
        upload_url,
        headers=DEFAULT_REQUEST_HEADERS,
    )
    return response.status_code


def upload_and_terminate(scenario, create_response):
    upload_config = scenario["upload"]
    termination_plan = termination(scenario)
    content = scenario_bytes(upload_config)
    chunk_size = fixed_chunk_size_bytes(scenario)
    request_methods = []

    if termination_plan["stopAfterAcceptedBytes"] > len(content):
        fail(
            "terminate upload stop-after bytes {} exceeds content length {}".format(
                termination_plan["stopAfterAcceptedBytes"],
                len(content),
            )
        )

    def before_request(context):
        request_methods.append(context.method)

    uploader = tus.TusClient(
        tus_url(upload_config, scenario, create_response),
        request_hooks=RequestLifecycleHooks(before_request=before_request),
    ).uploader(
        file_stream=BytesIO(content),
        chunk_size=chunk_size,
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
    )
    uploader.upload(stop_at=termination_plan["stopAfterAcceptedBytes"])

    if not uploader.url:
        fail("terminate upload did not expose an upload URL")
    if uploader.offset != termination_plan["stopAfterAcceptedBytes"]:
        fail(
            "terminate upload accepted {} bytes, expected {}".format(
                uploader.offset,
                termination_plan["stopAfterAcceptedBytes"],
            )
        )

    uploader.client.terminate_upload(uploader.url)
    verification_status = verify_terminated_upload(termination_plan, uploader.url)
    if verification_status != termination_plan["expectedVerificationStatus"]:
        fail(
            "terminate upload verification status {}, expected {}".format(
                verification_status,
                termination_plan["expectedVerificationStatus"],
            )
        )

    return {
        "acceptedBytes": uploader.offset,
        "deleteRequestCount": count_method(request_methods, termination_plan["method"]),
        "requestMethods": request_methods,
        "terminated": True,
        "uploadUrl": uploader.url,
        "verificationStatus": verification_status,
    }


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    result = upload_and_terminate(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} terminated {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
