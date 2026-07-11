"""Prove TUS parallel partial uploads are concatenated into a final upload."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    TusConformancePlanServer,
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


def upload_with_parallel_concat(conformance_scenario):
    input_options = conformance_input_options(conformance_scenario)
    content = conformance_input_source_bytes(conformance_scenario)
    endpoint_url = string_value(input_options["endpointUrl"], "endpointUrl")
    metadata = object_value(input_options["metadata"], "metadata")
    metadata_for_partial_uploads = object_value(
        input_options["metadataForPartialUploads"],
        "metadataForPartialUploads",
    )
    parallel_uploads = int_value(input_options["parallelUploads"], "parallelUploads")
    completion = object_value(
        conformance_scenario["completion"],
        "conformanceScenario.completion",
    )
    completion_kind = string_value(
        completion["kind"],
        "conformanceScenario.completion.kind",
    )
    events = []

    with TusConformancePlanServer(conformance_scenario, endpoint_url) as conformance_server:
        client = tus.TusClient(conformance_server.endpoint_url())
        uploader = client.uploader(
            file_stream=BytesIO(content),
            metadata=metadata,
            metadata_for_partial_uploads=metadata_for_partial_uploads,
            parallel_uploads=parallel_uploads,
            on_progress=lambda bytes_sent, bytes_total: events.append(
                {
                    "bytesSent": bytes_sent,
                    "bytesTotal": bytes_total,
                    "kind": "progress",
                },
            ),
            on_chunk_complete=lambda chunk_size, bytes_accepted, bytes_total: events.append(
                {
                    "bytesAccepted": bytes_accepted,
                    "bytesTotal": bytes_total,
                    "chunkSize": chunk_size,
                    "kind": "chunk-complete",
                },
            ),
        )
        uploader.upload()

        if not uploader.url:
            fail("parallel upload concat scenario did not expose an upload URL")
        if uploader.offset != len(content):
            fail(
                "parallel upload concat scenario upload offset {}, expected {}".format(
                    uploader.offset,
                    len(content),
                )
            )

        conformance_server.assert_exhausted()
        result = conformance_server.result()
        result["completionKind"] = completion_kind
        result["errorCalled"] = False
        result["eventCount"] = len(events)
        result["events"] = events
        result["successCalled"] = True
        result["uploadUrl"] = conformance_server.canonical_url(uploader.url)
        return result


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    conformance_scenario = object_value(
        scenario["conformanceScenario"],
        "conformanceScenario",
    )
    result = upload_with_parallel_concat(conformance_scenario)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} concatenated parallel uploads into {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
