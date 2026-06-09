"""Validate detailed TUS create-upload errors from contract scenarios."""

import sys
from io import BytesIO
from pathlib import Path

import requests
from tusclient import client as tus
from tusclient.exceptions import TusDetailedError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    load_scenario,
    object_value,
    scenario_id,
    string_value,
    write_result,
)


def conformance_input_options(conformance_scenario):
    entries = conformance_scenario["inputOptionEntries"]
    if not isinstance(entries, list):
        fail("conformanceScenario.inputOptionEntries must be a list")

    result = {}
    for index, entry in enumerate(entries):
        option = object_value(
            entry,
            "conformanceScenario.inputOptionEntries[{}]".format(index),
        )
        key = string_value(
            option["key"],
            "conformanceScenario.inputOptionEntries[{}].key".format(index),
        )
        result[key] = option["value"]

    return result


def conformance_input_source_bytes(conformance_scenario):
    input_source = object_value(
        conformance_scenario["inputSource"],
        "conformanceScenario.inputSource",
    )
    kind = string_value(input_source["kind"], "conformanceScenario.inputSource.kind")
    if kind != "blob":
        fail("unsupported conformance input source kind {!r}".format(kind))

    return string_value(
        input_source["content"],
        "conformanceScenario.inputSource.content",
    ).encode("utf-8")


def conformance_request(conformance_scenario):
    requests_list = conformance_scenario["requests"]
    if not isinstance(requests_list, list) or len(requests_list) != 1:
        fail("detailed error scenario must have exactly one request")
    return object_value(requests_list[0], "conformanceScenario.requests[0]")


def assert_expected_headers(actual_headers, expected_headers):
    normalized_actual_headers = {}
    for key, value in actual_headers.items():
        normalized_actual_headers[key.lower()] = value

    for key, expected_value in expected_headers.items():
        actual_value = normalized_actual_headers.get(key.lower())
        if actual_value != expected_value:
            fail(
                "detailed error expected header {}={!r}, got {!r}".format(
                    key,
                    expected_value,
                    actual_value,
                )
            )


def response_for(request_plan):
    response_plan = object_value(
        request_plan["response"],
        "conformanceScenario.requests[0].response",
    )
    response = requests.Response()
    response.status_code = response_plan["statusCode"]
    response._content = string_value(
        response_plan["body"],
        "conformanceScenario.requests[0].response.body",
    ).encode("utf-8")
    response.headers.update(response_plan.get("headers") or {})
    return response


def upload_expect_detailed_error(conformance_scenario):
    request_plan = conformance_request(conformance_scenario)
    input_options = conformance_input_options(conformance_scenario)
    endpoint_url = string_value(input_options["endpointUrl"], "endpointUrl")
    metadata = object_value(input_options["metadata"], "metadata")
    headers = object_value(input_options["headers"], "headers")
    content = conformance_input_source_bytes(conformance_scenario)
    request_methods = []
    request_urls = []
    original_post = requests.post

    def fake_post(url, **kwargs):
        request_methods.append(request_plan["effectiveMethod"])
        request_urls.append(url)
        if url != request_plan["expectedUrl"]:
            fail(
                "detailed error expected URL {!r}, got {!r}".format(
                    request_plan["expectedUrl"],
                    url,
                )
            )
        assert_expected_headers(kwargs["headers"], request_plan["headers"])
        error_message = request_plan.get("errorMessage")
        if error_message is not None:
            raise requests.exceptions.ConnectionError(error_message)
        return response_for(request_plan)

    requests.post = fake_post
    try:
        try:
            tus.TusClient(endpoint_url, headers=headers).uploader(
                file_stream=BytesIO(content),
                metadata=metadata,
            ).create_url()
        except Exception as error:
            return detailed_result(error, request_methods, request_urls)
    finally:
        requests.post = original_post

    fail("detailed error scenario unexpectedly created an upload")


def detailed_result(error, request_methods, request_urls):
    result = {
        "errorCaught": True,
        "errorIsDetailed": isinstance(error, TusDetailedError),
        "errorMessage": str(error),
        "requestCount": len(request_methods),
        "requestMethods": request_methods,
        "requestUrls": request_urls,
    }

    if not isinstance(error, TusDetailedError):
        return result

    result["causingErrorPresent"] = error.causing_error is not None
    if error.causing_error is not None:
        result["causingErrorMessage"] = str(error.causing_error)
    result["originalRequestMethod"] = error.original_request_method
    result["originalRequestRequestId"] = error.original_request_id
    result["originalRequestUrl"] = error.original_request_url
    result["originalResponsePresent"] = error.original_response_present
    if error.original_response_present:
        result["originalResponseBody"] = error.original_response_body
        result["originalResponseStatus"] = error.original_response_status

    return result


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    conformance_scenario = object_value(
        scenario["conformanceScenario"],
        "conformanceScenario",
    )
    result = upload_expect_detailed_error(conformance_scenario)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} observed detailed error {}".format(
            scenario_id(scenario),
            result["errorMessage"],
        )
    )


if __name__ == "__main__":
    main()
