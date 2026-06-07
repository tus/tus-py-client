"""Shared helpers for API2 devdock examples."""

import json
import os
from pathlib import Path


def fail(message):
    raise RuntimeError(message)


def load_scenario(default_path):
    configured_path = os.environ.get("API2_SDK_EXAMPLE_SCENARIO")
    scenario_path = Path(configured_path) if configured_path else Path(default_path)
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


def object_value(value, label):
    if not isinstance(value, dict):
        fail("{} must be an object".format(label))
    return value


def string_value(value, label):
    if not isinstance(value, str):
        fail("{} must be a string".format(label))
    return value


def int_value(value, label):
    if not isinstance(value, int) or isinstance(value, bool):
        fail("{} must be an integer".format(label))
    return value


def string_array_value(value, label):
    if not isinstance(value, list):
        fail("{} must be a list".format(label))
    for index, item in enumerate(value):
        string_value(item, "{}[{}]".format(label, index))
    return value


def int_array_value(value, label):
    if not isinstance(value, list):
        fail("{} must be a list".format(label))
    for index, item in enumerate(value):
        int_value(item, "{}[{}]".format(label, index))
    return value


def string_array_array_value(value, label):
    if not isinstance(value, list):
        fail("{} must be a list".format(label))
    for index, item in enumerate(value):
        string_array_value(item, "{}[{}]".format(label, index))
    return value


def string_map_value(value, label):
    if not isinstance(value, dict):
        fail("{} must be an object".format(label))
    for key, item in value.items():
        string_value(key, "{} key".format(label))
        string_value(item, "{}.{}".format(label, key))
    return value


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


def fixed_chunk_size_bytes(scenario):
    upload = object_value(scenario["upload"], "upload")
    chunk_size = object_value(upload["chunkSize"], "upload.chunkSize")
    kind = string_value(chunk_size["kind"], "upload.chunkSize.kind")
    if kind != "fixed-bytes":
        fail("unsupported chunk size kind {!r}".format(kind))
    bytes_value = int_value(chunk_size["bytes"], "upload.chunkSize.bytes")
    if bytes_value <= 0:
        fail("upload.chunkSize.bytes must be positive")
    return bytes_value


def retry_offset_recovery(scenario):
    upload = object_value(scenario["upload"], "upload")
    retry = object_value(upload["retryOffsetRecovery"], "upload.retryOffsetRecovery")
    fail_after_response = object_value(
        retry["failAfterResponse"],
        "upload.retryOffsetRecovery.failAfterResponse",
    )
    recovery_response = object_value(
        retry["recoveryResponse"],
        "upload.retryOffsetRecovery.recoveryResponse",
    )
    return {
        "expectedFailureCount": int_value(
            retry["expectedFailureCount"],
            "upload.retryOffsetRecovery.expectedFailureCount",
        ),
        "expectedRecoveredOffset": int_value(
            retry["expectedRecoveredOffset"],
            "upload.retryOffsetRecovery.expectedRecoveredOffset",
        ),
        "expectedRecoveryRequestCount": int_value(
            retry["expectedRecoveryRequestCount"],
            "upload.retryOffsetRecovery.expectedRecoveryRequestCount",
        ),
        "expectedRequestMethods": string_array_value(
            retry["expectedRequestMethods"],
            "upload.retryOffsetRecovery.expectedRequestMethods",
        ),
        "failAfterResponse": {
            "message": string_value(
                fail_after_response["message"],
                "upload.retryOffsetRecovery.failAfterResponse.message",
            ),
            "method": string_value(
                fail_after_response["method"],
                "upload.retryOffsetRecovery.failAfterResponse.method",
            ),
            "occurrence": int_value(
                fail_after_response["occurrence"],
                "upload.retryOffsetRecovery.failAfterResponse.occurrence",
            ),
        },
        "recoveryResponse": {
            "method": string_value(
                recovery_response["method"],
                "upload.retryOffsetRecovery.recoveryResponse.method",
            ),
            "offsetHeader": string_value(
                recovery_response["offsetHeader"],
                "upload.retryOffsetRecovery.recoveryResponse.offsetHeader",
            ),
        },
    }


def request_lifecycle_hooks(scenario):
    upload = object_value(scenario["upload"], "upload")
    hooks = object_value(upload["requestLifecycleHooks"], "upload.requestLifecycleHooks")
    return {
        "expectedAfterResponseMethods": string_array_value(
            hooks["expectedAfterResponseMethods"],
            "upload.requestLifecycleHooks.expectedAfterResponseMethods",
        ),
        "expectedAfterResponseStatusCodes": int_array_value(
            hooks["expectedAfterResponseStatusCodes"],
            "upload.requestLifecycleHooks.expectedAfterResponseStatusCodes",
        ),
        "expectedBeforeRequestMethods": string_array_value(
            hooks["expectedBeforeRequestMethods"],
            "upload.requestLifecycleHooks.expectedBeforeRequestMethods",
        ),
    }


def upload_headers(scenario):
    upload = object_value(scenario["upload"], "upload")
    return string_map_value(upload["headers"], "upload.headers")


def upload_callbacks(scenario):
    upload = object_value(scenario["upload"], "upload")
    callbacks = object_value(upload["uploadCallbacks"], "upload.uploadCallbacks")
    event_kinds = object_value(
        callbacks["eventKinds"],
        "upload.uploadCallbacks.eventKinds",
    )
    return {
        "allowedExtraEventKeyPrefixes": string_array_value(
            callbacks["allowedExtraEventKeyPrefixes"],
            "upload.uploadCallbacks.allowedExtraEventKeyPrefixes",
        ),
        "eventKeyAlternativeGroups": string_array_array_value(
            callbacks["eventKeyAlternativeGroups"],
            "upload.uploadCallbacks.eventKeyAlternativeGroups",
        ),
        "eventKinds": {
            "chunkComplete": string_value(
                event_kinds["chunkComplete"],
                "upload.uploadCallbacks.eventKinds.chunkComplete",
            ),
            "progress": string_value(
                event_kinds["progress"],
                "upload.uploadCallbacks.eventKinds.progress",
            ),
            "sourceClose": string_value(
                event_kinds["sourceClose"],
                "upload.uploadCallbacks.eventKinds.sourceClose",
            ),
            "success": string_value(
                event_kinds["success"],
                "upload.uploadCallbacks.eventKinds.success",
            ),
            "uploadUrlAvailable": string_value(
                event_kinds["uploadUrlAvailable"],
                "upload.uploadCallbacks.eventKinds.uploadUrlAvailable",
            ),
        },
        "eventKeyPartSeparator": string_value(
            callbacks["eventKeyPartSeparator"],
            "upload.uploadCallbacks.eventKeyPartSeparator",
        ),
        "eventKeys": string_array_value(
            callbacks["eventKeys"],
            "upload.uploadCallbacks.eventKeys",
        ),
        "eventPolicyMatching": string_value(
            callbacks["eventPolicyMatching"],
            "upload.uploadCallbacks.eventPolicyMatching",
        ),
    }


def upload_callback_event_key(callbacks, *parts):
    return callbacks["eventKeyPartSeparator"].join(parts)


def upload_callback_event_key_number(value):
    return str(value)


def upload_callback_event_key_total(value):
    return scalar_string(value)


def upload_callback_event_matches_expected(callbacks, expected_index, actual):
    if actual == callbacks["eventKeys"][expected_index]:
        return True

    if expected_index >= len(callbacks["eventKeyAlternativeGroups"]):
        return False

    return actual in callbacks["eventKeyAlternativeGroups"][expected_index]


def has_allowed_upload_callback_extra_event_prefix(callbacks, event):
    for prefix in callbacks["allowedExtraEventKeyPrefixes"]:
        if event.startswith(prefix):
            return True

    return False


def match_upload_callback_event_keys(callbacks, actual):
    policy = callbacks["eventPolicyMatching"]
    if policy not in ("exact", "exact-except-allowed-extra-events"):
        fail("unsupported upload callback event policy {!r}".format(policy))

    expected_index = 0
    matched = []
    for event in actual:
        if expected_index < len(callbacks["eventKeys"]) and upload_callback_event_matches_expected(
            callbacks,
            expected_index,
            event,
        ):
            matched.append(callbacks["eventKeys"][expected_index])
            expected_index += 1
            continue

        if policy == "exact-except-allowed-extra-events" and has_allowed_upload_callback_extra_event_prefix(
            callbacks,
            event,
        ):
            continue

        fail(
            "upload callback events emitted unexpected extra event {!r}; allowed prefixes {}; expected {}, got {}".format(
                event,
                callbacks["allowedExtraEventKeyPrefixes"],
                callbacks["eventKeys"],
                actual,
            )
        )

    if expected_index != len(callbacks["eventKeys"]):
        fail(
            "upload callback events did not emit every expected non-extra event; expected {}, got {}".format(
                callbacks["eventKeys"],
                actual,
            )
        )

    return matched


def scenario_id(scenario):
    return string_value(scenario["scenarioId"], "scenarioId")


def scalar_string(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def tus_url(upload_config, scenario, create_response):
    context = {"createResponse": create_response, "scenario": scenario}
    return scalar_string(resolve_value(upload_config["tusUrl"], context, "tusUrl"))


def upload_metadata(upload_config, scenario, create_response):
    context = {"createResponse": create_response, "scenario": scenario}
    metadata = {}
    for field in upload_config["metadata"]:
        metadata[field["name"]] = scalar_string(
            resolve_value(field["value"], context, field["name"])
        )
    return metadata


def write_result(result):
    result_path = os.environ.get("API2_SDK_EXAMPLE_RESULT")
    if not result_path:
        return

    with Path(result_path).open("w", encoding="utf-8") as result_file:
        json.dump(result, result_file, indent=2)
        result_file.write("\n")
