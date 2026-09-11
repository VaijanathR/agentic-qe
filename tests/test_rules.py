# Placeholder for tests covering deterministic rules (governance, validation, prioritization).
from rules.governance_rules import GovernanceRules
from rules.validation_rules import validate_customer
from rules.prioritization_rules import calculate_risk_score
from rules.prioritization_rules import (
    calculate_execution_priority,
    prioritize_testcases,
)

def test_green_governance_action():
    rules = GovernanceRules()

    result = rules.evaluate("READ_APPROVED_DOCUMENT")

    assert result["governance_level"] == "GREEN"
    assert result["allowed"] is True
    assert result["human_approval_required"] is False


def test_yellow_governance_action():
    rules = GovernanceRules()

    result = rules.evaluate("MODIFY_APPROVED_TESTCASE")

    assert result["governance_level"] == "YELLOW"
    assert result["allowed"] is False
    assert result["human_approval_required"] is True


def test_red_governance_action():
    rules = GovernanceRules()

    result = rules.evaluate("DELETE_ARTIFACT")

    assert result["governance_level"] == "RED"
    assert result["allowed"] is False


def test_valid_customer():
    customer = {
        "customerName": "ABC Corp",
        "country": "India",
        "email": "contact@abccorp.example",
        "phone": "+91-9876500003",
    }

    result = validate_customer(customer)

    assert result["valid"] is True
    assert result["errors"] == []


def test_invalid_country():
    customer = {
        "customerName": "ABC Corp",
        "country": "Zingababuva",
    }

    result = validate_customer(customer)

    assert result["valid"] is False
    assert "Unsupported country" in result["errors"][0]


def test_case_insensitive_country():
    customer = {
        "customerName": "ABC Corp",
        "country": "iNdIa",
    }

    result = validate_customer(customer)

    assert result["valid"] is True


def test_risk_score():
    score = calculate_risk_score(
        business_criticality=5,
        technical_complexity=5,
        probability_of_failure=5,
    )

    assert score == 125

def test_execution_priority_moscow_weight():
    score = calculate_execution_priority(
        risk_score=50,
        moscow="MUST",
    )

    assert score == 70


def test_execution_priority_historical_failure():
    score = calculate_execution_priority(
        risk_score=50,
        moscow="MUST",
        historical_failure=True,
    )

    assert score == 85


def test_execution_priority_security():
    score = calculate_execution_priority(
        risk_score=50,
        moscow="MUST",
        security_relevant=True,
    )

    assert score == 90


def test_prioritize_testcases_orders_by_execution_priority():
    testcases = [
        {
            "testcase_id": "TC-LOW",
            "business_criticality": 2,
            "technical_complexity": 2,
            "probability_of_failure": 2,
            "moscow": "SHOULD",
        },
        {
            "testcase_id": "TC-HIGH",
            "business_criticality": 5,
            "technical_complexity": 5,
            "probability_of_failure": 5,
            "moscow": "MUST",
            "historical_failure": True,
            "security_relevant": True,
        },
    ]

    result = prioritize_testcases(testcases)

    assert result[0]["testcase_id"] == "TC-HIGH"
    assert result[0]["risk_score"] == 125
    assert result[0]["execution_priority"] == 180