from tusclient.protocol_generated import (
    START_VALIDATION_CLIENT_FLOW_VALUES,
    START_VALIDATION_MESSAGES,
    START_VALIDATION_RULES,
    TUS_SUPPORTED_PROTOCOLS,
)


def validate_upload_start(
    file_path=None,
    file_stream=None,
    client=None,
    url=None,
    upload_size=None,
    upload_data_during_creation=False,
    upload_length_deferred=False,
    parallel_uploads=None,
    parallel_upload_boundaries=None,
    protocol=None,
    retry_delays=None,
):
    input_values = {
        "hasCurrentUrl": url is not None,
        "hasEndpoint": client is not None and getattr(client, "url", None) is not None,
        "hasFile": file_path is not None or file_stream is not None,
        "hasUploadSize": upload_size is not None,
        "hasUploadUrl": url is not None,
        "parallelUploadBoundariesCount": (
            len(parallel_upload_boundaries)
            if parallel_upload_boundaries is not None
            else None
        ),
        "parallelUploads": _default_parallel_uploads(parallel_uploads),
        "protocol": _default_protocol(protocol),
        "retryDelays": retry_delays,
        "uploadDataDuringCreation": upload_data_during_creation,
        "uploadLengthDeferred": upload_length_deferred,
    }

    for rule in START_VALIDATION_RULES:
        if _evaluate_predicate(rule["predicate"], input_values):
            return {
                "message": _resolve_message(rule["message"], input_values),
                "ok": False,
                "reason": rule["reason"],
            }

    return {"ok": True}


def validate_upload_start_or_raise(**kwargs):
    validation = validate_upload_start(**kwargs)
    if validation["ok"]:
        return validation

    raise ValueError(validation["message"])


def _default_parallel_uploads(value):
    if value is not None:
        return value

    return START_VALIDATION_CLIENT_FLOW_VALUES["minimumParallelUploads"] - 1


def _default_protocol(value):
    if value is not None:
        return value

    return TUS_SUPPORTED_PROTOCOLS[0]


def _evaluate_predicate(predicate, input_values):
    kind = predicate["kind"]

    if kind == "all":
        return all(
            _evaluate_predicate(child, input_values)
            for child in predicate.get("predicates", [])
        )

    if kind == "any":
        return any(
            _evaluate_predicate(child, input_values)
            for child in predicate.get("predicates", [])
        )

    if kind == "array-or-null":
        value = input_values[predicate["input"]]
        result = value is None or isinstance(value, list)
        return result == predicate["equals"]

    if kind == "boolean-input":
        return bool(input_values[predicate["input"]]) == predicate["equals"]

    if kind == "not":
        return not _evaluate_predicate(predicate["predicate"], input_values)

    if kind == "number-input-gte-client-flow-value":
        return _number_input(input_values, predicate["input"]) >= _client_flow_value(
            predicate["value"]
        )

    if kind == "number-input-lt-client-flow-value":
        return _number_input(input_values, predicate["input"]) < _client_flow_value(
            predicate["value"]
        )

    if kind == "number-input-not-equals-number-input":
        return _number_input(input_values, predicate["left"]) != _number_input(
            input_values,
            predicate["right"],
        )

    if kind == "number-input-not-null":
        return input_values[predicate["input"]] is not None

    if kind == "supported-protocol":
        result = input_values[predicate["input"]] in TUS_SUPPORTED_PROTOCOLS
        return result == predicate["equals"]

    raise ValueError("Unsupported generated start validation predicate {}".format(kind))


def _client_flow_value(name):
    return START_VALIDATION_CLIENT_FLOW_VALUES[name]


def _number_input(input_values, name):
    value = input_values[name]
    if value is None:
        return 0

    return value


def _resolve_message(message, input_values):
    template = START_VALIDATION_MESSAGES[message["key"]]
    if message["kind"] == "client-flow-message":
        return template

    if message["kind"] == "client-flow-message-with-input-suffix":
        return "{}{}".format(template, input_values[message["input"]])

    raise ValueError(
        "Unsupported generated start validation message {}".format(message["kind"])
    )
