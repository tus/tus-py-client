"""Upload TUS bytes by tunneling PATCH through an override POST."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    TusConformancePlanServer,
    bool_value,
    conformance_input_options,
    conformance_input_source_bytes,
    fail,
    load_scenario,
    object_value,
    scenario_id,
    string_value,
    write_result,
)


def upload_with_override_patch_method(conformance_scenario):
    input_options = conformance_input_options(conformance_scenario)
    content = conformance_input_source_bytes(conformance_scenario)
    endpoint_url = string_value(input_options["endpointUrl"], "endpointUrl")
    upload_url = string_value(input_options["uploadUrl"], "uploadUrl")
    override_patch_method = bool_value(
        input_options["overridePatchMethod"],
        "overridePatchMethod",
    )

    with TusConformancePlanServer(conformance_scenario, endpoint_url) as conformance_server:
        uploader = tus.TusClient(conformance_server.endpoint_url()).uploader(
            file_stream=BytesIO(content),
            chunk_size=len(content),
            url=conformance_server.local_url(upload_url),
            override_patch_method=override_patch_method,
        )
        uploader.upload()

        if not uploader.url:
            fail("override PATCH method scenario did not expose an upload URL")
        if uploader.offset != len(content):
            fail(
                "override PATCH method upload offset {}, expected {}".format(
                    uploader.offset,
                    len(content),
                )
            )

        conformance_server.assert_exhausted()
        result = conformance_server.result()
        result["uploadUrl"] = conformance_server.canonical_url(uploader.url)
        return result


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    conformance_scenario = object_value(
        scenario["conformanceScenario"],
        "conformanceScenario",
    )
    result = upload_with_override_patch_method(conformance_scenario)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} overrode PATCH for {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
