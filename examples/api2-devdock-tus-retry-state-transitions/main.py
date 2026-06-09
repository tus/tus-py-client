"""Prove TUS retry attempt state resets after recovered progress."""

import sys
from io import BytesIO
from pathlib import Path

from tusclient import client as tus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api2devdock import (
    TusConformancePlanServer,
    conformance_input_options,
    conformance_input_source_bytes,
    conformance_retry_decisions,
    fail,
    int_array_value,
    load_scenario,
    object_value,
    scenario_id,
    string_value,
    write_result,
)


class RetryStateObserver:
    def __init__(self, retry_decisions, retry_delays):
        self.retry_decisions = retry_decisions
        self.retry_delays = retry_delays
        self.events = []
        self.index = 0

    def on_should_retry(self, error, retry_attempt):
        if self.index >= len(self.retry_decisions):
            fail(
                "retry state scenario observed unexpected retry attempt {}".format(
                    retry_attempt,
                )
            )

        expected = self.retry_decisions[self.index]
        if retry_attempt != expected["retryAttempt"]:
            fail(
                "retry state scenario expected retry attempt {}, got {}".format(
                    expected["retryAttempt"],
                    retry_attempt,
                )
            )

        decision = expected["decision"]
        self.events.append(
            {
                "decision": decision,
                "kind": "should-retry",
                "retryAttempt": retry_attempt,
            }
        )

        if decision:
            if retry_attempt >= len(self.retry_delays):
                fail(
                    "retry state scenario has no delay for retry attempt {}".format(
                        retry_attempt,
                    )
                )
            self.events.append(
                {
                    "delay": self.retry_delays[retry_attempt],
                    "kind": "retry-schedule",
                }
            )

        self.index += 1
        return decision

    def assert_complete(self):
        if self.index == len(self.retry_decisions):
            return

        fail(
            "retry state scenario observed {} retry decision(s), expected {}".format(
                self.index,
                len(self.retry_decisions),
            )
        )


def upload_with_retry_state_transitions(conformance_scenario):
    input_options = conformance_input_options(conformance_scenario)
    content = conformance_input_source_bytes(conformance_scenario)
    endpoint_url = string_value(input_options["endpointUrl"], "endpointUrl")
    metadata = object_value(input_options["metadata"], "metadata")
    retry_delays = int_array_value(input_options["retryDelays"], "retryDelays")
    retry_decisions = conformance_retry_decisions(conformance_scenario)
    completion = object_value(
        conformance_scenario["completion"],
        "conformanceScenario.completion",
    )
    completion_kind = string_value(
        completion["kind"],
        "conformanceScenario.completion.kind",
    )
    observer = RetryStateObserver(retry_decisions, retry_delays)

    with TusConformancePlanServer(conformance_scenario, endpoint_url) as conformance_server:
        client = tus.TusClient(conformance_server.endpoint_url())
        uploader = client.uploader(
            file_stream=BytesIO(content),
            metadata=metadata,
            on_should_retry=observer.on_should_retry,
            retry_delays=retry_delays,
        )
        uploader.upload()
        observer.assert_complete()

        if not uploader.url:
            fail("retry state scenario did not expose an upload URL")
        if uploader.offset != len(content):
            fail(
                "retry state scenario upload offset {}, expected {}".format(
                    uploader.offset,
                    len(content),
                )
            )

        conformance_server.assert_exhausted()
        result = conformance_server.result()
        result["completionKind"] = completion_kind
        result["errorCalled"] = False
        result["eventCount"] = len(observer.events)
        result["events"] = observer.events
        result["successCalled"] = True
        result["uploadUrl"] = conformance_server.canonical_url(uploader.url)
        return result


def main():
    scenario = load_scenario(Path(__file__).with_name("api2-scenario.json"))
    conformance_scenario = object_value(
        scenario["conformanceScenario"],
        "conformanceScenario",
    )
    result = upload_with_retry_state_transitions(conformance_scenario)
    write_result(result)
    print(
        "Python TUS SDK devdock scenario {} proved retry state transitions".format(
            scenario_id(scenario),
        )
    )


if __name__ == "__main__":
    main()
