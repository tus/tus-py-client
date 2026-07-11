"""Read a path-backed source as a TUS upload input."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    TusConformancePlanServer,
    conformance_input_options,
    conformance_input_source_bytes,
    conformance_input_source_kind,
    conformance_scenario_wants_event,
    fail,
    load_scenario,
    object_value,
    scenario_id,
    write_result,
)


def append_source_open_event(events, conformance_scenario, input_kind, size):
    if not conformance_scenario_wants_event(conformance_scenario, "source-open"):
        return events

    return events + [
        {
            "inputKind": input_kind,
            "kind": "source-open",
            "size": size,
        }
    ]


def append_source_close_event(events, conformance_scenario):
    if not conformance_scenario_wants_event(conformance_scenario, "source-close"):
        return events

    return events + [{"kind": "source-close"}]


def append_success_event(events, conformance_scenario):
    if not conformance_scenario_wants_event(conformance_scenario, "success"):
        return events

    return events + [{"kind": "success"}]


def upload_with_node_path_input_source(conformance_scenario):
    input_options = conformance_input_options(conformance_scenario)
    content = conformance_input_source_bytes(conformance_scenario)
    input_kind = conformance_input_source_kind(conformance_scenario)
    endpoint_url = input_options["endpointUrl"]
    events = []

    with TemporaryDirectory(prefix="api2-python-tus-node-path-input-source-") as tmp_dir:
        input_path = Path(tmp_dir) / "input.txt"
        input_path.write_bytes(content)
        events = append_source_open_event(
            events,
            conformance_scenario,
            input_kind,
            len(content),
        )

        with TusConformancePlanServer(conformance_scenario, endpoint_url) as conformance_server:
            uploader = tus.TusClient(conformance_server.endpoint_url()).uploader(
                chunk_size=len(content),
                file_path=str(input_path),
                metadata=object_value(input_options["metadata"], "metadata"),
            )
            uploader.upload()
            events = append_success_event(events, conformance_scenario)

            if not uploader.url:
                fail("node-path TUS upload did not expose an upload URL")
            if uploader.offset != len(content):
                fail(
                    "node-path TUS upload offset {}, expected {}".format(
                        uploader.offset,
                        len(content),
                    )
                )

            events = append_source_close_event(events, conformance_scenario)
            conformance_server.assert_exhausted()
            result = conformance_server.result()
            result["events"] = events
            result["inputKind"] = input_kind
            result["uploadUrl"] = conformance_server.canonical_url(uploader.url)
            return result


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    conformance_scenario = object_value(
        scenario["conformanceScenario"],
        "conformanceScenario",
    )
    result = upload_with_node_path_input_source(conformance_scenario)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} read {} for {}".format(
            scenario_id(scenario),
            result["inputKind"],
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
