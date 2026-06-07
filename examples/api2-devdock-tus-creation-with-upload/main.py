"""Create a Transloadit devdock TUS upload with bytes in the creation request."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    load_scenario,
    scenario_bytes,
    scenario_id,
    tus_url,
    upload_metadata,
    write_result,
)


def upload_with_creation_body(scenario, create_response):
    upload_config = scenario["upload"]
    content = scenario_bytes(upload_config)

    if upload_config["chunkSize"] != "full-file":
        fail("unsupported chunk size policy {!r}".format(upload_config["chunkSize"]))
    if not upload_config["uploadDataDuringCreation"]:
        fail("scenario does not enable uploadDataDuringCreation")

    uploader = tus.TusClient(
        tus_url(upload_config, scenario, create_response)
    ).create_upload_with_data(
        len(content),
        file_stream=BytesIO(content),
        chunk_size=len(content),
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
    )
    uploader.upload()

    if not uploader.url:
        fail("creation-with-upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail(
            "creation-with-upload accepted {} bytes, expected {}".format(
                uploader.offset,
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
    result = upload_with_creation_body(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} uploaded during creation to {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
