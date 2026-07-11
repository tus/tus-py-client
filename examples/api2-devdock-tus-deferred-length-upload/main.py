"""Create a Transloadit devdock TUS upload with deferred upload length."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    fixed_chunk_size_bytes,
    load_scenario,
    scenario_bytes,
    scenario_id,
    tus_url,
    upload_metadata,
    write_result,
)


def upload_with_deferred_length(scenario, create_response):
    upload_config = scenario["upload"]
    content = scenario_bytes(upload_config)
    chunk_size = fixed_chunk_size_bytes(scenario)

    if not upload_config["uploadLengthDeferred"]:
        fail("scenario does not enable uploadLengthDeferred")
    if chunk_size <= len(content):
        fail(
            "deferred-length scenario chunk size {} must exceed payload size {}".format(
                chunk_size,
                len(content),
            )
        )

    uploader = tus.TusClient(tus_url(upload_config, scenario, create_response)).uploader(
        file_stream=BytesIO(content),
        chunk_size=chunk_size,
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
        upload_length_deferred=True,
    )
    uploader.upload()

    if not uploader.url:
        fail("deferred-length TUS upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail(
            "deferred-length upload accepted {} bytes, expected {}".format(
                uploader.offset,
                len(content),
            )
        )
    if uploader.file_size != len(content):
        fail(
            "deferred-length upload declared final size {}, expected {}".format(
                uploader.file_size,
                len(content),
            )
        )

    return {
        "acceptedBytes": uploader.offset,
        "uploadUrl": uploader.url,
    }


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    result = upload_with_deferred_length(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} deferred length for {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
