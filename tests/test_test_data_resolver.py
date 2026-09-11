import json

from automation.test_data_resolver import TestDataResolver


def test_resolves_primary_customer_data():
    resolver = TestDataResolver()

    result = resolver.resolve(["TD-CUST-008"])

    assert len(result) == 1
    assert result[0]["data_id"] == "TD-CUST-008"
    assert result[0]["section"] == "customer_data"
    assert result[0]["data"]["customerName"] == "ABC Corp"
    assert result[0]["data"]["country"] == "India"


def test_resolves_variation_data():
    resolver = TestDataResolver()

    result = resolver.resolve(["TD-CUST-002-A"])

    assert len(result) == 1
    assert result[0]["data_id"] == "TD-CUST-002-A"
    assert result[0]["parent_data_id"] == "TD-CUST-002"
    assert result[0]["data"]["customerName"] is None
    assert result[0]["data"]["expected_valid"] is False


def test_resolves_multiple_data_ids():
    resolver = TestDataResolver()

    result = resolver.resolve([
        "TD-CUST-008",
        "TD-CUST-010",
    ])

    assert len(result) == 2
    assert result[0]["data_id"] == "TD-CUST-008"
    assert result[1]["data_id"] == "TD-CUST-010"


def test_rejects_unknown_test_data_id():
    resolver = TestDataResolver()

    try:
        resolver.resolve(["TD-CUST-999"])
    except ValueError as exc:
        assert "Approved test data not found" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for unknown test data ID"
        )


def test_does_not_modify_approved_test_data_baseline():
    testdata_file = "testdata/testdata.json"

    with open(testdata_file, encoding="utf-8") as file:
        before = file.read()

    resolver = TestDataResolver()
    resolver.resolve(["TD-CUST-008"])

    with open(testdata_file, encoding="utf-8") as file:
        after = file.read()

    assert before == after