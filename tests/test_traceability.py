from requirements.traceability import (
    TraceabilityAnalyzer,
)


def test_exact_identifier_mapping():
    analyzer = TraceabilityAnalyzer()

    requirements = [
        {
            "requirement_id": "REQ-001",
            "title": "Customer ID is unique",
        }
    ]

    rtm_rows = [
        {
            "Requirement_ID": "REQ-001",
            "Requirement_Title": "Customer ID is unique",
            "Testcase_ID": "TC-001",
        }
    ]

    testcases = [
        {
            "testcase_id": "TC-001",
        }
    ]

    result = analyzer.analyze(
        requirements,
        rtm_rows,
        testcases,
    )

    assert len(result["matched"]) == 1
    assert result["matched"][0]["match_type"] == "IDENTIFIER"
    assert result["mismatches"] == []
    assert result["gaps"] == []


def test_identifier_mismatch_requires_governance():
    analyzer = TraceabilityAnalyzer()

    requirements = [
        {
            "requirement_id": "CUST-CREATE-001",
            "title": "Customer ID is system generated and unique",
        }
    ]

    rtm_rows = [
        {
            "Requirement_ID": "REQ-CUST-001",
            "Requirement_Title": (
                "Customer ID is system generated and unique"
            ),
            "Testcase_ID": "TC-CUST-001",
        }
    ]

    testcases = [
        {
            "testcase_id": "TC-CUST-001",
        }
    ]

    result = analyzer.analyze(
        requirements,
        rtm_rows,
        testcases,
    )

    assert len(result["matched"]) == 1
    assert (
        result["matched"][0]["match_type"]
        == "SEMANTIC_IDENTIFIER_MISMATCH"
    )

    assert len(result["mismatches"]) == 1

    mismatch = result["mismatches"][0]

    assert (
        mismatch["mismatch_type"]
        == "REQUIREMENT_IDENTIFIER_MISMATCH"
    )

    assert mismatch["human_governance_required"] is True


def test_requirement_without_rtm_is_gap():
    analyzer = TraceabilityAnalyzer()

    requirements = [
        {
            "requirement_id": "REQ-001",
            "title": "Customer ID is unique",
        }
    ]

    result = analyzer.analyze(
        requirements,
        [],
        [],
    )

    assert len(result["gaps"]) == 1
    assert result["gaps"][0]["gap_type"] == "NO_RTM_MAPPING"


def test_rtm_without_testcase_is_gap():
    analyzer = TraceabilityAnalyzer()

    requirements = [
        {
            "requirement_id": "REQ-001",
            "title": "Customer ID is unique",
        }
    ]

    rtm_rows = [
        {
            "Requirement_ID": "REQ-001",
            "Requirement_Title": "Customer ID is unique",
            "Testcase_ID": "TC-001",
        }
    ]

    result = analyzer.analyze(
        requirements,
        rtm_rows,
        [],
    )

    assert len(result["gaps"]) == 1
    assert result["gaps"][0]["gap_type"] == "NO_TESTCASE"


def test_coverage_summary():
    analyzer = TraceabilityAnalyzer()

    requirements = [
        {
            "requirement_id": "REQ-001",
            "title": "Customer ID is unique",
        },
        {
            "requirement_id": "REQ-002",
            "title": "Customer name is mandatory",
        },
    ]

    rtm_rows = [
        {
            "Requirement_ID": "REQ-001",
            "Requirement_Title": "Customer ID is unique",
            "Testcase_ID": "TC-001",
        }
    ]

    testcases = [
        {
            "testcase_id": "TC-001",
        }
    ]

    result = analyzer.analyze(
        requirements,
        rtm_rows,
        testcases,
    )

    summary = result["coverage_summary"]

    assert summary["total_requirements"] == 2
    assert summary["covered_requirements"] == 1
    assert summary["coverage_percentage"] == 50.0