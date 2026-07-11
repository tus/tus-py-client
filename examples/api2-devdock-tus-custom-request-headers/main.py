"""Send Transloadit devdock TUS custom request headers."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus
from tusclient.request_lifecycle import RequestLifecycleHooks

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    load_scenario,
    scenario_bytes,
    scenario_id,
    tus_url,
    upload_headers,
    upload_metadata,
    write_result,
)


def record_custom_request_headers(context, expected_headers):
    observed = {}
    for header_name, expected_value in expected_headers.items():
        actual_value = context.headers.get(header_name)
        if actual_value != expected_value:
            fail(
                "custom request header {} expected {!r}, got {!r}".format(
                    header_name,
                    expected_value,
                    actual_value,
                )
            )
        observed[header_name] = actual_value
    return observed


def upload_with_custom_request_headers(scenario, create_response):
    upload_config = scenario["upload"]
    expected_headers = upload_headers(scenario)
    content = scenario_bytes(upload_config)
    headers_by_method = {}
    if upload_config["chunkSize"] != "full-file":
        fail("unsupported chunk size policy {!r}".format(upload_config["chunkSize"]))

    def before_request(context):
        if context.method in ("POST", "PATCH"):
            headers_by_method[context.method] = record_custom_request_headers(
                context,
                expected_headers,
            )

    uploader = tus.TusClient(
        tus_url(upload_config, scenario, create_response),
        headers=expected_headers,
        request_hooks=RequestLifecycleHooks(before_request=before_request),
    ).uploader(
        file_stream=BytesIO(content),
        chunk_size=len(content),
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
    )
    uploader.upload()

    if not uploader.url:
        fail("custom request headers upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail(
            "custom request headers upload offset {}, expected {}".format(
                uploader.offset,
                len(content),
            )
        )
    for method in ("POST", "PATCH"):
        if method not in headers_by_method:
            fail("custom request headers did not observe {} request".format(method))

    return {
        "headersByMethod": headers_by_method,
        "uploadUrl": uploader.url,
    }


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    result = upload_with_custom_request_headers(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} sent custom request headers for {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
