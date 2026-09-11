from planner.risk_input_resolver import (
    RiskInputResolver,
)


def test_complete_risk_inputs_are_resolved():
    resolver = RiskInputResolver()

    testcase = {
        "testcase_id": "TC-001",
        "business_criticality": 5,
        "technical_complexity": 4,
        "probability_of_failure": 3,
    }

    result = resolver.resolve(testcase)

    assert result["status"] == "RESOLVED"
    assert result["risk_inputs"] == {
        "business_criticality": 5,
        "technical_complexity": 4,
        "probability_of_failure": 3,
    }


def test_missing_risk_input_is_blocked():
    resolver = RiskInputResolver()

    testcase = {
        "testcase_id": "TC-001",
        "business_criticality": 5,
        "technical_complexity": 4,
    }

    result = resolver.resolve(testcase)

    assert result["status"] == "BLOCKED"
    assert (
        "probability_of_failure"
        in result["missing_fields"]
    )


def test_none_risk_input_is_blocked():
    resolver = RiskInputResolver()

    testcase = {
        "testcase_id": "TC-001",
        "business_criticality": 5,
        "technical_complexity": None,
        "probability_of_failure": 3,
    }

    result = resolver.resolve(testcase)

    assert result["status"] == "BLOCKED"
    assert (
        "technical_complexity"
        in result["missing_fields"]
    )


def test_resolve_all_blocks_if_any_testcase_is_missing_risk():
    resolver = RiskInputResolver()

    testcases = [
        {
            "testcase_id": "TC-001",
            "business_criticality": 5,
            "technical_complexity": 4,
            "probability_of_failure": 3,
        },
        {
            "testcase_id": "TC-002",
            "business_criticality": 4,
        },
    ]

    result = resolver.resolve_all(testcases)

    assert result["status"] == "BLOCKED"
    assert len(result["results"]) == 2


def test_resolver_does_not_modify_testcase():
    resolver = RiskInputResolver()

    testcase = {
        "testcase_id": "TC-001",
        "business_criticality": 5,
        "technical_complexity": 4,
        "probability_of_failure": 3,
    }

    original = testcase.copy()

    resolver.resolve(testcase)

    assert testcase == original