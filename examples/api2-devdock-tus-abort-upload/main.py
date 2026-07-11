"""Abort a TUS upload against the API2 devdock conformance server."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus
from tusclient.exceptions import TusUploadAborted
from tusclient.fingerprint.interface import Fingerprint
from tusclient.storage.interface import Storage

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


class MemoryStorage(Storage):
    def __init__(self):
        self.values = {}

    def get_item(self, key):
        return self.values.get(key)

    def set_item(self, key, value):
        self.values[key] = value

    def remove_item(self, key):
        self.values.pop(key, None)


class FixedFingerprint(Fingerprint):
    def __init__(self, fingerprint):
        self.fingerprint = fingerprint

    def get_fingerprint(self, fs):
        return self.fingerprint


def upload_and_abort(conformance_scenario):
    input_options = conformance_input_options(conformance_scenario)
    content = conformance_input_source_bytes(conformance_scenario)
    endpoint_url = string_value(input_options["endpointUrl"], "endpointUrl")
    headers = object_value(input_options.get("headers", {}), "headers")
    metadata = object_value(input_options["metadata"], "metadata")
    override_patch_method = bool_value(
        input_options.get("overridePatchMethod", False),
        "overridePatchMethod",
    )
    runtime_setup = object_value(
        conformance_scenario["runtimeSetup"],
        "conformanceScenario.runtimeSetup",
    )
    abort_setup = object_value(
        runtime_setup["abort"],
        "conformanceScenario.runtimeSetup.abort",
    )
    terminate_upload_on_abort = bool_value(
        abort_setup["terminateUpload"],
        "conformanceScenario.runtimeSetup.abort.terminateUpload",
    )

    client_ref = {}
    uploader_ref = {}

    def on_abort_request(event):
        active_client = client_ref.get("client")
        active_uploader = uploader_ref.get("uploader")
        if active_client is None:
            fail("abort request observed before client was initialized")
        active_client.abort_upload(active_uploader, False)

    with TusConformancePlanServer(
        conformance_scenario,
        endpoint_url,
        on_abort_request=on_abort_request,
    ) as conformance_server:
        client = tus.TusClient(conformance_server.endpoint_url(), headers=headers)
        client_ref["client"] = client

        storage = None
        fingerprint = input_options.get("fingerprint")
        uploader_options = {}
        if fingerprint is not None:
            storage = MemoryStorage()
            uploader_options.update(
                {
                    "fingerprinter": FixedFingerprint(
                        string_value(fingerprint, "fingerprint"),
                    ),
                    "store_url": True,
                    "url_storage": storage,
                }
            )

        uploader = client.uploader(
            file_stream=BytesIO(content),
            chunk_size=len(content),
            metadata=metadata,
            override_patch_method=override_patch_method,
            **uploader_options,
        )
        uploader_ref["uploader"] = uploader

        try:
            uploader.upload()
        except TusUploadAborted:
            pass
        else:
            fail("abort scenario completed without TusUploadAborted")

        if terminate_upload_on_abort:
            if not uploader.url:
                fail("abort scenario requested termination before upload URL was known")
            client.abort_upload(uploader, True)

        conformance_server.assert_exhausted()
        result = conformance_server.result()
        result["completionKind"] = "aborted"
        result["errorCalled"] = False
        result["successCalled"] = False
        result["uploadUrl"] = (
            conformance_server.canonical_url(uploader.url) if uploader.url else None
        )
        if storage is not None and fingerprint is not None:
            result["storedUrlAfterAbort"] = storage.get_item(fingerprint)
        return result


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    conformance_scenario = object_value(
        scenario["conformanceScenario"],
        "conformanceScenario",
    )
    result = upload_and_abort(conformance_scenario)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} aborted the upload".format(
            scenario_id(scenario),
        )
    )


if __name__ == "__main__":
    main()
