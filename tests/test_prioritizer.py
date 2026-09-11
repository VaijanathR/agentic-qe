from planner.prioritizer import TestPrioritizer


def test_prioritizer_accepts_complete_risk_inputs():
    prioritizer = TestPrioritizer()

    testcases = [
        {
            "testcase_id": "TC-001",
            "business_criticality": 5,
            "technical_complexity": 4,
            "probability_of_failure": 3,
            "moscow": "MUST",
            "historical_failure": False,
            "security_relevant": True,
        }
    ]

    result = prioritizer.prioritize(
        testcases
    )

    assert result["status"] == "COMPLETED"
    assert len(
        result["prioritized_testcases"]
    ) == 1


def test_prioritizer_calculates_execution_priority():
    prioritizer = TestPrioritizer()

    testcases = [
        {
            "testcase_id": "TC-001",
            "business_criticality": 5,
            "technical_complexity": 5,
            "probability_of_failure": 5,
            "moscow": "MUST",
            "historical_failure": True,
            "security_relevant": True,
        }
    ]

    result = prioritizer.prioritize(
        testcases
    )

    testcase = result[
        "prioritized_testcases"
    ][0]

    assert testcase["risk_score"] == 125
    assert testcase["execution_priority"] == 180


def test_prioritizer_does_not_invent_missing_risk_inputs():
    prioritizer = TestPrioritizer()

    testcases = [
        {
            "testcase_id": "TC-001",
            "moscow": "MUST",
        }
    ]

    result = prioritizer.prioritize(
        testcases
    )

    assert result["status"] == "BLOCKED"
    assert result["prioritized_testcases"] == []

    validation = result["validation"][0]

    assert validation["valid"] is False
    assert (
        "business_criticality"
        in validation["missing_fields"]
    )
    assert (
        "technical_complexity"
        in validation["missing_fields"]
    )
    assert (
        "probability_of_failure"
        in validation["missing_fields"]
    )


def test_prioritizer_preserves_input_testcases():
    prioritizer = TestPrioritizer()

    testcase = {
        "testcase_id": "TC-001",
        "business_criticality": 4,
        "technical_complexity": 3,
        "probability_of_failure": 2,
        "moscow": "SHOULD",
        "historical_failure": True,
        "security_relevant": False,
    }

    original = testcase.copy()

    prioritizer.prioritize([testcase])

    assert testcase == original

def test_prioritizer_does_not_invent_missing_risk_inputs():
    prioritizer = TestPrioritizer()

    testcases = [
        {
            "testcase_id": "TC-001",
            "moscow": "MUST",
        }
    ]

    result = prioritizer.prioritize(
        testcases
    )

    assert result["status"] == "BLOCKED"
    assert result["prioritized_testcases"] == []

    resolution = result[
        "risk_input_resolution"
    ]

    assert resolution["status"] == "BLOCKED"

    testcase_result = resolution["results"][0]

    assert testcase_result["status"] == "BLOCKED"

    assert (
        "business_criticality"
        in testcase_result["missing_fields"]
    )

    assert (
        "technical_complexity"
        in testcase_result["missing_fields"]
    )

    assert (
        "probability_of_failure"
        in testcase_result["missing_fields"]
    )