import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = PROJECT_ROOT / "runs" / "risk_prioritization_schema.json"


def load_schema():
    with SCHEMA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_risk_prioritization_schema_exists():
    assert SCHEMA_FILE.exists()
    assert SCHEMA_FILE.is_file()


def test_risk_prioritization_schema_has_required_metadata():
    schema = load_schema()

    assert schema["artifact_type"] == "risk_prioritization"
    assert schema["artifact_version"] == "1.0"
    assert "description" in schema


def test_risk_prioritization_schema_has_required_fields():
    schema = load_schema()

    required_fields = {
        "task_id",
        "status",
        "input_testcase_count",
        "risk_input_resolution",
        "prioritized_testcases",
        "blocked_testcases",
        "human_approval_required",
        "reason",
        "next_action",
        "evidence",
    }

    assert set(schema["required_fields"]) == required_fields


def test_risk_prioritization_schema_has_governance_rules():
    schema = load_schema()

    governance = schema["governance"]

    assert governance["missing_risk_inputs"] == "BLOCKED"
    assert governance["invalid_risk_inputs"] == "BLOCKED"
    assert governance["ambiguous_risk_inputs"] == "HUMAN_APPROVAL_REQUIRED"
    assert governance["invented_risk_inputs"] == "PROHIBITED"


def test_risk_prioritization_schema_preserves_baseline_immutability():
    schema = load_schema()

    assert schema["immutability"]["approved_testcase_baseline"] == "READ_ONLY"
    assert schema["immutability"]["risk_prioritization_artifact"] == "DERIVED"