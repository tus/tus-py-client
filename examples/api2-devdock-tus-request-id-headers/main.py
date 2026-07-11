"""Send Transloadit devdock TUS request ID headers."""

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
    upload_add_request_id,
    upload_headers,
    upload_metadata,
    upload_request_id_header_name,
    write_result,
)


def record_request_id_header(context, request_id_header_name, custom_request_id):
    actual_value = context.headers.get(request_id_header_name)
    if actual_value is None:
        fail("request ID header {} was not sent".format(request_id_header_name))
    if actual_value == custom_request_id:
        fail(
            "request ID header {} was not generated; saw custom value {!r}".format(
                request_id_header_name,
                custom_request_id,
            )
        )
    if len(actual_value) != 36 or "-" not in actual_value:
        fail(
            "request ID header {} expected generated UUID shape, got {!r}".format(
                request_id_header_name,
                actual_value,
            )
        )
    return {request_id_header_name: actual_value}


def upload_with_request_id_headers(scenario, create_response):
    upload_config = scenario["upload"]
    request_id_header_name = upload_request_id_header_name(scenario)
    custom_headers = upload_headers(scenario)
    custom_request_id = custom_headers[request_id_header_name]
    content = scenario_bytes(upload_config)
    headers_by_method = {}
    if upload_config["chunkSize"] != "full-file":
        fail("unsupported chunk size policy {!r}".format(upload_config["chunkSize"]))

    def before_request(context):
        if context.method in ("POST", "PATCH"):
            headers_by_method[context.method] = record_request_id_header(
                context,
                request_id_header_name,
                custom_request_id,
            )

    uploader = tus.TusClient(
        tus_url(upload_config, scenario, create_response),
        headers=custom_headers,
        request_hooks=RequestLifecycleHooks(before_request=before_request),
        add_request_id=upload_add_request_id(scenario),
    ).uploader(
        file_stream=BytesIO(content),
        chunk_size=len(content),
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
    )
    uploader.upload()

    if not uploader.url:
        fail("request ID headers upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail(
            "request ID headers upload offset {}, expected {}".format(
                uploader.offset,
                len(content),
            )
        )
    for method in ("POST", "PATCH"):
        if method not in headers_by_method:
            fail("request ID headers did not observe {} request".format(method))

    return {
        "headersByMethod": headers_by_method,
        "uploadUrl": uploader.url,
    }


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    result = upload_with_request_id_headers(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} sent request ID headers for {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
