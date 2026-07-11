"""Select a generated TUS protocol mode for a conformance upload."""

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


def upload_with_protocol_version_selection(conformance_scenario):
    input_options = conformance_input_options(conformance_scenario)
    content = conformance_input_source_bytes(conformance_scenario)
    endpoint_url = string_value(input_options["endpointUrl"], "endpointUrl")
    metadata = object_value(input_options["metadata"], "metadata")
    protocol = string_value(input_options["protocol"], "protocol")
    upload_data_during_creation = bool_value(
        input_options["uploadDataDuringCreation"],
        "uploadDataDuringCreation",
    )
    if not upload_data_during_creation:
        fail("Python protocol-version proof expects creation with upload")

    completion = object_value(conformance_scenario["completion"], "completion")

    with TusConformancePlanServer(conformance_scenario, endpoint_url) as conformance_server:
        uploader = tus.TusClient(conformance_server.endpoint_url()).create_upload_with_data(
            len(content),
            file_stream=BytesIO(content),
            chunk_size=len(content),
            metadata=metadata,
            protocol=protocol,
        )

        if not uploader.url:
            fail("protocol-version scenario did not expose an upload URL")
        if uploader.offset != len(content):
            fail(
                "protocol-version upload offset {}, expected {}".format(
                    uploader.offset,
                    len(content),
                )
            )

        conformance_server.assert_exhausted()
        result = conformance_server.result()
        result["completionKind"] = string_value(completion["kind"], "completion.kind")
        result["errorCalled"] = False
        result["successCalled"] = True
        result["uploadUrl"] = conformance_server.canonical_url(uploader.url)
        return result


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    conformance_scenario = object_value(
        scenario["conformanceScenario"],
        "conformanceScenario",
    )
    result = upload_with_protocol_version_selection(conformance_scenario)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} selected protocol for {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
