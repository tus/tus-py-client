"""Resume a Transloadit devdock TUS upload using tus-py-client."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus
from tusclient.fingerprint.interface import Fingerprint
from tusclient.storage.interface import Storage

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import fail, load_scenario, scenario_bytes, tus_url, upload_metadata, write_result


class StaticFingerprint(Fingerprint):
    def __init__(self, value):
        self.value = value

    def get_fingerprint(self, fs):
        return self.value


class MemoryStorage(Storage):
    def __init__(self):
        self.urls = {}

    def get_item(self, key):
        return self.urls.get(key)

    def set_item(self, key, value):
        self.urls[key] = value

    def remove_item(self, key):
        self.urls.pop(key, None)

    def count(self):
        return len(self.urls)


def uploader_for(scenario, create_response, content, storage):
    upload_config = scenario["upload"]
    resume = upload_config["resume"]
    return tus.TusClient(tus_url(upload_config, scenario, create_response)).uploader(
        file_stream=BytesIO(content),
        chunk_size=len(content),
        metadata=upload_metadata(upload_config, scenario, create_response),
        store_url=True,
        remove_fingerprint_on_success=resume["removeFingerprintOnSuccess"],
        url_storage=storage,
        fingerprinter=StaticFingerprint(resume["fingerprint"]),
        retries=upload_config["retries"],
    )


def upload_first_chunk_and_pause(scenario, create_response, content, storage):
    upload_config = scenario["upload"]
    resume = upload_config["resume"]
    chunk_size = upload_config["chunkSize"]
    if chunk_size["kind"] != "fixed-bytes":
        fail("unsupported chunk size policy {!r}".format(chunk_size["kind"]))

    uploader = uploader_for(scenario, create_response, content, storage)
    uploader.chunk_size = chunk_size["bytes"]
    uploader.upload(stop_at=resume["stopAfterAcceptedBytes"])

    if uploader.offset != resume["stopAfterAcceptedBytes"]:
        fail(
            "first upload accepted {}, expected {}".format(
                uploader.offset,
                resume["stopAfterAcceptedBytes"],
            )
        )
    if not uploader.url:
        fail("first TUS upload did not expose an upload URL")

    return uploader.url


def resume_stored_upload(scenario, create_response, content, storage):
    upload_config = scenario["upload"]
    uploader = uploader_for(scenario, create_response, content, storage)
    uploader.chunk_size = len(content)
    uploader.upload()

    if not uploader.url:
        fail("resumed TUS upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail("resumed TUS upload offset {}, expected {}".format(uploader.offset, len(content)))

    return uploader.url


def upload_with_stored_resume(scenario, create_response):
    upload_config = scenario["upload"]
    resume = upload_config["resume"]
    content = scenario_bytes(upload_config)
    storage = MemoryStorage()

    first_upload_url = upload_first_chunk_and_pause(scenario, create_response, content, storage)
    previous_upload_count = storage.count()
    if previous_upload_count != resume["expectedPreviousUploadCount"]:
        fail(
            "stored upload count {}, expected {}".format(
                previous_upload_count,
                resume["expectedPreviousUploadCount"],
            )
        )

    upload_url = resume_stored_upload(scenario, create_response, content, storage)
    if upload_url != first_upload_url:
        fail("resumed upload URL {}, expected {}".format(upload_url, first_upload_url))

    remaining_previous_upload_count = storage.count()
    if remaining_previous_upload_count != resume["expectedRemainingPreviousUploadCount"]:
        fail(
            "remaining stored upload count {}, expected {}".format(
                remaining_previous_upload_count,
                resume["expectedRemainingPreviousUploadCount"],
            )
        )

    return {
        "firstUploadUrl": first_upload_url,
        "previousUploadCount": previous_upload_count,
        "remainingPreviousUploadCount": remaining_previous_upload_count,
        "uploadUrl": upload_url,
    }


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    result = upload_with_stored_resume(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} resumed {}".format(
            scenario["scenarioId"],
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
