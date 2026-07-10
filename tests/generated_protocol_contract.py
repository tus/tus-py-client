"""SDK test adapter for the canonical api2 TUS contract fixture."""

import json
from pathlib import Path


with (Path(__file__).parent / "api2_tus_contract.json").open(encoding="utf-8") as stream:
    _CONTRACT = json.load(stream)

TUS_WIRE_VERSIONS = _CONTRACT["wireVersions"]
TUS_PROTOCOL_OPERATIONS = _CONTRACT["operations"]
TUS_CLIENT_FEATURES = _CONTRACT["clientFeatures"]
TUS_MANAGED_UPLOAD = _CONTRACT["managedUpload"]
TUS_CLIENT_CONFORMANCE_SCENARIOS = _CONTRACT["clientConformanceScenarios"]

_PROTOCOL_FEATURE_IDS = [
    step["featureId"]
    for step in TUS_MANAGED_UPLOAD["flow"]
    if step["kind"] == "protocol-feature"
]
_RUNTIME_PROFILES = [profile["runtime"] for profile in TUS_MANAGED_UPLOAD["runtimeProfiles"]]
TUS_MANAGED_UPLOAD_PROOF_CASES = [
    {
        "featureId": TUS_MANAGED_UPLOAD["featureId"],
        "layer": TUS_MANAGED_UPLOAD["layer"],
        "protocolFeatureIds": _PROTOCOL_FEATURE_IDS,
        "requiredPrimitives": scenario["requiredPrimitives"],
        "runtimeProfiles": _RUNTIME_PROFILES,
        "scenarioId": scenario["scenarioId"],
    }
    for scenario in TUS_MANAGED_UPLOAD["scenarios"]
]
