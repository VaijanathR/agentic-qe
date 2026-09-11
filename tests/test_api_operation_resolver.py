from automation.api_operation_resolver import APIOperationResolver


def test_resolves_create_customer():
    resolver = APIOperationResolver()

    result = resolver.resolve({
        "testcase_id": "TC-CUST-008",
        "requirement_id": "REQ-CUST-008",
        "title": "Create customer using valid authorized request",
        "category": "Create",
    })

    assert result["path"] == "/customers"
    assert result["method"] == "POST"


def test_resolves_retrieve_customer():
    resolver = APIOperationResolver()

    result = resolver.resolve({
        "testcase_id": "TC-CUST-015",
        "requirement_id": "REQ-CUST-016",
        "title": "Retrieve existing customer using authorized user",
        "category": "Retrieve",
    })

    assert result["path"] == "/customers/{customerId}"
    assert result["method"] == "GET"


def test_resolves_update_customer():
    resolver = APIOperationResolver()

    result = resolver.resolve({
        "testcase_id": "TC-CUST-018",
        "requirement_id": "REQ-CUST-018",
        "title": "Update existing customer using authorized user",
        "category": "Update",
    })

    assert result["path"] == "/customers/{customerId}"
    assert result["method"] == "PUT"


def test_resolves_create_and_retrieve_flow():
    resolver = APIOperationResolver()

    result = resolver.resolve({
        "testcase_id": "TC-CUST-011",
        "requirement_id": "REQ-CUST-011",
        "title": "Verify created customer can be retrieved",
        "category": "Create_and_Retrieve",
    })

    assert result["path"] == "/customers/{customerId}"
    assert result["method"] == "GET"
    assert result["resolution"] == "RETRIEVE_CREATED_CUSTOMER"


def test_agentic_testcases_are_not_api_automation():
    resolver = APIOperationResolver()

    result = resolver.resolve({
        "testcase_id": "TC-CUST-044",
        "requirement_id": "REQ-CUST-044",
        "title": "Verify requirement change triggers impact analysis and re-planning",
        "category": "Agentic Behavior",
    })

    assert result is None


def test_unresolved_operation_is_explicit():
    resolver = APIOperationResolver()

    result = resolver.resolve({
        "testcase_id": "TC-CUST-999",
        "requirement_id": "REQ-CUST-999",
        "title": "Unknown scenario",
        "category": "Unknown",
    })

    assert result["path"] is None
    assert result["method"] is None
    assert result["resolution"] == "UNRESOLVED"