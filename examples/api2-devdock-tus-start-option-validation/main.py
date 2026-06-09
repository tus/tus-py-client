"""Validate conflicting TUS start options before transport."""

import sys
from io import BytesIO
from pathlib import Path

import requests
from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    conformance_input_options,
    conformance_input_source_bytes,
    fail,
    int_value,
    load_scenario,
    object_value,
    scenario_id,
    string_value,
    write_result,
)


def bool_value(value, label):
    if not isinstance(value, bool):
        fail("{} must be a boolean".format(label))
    return value


def conformance_completion(conformance_scenario):
    return object_value(
        conformance_scenario["completion"],
        "conformanceScenario.completion",
    )


def run_with_request_counter(operation):
    request_count = 0
    original_head = requests.head
    original_patch = requests.patch
    original_post = requests.post
    original_request = requests.request

    def record_request(*args, **kwargs):
        nonlocal request_count
        request_count += 1
        fail("start option validation made an unexpected HTTP request")

    requests.head = record_request
    requests.patch = record_request
    requests.post = record_request
    requests.request = record_request
    try:
        return operation(), request_count
    finally:
        requests.head = original_head
        requests.patch = original_patch
        requests.post = original_post
        requests.request = original_request


def validate_start_options(scenario):
    conformance_scenario = object_value(
        scenario["conformanceScenario"],
        "conformanceScenario",
    )
    completion = conformance_completion(conformance_scenario)
    input_options = conformance_input_options(conformance_scenario)
    content = conformance_input_source_bytes(conformance_scenario)
    expected_message = string_value(
        completion["message"],
        "conformanceScenario.completion.message",
    )

    def start_upload():
        try:
            tus.TusClient(input_options["endpointUrl"]).uploader(
                file_stream=BytesIO(content),
                parallel_uploads=int_value(
                    input_options["parallelUploads"],
                    "conformanceScenario.inputOptionEntries.parallelUploads",
                ),
                upload_data_during_creation=bool_value(
                    input_options.get("uploadDataDuringCreation", False),
                    "conformanceScenario.inputOptionEntries.uploadDataDuringCreation",
                ),
                url=input_options.get("uploadUrl"),
            )
        except ValueError as error:
            return {
                "errorCaught": True,
                "errorMessage": str(error),
            }

        fail("start option validation unexpectedly accepted conflicting options")

    result, request_count = run_with_request_counter(start_upload)
    result["requestCount"] = request_count
    if result["errorMessage"] != expected_message:
        fail(
            "start option validation expected error {!r}, got {!r}".format(
                expected_message,
                result["errorMessage"],
            )
        )

    return result


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    result = validate_start_options(scenario)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} rejected conflicting start options".format(
            scenario_id(scenario),
        )
    )


if __name__ == "__main__":
    main()
