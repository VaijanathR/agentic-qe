from pathlib import Path

from automation.api_automation_generator import (
    APIAutomationGenerator,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_generator_reads_create_customer_contract():
    generator = APIAutomationGenerator(
        PROJECT_ROOT
        / "technical_docs"
        / "customer_api.yaml"
    )

    testcase = {
        "testcase_id": "TC-CUST-001",
        "requirement_id": "REQ-CUST-001",
        "title": "Create valid customer",
        "objective": "Create a customer successfully",
    }

    result = generator.generate_for_testcase(
        testcase,
        "/customers",
        "post",
    )

    assert result["http_method"] == "POST"
    assert result["endpoint"] == "/customers"
    assert result["operation_id"] == "createCustomer"


def test_generator_captures_expected_create_responses():
    generator = APIAutomationGenerator(
        PROJECT_ROOT
        / "technical_docs"
        / "customer_api.yaml"
    )

    testcase = {
        "testcase_id": "TC-CUST-001",
        "requirement_id": "REQ-CUST-001",
        "title": "Create valid customer",
        "objective": "Create a customer successfully",
    }

    result = generator.generate_for_testcase(
        testcase,
        "/customers",
        "post",
    )

    assert "201" in result["expected_responses"]
    assert "400" in result["expected_responses"]
    assert "401" in result["expected_responses"]
    assert "403" in result["expected_responses"]
    assert "409" in result["expected_responses"]
    assert "500" in result["expected_responses"]


def test_generator_detects_bearer_security():
    generator = APIAutomationGenerator(
        PROJECT_ROOT
        / "technical_docs"
        / "customer_api.yaml"
    )

    testcase = {
        "testcase_id": "TC-CUST-001",
        "requirement_id": "REQ-CUST-001",
    }

    result = generator.generate_for_testcase(
        testcase,
        "/customers",
        "post",
    )

    assert result["security_required"] is True


def test_generator_reads_retrieve_customer_contract():
    generator = APIAutomationGenerator(
        PROJECT_ROOT
        / "technical_docs"
        / "customer_api.yaml"
    )

    testcase = {
        "testcase_id": "TC-CUST-002",
        "requirement_id": "REQ-CUST-002",
    }

    result = generator.generate_for_testcase(
        testcase,
        "/customers/{customerId}",
        "get",
    )

    assert result["http_method"] == "GET"
    assert result["operation_id"] == "getCustomer"
    assert "200" in result["expected_responses"]
    assert "404" in result["expected_responses"]


def test_generator_reads_update_customer_contract():
    generator = APIAutomationGenerator(
        PROJECT_ROOT
        / "technical_docs"
        / "customer_api.yaml"
    )

    testcase = {
        "testcase_id": "TC-CUST-003",
        "requirement_id": "REQ-CUST-003",
    }

    result = generator.generate_for_testcase(
        testcase,
        "/customers/{customerId}",
        "put",
    )

    assert result["http_method"] == "PUT"
    assert result["operation_id"] == "updateCustomer"
    assert "200" in result["expected_responses"]
    assert "409" in result["expected_responses"]


def test_generator_rejects_unknown_endpoint():
    generator = APIAutomationGenerator(
        PROJECT_ROOT
        / "technical_docs"
        / "customer_api.yaml"
    )

    testcase = {
        "testcase_id": "TC-CUST-999",
    }

    try:
        generator.generate_for_testcase(
            testcase,
            "/unknown",
            "post",
        )
        assert False
    except ValueError as exc:
        assert "OpenAPI path not found" in str(exc)