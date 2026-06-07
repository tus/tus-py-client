"""Upload to a Transloadit devdock Assembly using tus-py-client.

This example is intentionally checked into the SDK repository. API2 owns the
scenario JSON and prepares the live Transloadit Assembly; this file only shows
ordinary tus-py-client usage against the injected TUS endpoint.
"""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    load_scenario,
    scenario_bytes,
    tus_url,
    upload_metadata,
    write_result,
)


def upload_with_tus(scenario, create_response):
    upload_config = scenario["upload"]
    endpoint_url = tus_url(upload_config, scenario, create_response)
    content = scenario_bytes(upload_config)
    if upload_config["chunkSize"] != "full-file":
        fail("unsupported chunk size policy {!r}".format(upload_config["chunkSize"]))

    uploader = tus.TusClient(endpoint_url).uploader(
        file_stream=BytesIO(content),
        chunk_size=len(content),
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
    )
    uploader.upload()

    if not uploader.url:
        fail("TUS upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail("TUS upload offset {}, expected {}".format(uploader.offset, len(content)))

    return uploader.url


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    upload_url = upload_with_tus(scenario, create_response)
    write_result({"uploadUrl": upload_url})
    print(
        "Python TUS SDK devdock scenario {} uploaded to {}".format(
            scenario["scenarioId"], upload_url
        )
    )


if __name__ == "__main__":
    main()
