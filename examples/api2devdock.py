"""Shared helpers for API2 devdock examples."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse, urlunparse


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


def bool_value(value, label):
    if not isinstance(value, bool):
        fail("{} must be a boolean".format(label))
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


def conformance_input_options(conformance_scenario):
    entries = conformance_scenario["inputOptionEntries"]
    if not isinstance(entries, list):
        fail("conformanceScenario.inputOptionEntries must be a list")

    result = {}
    for index, entry in enumerate(entries):
        option = object_value(
            entry,
            "conformanceScenario.inputOptionEntries[{}]".format(index),
        )
        key = string_value(
            option["key"],
            "conformanceScenario.inputOptionEntries[{}].key".format(index),
        )
        result[key] = option["value"]

    return result


def conformance_input_source_bytes(conformance_scenario):
    input_source = object_value(
        conformance_scenario["inputSource"],
        "conformanceScenario.inputSource",
    )
    kind = string_value(input_source["kind"], "conformanceScenario.inputSource.kind")
    if kind not in ("blob", "node-path-reference"):
        fail("unsupported conformance input source kind {!r}".format(kind))

    return string_value(
        input_source["content"],
        "conformanceScenario.inputSource.content",
    ).encode("utf-8")


def conformance_input_source_kind(conformance_scenario):
    input_source = object_value(
        conformance_scenario["inputSource"],
        "conformanceScenario.inputSource",
    )
    return string_value(input_source["kind"], "conformanceScenario.inputSource.kind")


def conformance_scenario_wants_event(conformance_scenario, event_kind):
    events = conformance_scenario.get("events", [])
    if not isinstance(events, list):
        fail("conformanceScenario.events must be a list")

    for index, event in enumerate(events):
        event = object_value(event, "conformanceScenario.events[{}]".format(index))
        kind = string_value(
            event["kind"],
            "conformanceScenario.events[{}].kind".format(index),
        )
        if kind == event_kind:
            return True

    return False


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


def upload_body_headers_by_method(scenario):
    upload = object_value(scenario["upload"], "upload")
    body_headers_by_method = object_value(
        upload["bodyHeadersByMethod"],
        "upload.bodyHeadersByMethod",
    )
    result = {}
    for method, headers in body_headers_by_method.items():
        string_value(method, "upload.bodyHeadersByMethod key")
        result[method] = string_map_value(
            headers,
            "upload.bodyHeadersByMethod.{}".format(method),
        )
    return result


def upload_add_request_id(scenario):
    upload = object_value(scenario["upload"], "upload")
    value = upload["addRequestId"]
    if not isinstance(value, bool):
        fail("upload.addRequestId must be a boolean")
    return value


def upload_request_id_header_name(scenario):
    upload = object_value(scenario["upload"], "upload")
    return string_value(upload["requestIdHeaderName"], "upload.requestIdHeaderName")


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


def termination(scenario):
    upload = object_value(scenario["upload"], "upload")
    termination_config = object_value(upload["termination"], "upload.termination")
    return {
        "expectedVerificationStatus": int_value(
            termination_config["expectedVerificationStatus"],
            "upload.termination.expectedVerificationStatus",
        ),
        "method": string_value(
            termination_config["method"],
            "upload.termination.method",
        ),
        "minimumDeleteRequestCount": int_value(
            termination_config["minimumDeleteRequestCount"],
            "upload.termination.minimumDeleteRequestCount",
        ),
        "stopAfterAcceptedBytes": int_value(
            termination_config["stopAfterAcceptedBytes"],
            "upload.termination.stopAfterAcceptedBytes",
        ),
        "verificationMethod": string_value(
            termination_config["verificationMethod"],
            "upload.termination.verificationMethod",
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


class TusConformancePlanServer:
    def __init__(self, conformance_scenario, endpoint_origin, on_abort_request=None):
        self.endpoint_origin = urlparse(string_value(endpoint_origin, "endpointOrigin"))
        if not self.endpoint_origin.scheme or not self.endpoint_origin.netloc:
            fail("endpointOrigin must be an absolute URL")

        self.on_abort_request = on_abort_request
        self.input_source_content = conformance_input_source_bytes(conformance_scenario)
        requests = conformance_scenario["requests"]
        if not isinstance(requests, list):
            fail("conformanceScenario.requests must be a list")
        self.requests = requests
        self.errors = []
        self.events = []
        self.observed = [None] * len(requests)
        self.observed_count = 0
        self.next_request_index = 0
        self.httpd = HTTPServer(("127.0.0.1", 0), self._handler_class())
        self.thread = Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)

    def endpoint_url(self):
        return self.local_url(urlunparse(self.endpoint_origin))

    def local_url(self, canonical_url):
        parsed = urlparse(canonical_url)
        if (
            parsed.scheme != self.endpoint_origin.scheme
            or parsed.netloc != self.endpoint_origin.netloc
        ):
            return canonical_url

        server_origin = self._server_origin()
        return urlunparse(
            (
                server_origin.scheme,
                server_origin.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    def canonical_url(self, actual_url):
        parsed = urlparse(actual_url)
        server_origin = self._server_origin()
        if parsed.scheme != server_origin.scheme or parsed.netloc != server_origin.netloc:
            return actual_url

        return urlunparse(
            (
                self.endpoint_origin.scheme,
                self.endpoint_origin.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    def local_value(self, value):
        return string_value(value, "value").replace(
            self._origin_string(self.endpoint_origin),
            self._origin_string(self._server_origin()),
        )

    def canonical_value(self, value):
        return string_value(value, "value").replace(
            self._origin_string(self._server_origin()),
            self._origin_string(self.endpoint_origin),
        )

    def assert_exhausted(self):
        self.assert_no_errors()
        if self.observed_count == len(self.requests):
            return

        fail(
            "expected {} conformance request(s), got {}".format(
                len(self.requests),
                self.observed_count,
            )
        )

    def assert_no_errors(self):
        if self.errors:
            fail("; ".join(self.errors))

    def result(self):
        self.assert_no_errors()
        observed = [request for request in self.observed if request is not None]
        return {
            "absentHeaderPresence": [
                request["absentHeaderPresence"] for request in observed
            ],
            "events": self.events,
            "requestBodySizes": [request["bodySize"] for request in observed],
            "requestBodyStarts": [request["bodyStart"] for request in observed],
            "requestCount": self.observed_count,
            "requestHeaders": [request["headers"] for request in observed],
            "requestMethods": [request["method"] for request in observed],
            "requestUrls": [request["url"] for request in observed],
        }

    def _handler_class(self):
        conformance_server = self

        class TusConformanceRequestHandler(BaseHTTPRequestHandler):
            def do_HEAD(self):
                self._handle_conformance_request()

            def do_PATCH(self):
                self._handle_conformance_request()

            def do_POST(self):
                self._handle_conformance_request()

            def do_DELETE(self):
                self._handle_conformance_request()

            def log_message(self, format, *args):
                return

            def _handle_conformance_request(self):
                content_length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(content_length) if content_length > 0 else b""
                try:
                    request_plan = conformance_server.observe_request(self, body)
                    if request_plan.get("abort", False):
                        conformance_server.abort_request(conformance_server.observed_count - 1)
                        self.close_connection = True
                        return
                    conformance_server.write_response(self, request_plan)
                except Exception as error:
                    conformance_server.errors.append(str(error))
                    response_body = str(error).encode("utf-8")
                    self.send_response(500)
                    self.send_header("Content-Length", str(len(response_body)))
                    self.end_headers()
                    self.wfile.write(response_body)

        return TusConformanceRequestHandler

    def observe_request(self, handler, body):
        if self.next_request_index >= len(self.requests):
            fail("unexpected request {} {}".format(handler.command, handler.path))

        request_plan = object_value(
            self.requests[self.next_request_index],
            "conformanceScenario.requests[{}]".format(self.next_request_index),
        )
        actual_url = self.canonical_url(self._request_url(handler))
        self.assert_request_matches_plan(
            self.next_request_index,
            request_plan,
            handler.command,
            actual_url,
            body,
        )
        self.assert_request_body_content(self.next_request_index, request_plan, body)
        self.assert_absent_headers(self.next_request_index, request_plan, handler.headers)
        expected_headers = object_value(
            request_plan["effectiveHeaders"],
            "conformanceScenario.requests[{}].effectiveHeaders".format(
                self.next_request_index,
            ),
        )
        self.assert_headers(self.next_request_index, expected_headers, handler.headers)

        self.observed[self.next_request_index] = {
            "absentHeaderPresence": self.captured_absent_header_presence(
                request_plan,
                handler.headers,
            ),
            "bodySize": None if request_plan.get("bodySize") is None else len(body),
            "bodyStart": request_plan.get("bodyStart"),
            "headers": self.captured_headers(expected_headers, handler.headers),
            "method": handler.command,
            "url": actual_url,
        }
        self.observed_count += 1
        self.next_request_index += 1
        return request_plan

    def abort_request(self, request_index):
        observed = self.observed[request_index]
        event = {
            "kind": "request-abort",
            "method": observed["method"],
            "requestIndex": request_index,
            "url": observed["url"],
        }
        self.events.append(event)
        if self.on_abort_request is not None:
            self.on_abort_request(event)

    def assert_request_matches_plan(self, request_index, request_plan, method, actual_url, body):
        expected_method = string_value(
            request_plan["effectiveMethod"],
            "conformanceScenario.requests[{}].effectiveMethod".format(request_index),
        )
        expected_url = string_value(
            request_plan["expectedUrl"],
            "conformanceScenario.requests[{}].expectedUrl".format(request_index),
        )
        if method != expected_method:
            fail(
                "request {} expected method {}, got {}".format(
                    request_index,
                    expected_method,
                    method,
                )
            )
        if actual_url != expected_url:
            fail(
                "request {} expected URL {}, got {}".format(
                    request_index,
                    expected_url,
                    actual_url,
                )
            )
        body_size = request_plan.get("bodySize")
        if body_size is not None and len(body) != body_size:
            fail(
                "request {} expected body size {}, got {}".format(
                    request_index,
                    body_size,
                    len(body),
                )
            )

    def assert_request_body_content(self, request_index, request_plan, body):
        body_start = request_plan.get("bodyStart")
        if body_start is None:
            return

        expected = self.input_source_content[body_start : body_start + len(body)]
        if body != expected:
            fail("request {} body did not match input source slice".format(request_index))

    def assert_absent_headers(self, request_index, request_plan, actual_headers):
        normalized_headers = self._normalized_headers(actual_headers)
        for name in request_plan["absentHeaders"]:
            if name.lower() not in normalized_headers:
                continue

            fail("request {} expected header {} to be absent".format(request_index, name))

    def assert_headers(self, request_index, expected_headers, actual_headers):
        normalized_headers = self._normalized_headers(actual_headers)
        for name, expected_value in expected_headers.items():
            actual_value = normalized_headers.get(name.lower())
            local_expected_value = self.local_value(expected_value)
            if actual_value == local_expected_value:
                continue

            fail(
                "request {} expected header {}={!r}, got {!r}".format(
                    request_index,
                    name,
                    local_expected_value,
                    actual_value,
                )
            )

    def captured_headers(self, expected_headers, actual_headers):
        normalized_headers = self._normalized_headers(actual_headers)
        result = {}
        for name in expected_headers:
            actual_value = normalized_headers.get(name.lower())
            if actual_value is not None:
                result[name] = self.canonical_value(actual_value)

        return result

    def captured_absent_header_presence(self, request_plan, actual_headers):
        normalized_headers = self._normalized_headers(actual_headers)
        result = {}
        for name in request_plan["absentHeaders"]:
            result[name] = name.lower() in normalized_headers
        return result

    def write_response(self, handler, request_plan):
        response_plan = object_value(
            request_plan["response"],
            "conformanceScenario request response",
        )
        response_body = (response_plan.get("body") or "").encode("utf-8")
        handler.send_response(response_plan["statusCode"])
        for name, value in response_plan["effectiveHeaders"].items():
            handler.send_header(name, self.local_value(value))
        if response_body:
            handler.send_header("Content-Length", str(len(response_body)))
        handler.end_headers()
        if response_body:
            handler.wfile.write(response_body)

    def _server_origin(self):
        host, port = self.httpd.server_address
        return urlparse("http://{}:{}".format(host, port))

    def _request_url(self, handler):
        host = handler.headers.get("Host")
        if host is None:
            host = "{}:{}".format(*self.httpd.server_address)
        return "http://{}{}".format(host, handler.path)

    def _normalized_headers(self, headers):
        return {name.lower(): value for name, value in headers.items()}

    @staticmethod
    def _origin_string(parsed_url):
        return "{}://{}".format(parsed_url.scheme, parsed_url.netloc)


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
