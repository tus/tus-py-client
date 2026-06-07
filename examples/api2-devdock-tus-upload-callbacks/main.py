"""Observe Transloadit devdock TUS upload callbacks."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    fail,
    load_scenario,
    match_upload_callback_event_keys,
    scenario_bytes,
    scenario_id,
    tus_url,
    upload_callback_event_key,
    upload_callback_event_key_number,
    upload_callback_event_key_total,
    upload_callbacks,
    upload_metadata,
    write_result,
)


class EventRecordingBytesIO(BytesIO):
    def __init__(self, content, callbacks, events):
        super().__init__(content)
        self.callbacks = callbacks
        self.events = events

    def close(self):
        self.events.append(
            upload_callback_event_key(
                self.callbacks,
                self.callbacks["eventKinds"]["sourceClose"],
            )
        )
        super().close()


def upload_with_callbacks(scenario, create_response):
    upload_config = scenario["upload"]
    callbacks = upload_callbacks(scenario)
    content = scenario_bytes(upload_config)
    events = []
    if upload_config["chunkSize"] != "full-file":
        fail("unsupported chunk size policy {!r}".format(upload_config["chunkSize"]))

    source = EventRecordingBytesIO(content, callbacks, events)

    def on_progress(bytes_sent, bytes_total):
        events.append(
            upload_callback_event_key(
                callbacks,
                callbacks["eventKinds"]["progress"],
                upload_callback_event_key_number(bytes_sent),
                upload_callback_event_key_total(bytes_total),
            )
        )

    def on_chunk_complete(chunk_size, bytes_accepted, bytes_total):
        events.append(
            upload_callback_event_key(
                callbacks,
                callbacks["eventKinds"]["chunkComplete"],
                upload_callback_event_key_number(chunk_size),
                upload_callback_event_key_number(bytes_accepted),
                upload_callback_event_key_total(bytes_total),
            )
        )

    uploader = tus.TusClient(tus_url(upload_config, scenario, create_response)).uploader(
        file_stream=source,
        chunk_size=len(content),
        metadata=upload_metadata(upload_config, scenario, create_response),
        retries=upload_config["retries"],
        on_progress=on_progress,
        on_chunk_complete=on_chunk_complete,
    )
    uploader.set_url(uploader.create_url())
    uploader.offset = 0
    events.append(
        upload_callback_event_key(
            callbacks,
            callbacks["eventKinds"]["uploadUrlAvailable"],
        )
    )

    uploader.upload()

    if not uploader.url:
        fail("upload callbacks TUS upload did not expose an upload URL")
    if uploader.offset != len(content):
        fail("upload callbacks upload offset {}, expected {}".format(uploader.offset, len(content)))

    events.append(upload_callback_event_key(callbacks, callbacks["eventKinds"]["success"]))
    source.close()
    matched_events = match_upload_callback_event_keys(callbacks, events)

    return {
        "eventKeys": matched_events,
        "rawEventKeys": events,
        "uploadUrl": uploader.url,
    }


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    create_response = scenario["prepared"]["createResponse"]
    result = upload_with_callbacks(scenario, create_response)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} observed upload callbacks for {}".format(
            scenario_id(scenario),
            result["uploadUrl"],
        )
    )


if __name__ == "__main__":
    main()
