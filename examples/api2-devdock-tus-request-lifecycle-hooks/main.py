"""Observe Transloadit devdock TUS request lifecycle hooks."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus
from tusclient.request_lifecycle import RequestLifecycleHooks

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    load_scenario,
    request_lifecycle_hooks,
    scenario_bytes,
    scenario_id,
    tus_url,
    upload_metadata,
    write_result,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        fail("request lifecycle hooks expected {} {}, got {}".format(label, expected, actual))


def upload_with_request_lifecycle_hooks(scenario, create_response):
    upload_config = scenario["upload"]
    hooks = request_lifecycle_hooks(scenario)
    content = scenario_bytes(upload_config)
    before_request_methods = []
    after_response_methods = []
    after_response_status_codes = []
    if upload_config["chunkSize"] != "full-file":
        fail("unsupported chunk size policy {!r}".format(upload_config["chunkSize"]))

    def before_request(context):
        before_request_methods.append(context.method)

    def after_response(context, response):
        after_response_methods.append(context.method)
        after_response_status_codes.append(response.status_code)

    uploader = tus.TusClient(
        tus_url(upload_config, scenario, create_response),
        request_hooks=RequestLifecycleHooks(
            before_request=before_request,
            after_response=after_response,
        ),
    ).uploader(
        file_stream=BytesIO(content),
        chunk_size=len(content),
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
    )
    uploader.upload()

    if not uploader.url:
        fail("request lifecycle hooks upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail(
            "request lifecycle hooks upload offset {}, expected {}".format(
                uploader.offset,
                len(content),
            )
        )

    assert_equal(
        before_request_methods,
        hooks["expectedBeforeRequestMethods"],
        "before request methods",
    )
    assert_equal(
        after_response_methods,
        hooks["expectedAfterResponseMethods"],
        "after response methods",
    )
    assert_equal(
        after_response_status_codes,
        hooks["expectedAfterResponseStatusCodes"],
        "after response status codes",
    )

    return {
        "afterResponseMethods": after_response_methods,
        "afterResponseStatusCodes": after_response_status_codes,
        "beforeRequestMethods": before_request_methods,
        "uploadUrl": uploader.url,
    }


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    result = upload_with_request_lifecycle_hooks(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} observed lifecycle hooks for {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
