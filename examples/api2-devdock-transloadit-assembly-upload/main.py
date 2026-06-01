"""Upload to a Transloadit devdock Assembly using tus-py-client.

This example is intentionally checked into the SDK repository. API2 owns the
scenario JSON and prepares the live Transloadit Assembly; this file only shows
ordinary tus-py-client usage against the injected TUS endpoint.
"""

import json
import os
from io import BytesIO
from pathlib import Path

from tusclient import client as tus


def fail(message):
    raise RuntimeError(message)


def load_scenario():
    configured_path = os.environ.get("API2_SDK_EXAMPLE_SCENARIO")
    scenario_path = (
        Path(configured_path) if configured_path else Path(__file__).with_name("api2-scenario.json")
    )
    with scenario_path.open(encoding="utf-8") as scenario_file:
        return json.load(scenario_file)


def read_path(value, path_parts, label):
    current = value
    for part in path_parts:
        if isinstance(current, list) and isinstance(part, int):
            if part >= len(current):
                fail("{} path {!r} index {} is out of range".format(label, path_parts, part))
            current = current[part]
            continue

        if isinstance(current, dict) and isinstance(part, str):
            if part not in current:
                fail("{} path {!r} is missing key {!r}".format(label, path_parts, part))
            current = current[part]
            continue

        fail("{} path {!r} cannot read {!r} from {!r}".format(label, path_parts, part, current))

    return current


def resolve_value(value_spec, context, label):
    if "value" in value_spec:
        return value_spec["value"]

    source = value_spec.get("source")
    if not isinstance(source, dict):
        fail("{} value spec has no literal value or source".format(label))

    root = source.get("root")
    if root not in context:
        fail("{} value source root {!r} is unavailable".format(label, root))

    path_parts = source.get("path") or []
    if not isinstance(path_parts, list):
        fail("{} value source path must be a list".format(label))

    return read_path(context[root], path_parts, label)


def scenario_bytes(upload_config):
    source = upload_config["source"]
    if source["kind"] != "bytes":
        fail("unsupported scenario source kind {!r}".format(source["kind"]))
    if source["encoding"] != "utf8":
        fail("unsupported scenario source encoding {!r}".format(source["encoding"]))
    return source["value"].encode("utf-8")


def scalar_string(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def upload_metadata(upload_config, scenario, create_response):
    context = {"createResponse": create_response, "scenario": scenario}
    metadata = {}
    for field in upload_config["metadata"]:
        metadata[field["name"]] = scalar_string(
            resolve_value(field["value"], context, field["name"])
        )
    return metadata


def upload_with_tus(scenario, create_response):
    upload_config = scenario["upload"]
    context = {"createResponse": create_response, "scenario": scenario}
    endpoint_url = scalar_string(resolve_value(upload_config["tusUrl"], context, "tusUrl"))
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
    scenario = load_scenario()
    create_response = scenario["prepared"]["createResponse"]
    upload_url = upload_with_tus(scenario, create_response)
    print(
        "Python TUS SDK devdock scenario {} uploaded to {}".format(
            scenario["scenarioId"], upload_url
        )
    )


if __name__ == "__main__":
    main()
