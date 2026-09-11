from agents.automation_agent import AutomationAgent
from automation.api_test_renderer import APITestRenderer


class DummyTask:
    task_id = "TASK-RENDER-001"
    objective = "Generate API automation specifications"


def _get_api_spec(testcase_id):
    agent = AutomationAgent()
    result = agent.execute(DummyTask())

    import json

    with open(result.evidence[0], encoding="utf-8") as file:
        artifact = json.load(file)

    for item in artifact["api_automation_items"]:
        if item["testcase_id"] == testcase_id:
            return item

    raise AssertionError(
        f"API automation specification not found: {testcase_id}"
    )


def _get_testcase(testcase_id):
    import json

    with open("testcases/testcases.json", encoding="utf-8") as file:
        data = json.load(file)

    testcases = data["testcases"] if isinstance(data, dict) else data

    for testcase in testcases:
        if testcase["testcase_id"] == testcase_id:
            return testcase

    raise AssertionError(
        f"Testcase not found: {testcase_id}"
    )


def test_renderer_generates_post_test():
    testcase = _get_testcase("TC-CUST-008")
    spec = _get_api_spec("TC-CUST-008")

    renderer = APITestRenderer()

    code = renderer.render(testcase, spec)

    assert "requests.post" in code
    assert "/customers" in code
    assert "assert response.status_code == 201" in code


def test_renderer_generates_get_test():
    testcase = _get_testcase("TC-CUST-017")
    spec = _get_api_spec("TC-CUST-017")

    renderer = APITestRenderer()

    code = renderer.render(testcase, spec)

    assert "requests.get" in code
    assert "/customers/{customerId}" in code
    assert "assert response.status_code == 404" in code


def test_renderer_uses_explicit_status():
    testcase = _get_testcase("TC-CUST-011")
    spec = _get_api_spec("TC-CUST-011")

    renderer = APITestRenderer()

    code = renderer.render(testcase, spec)

    assert "requests.get" in code
    assert "/customers/{customerId}" in code
    assert "assert response.status_code == 200" in code


def test_renderer_uses_environment_configuration():
    testcase = _get_testcase("TC-CUST-008")
    spec = _get_api_spec("TC-CUST-008")

    renderer = APITestRenderer()

    code = renderer.render(testcase, spec)

    assert "CUSTOMER_API_BASE_URL" in code
    assert "CUSTOMER_API_TOKEN" in code
    assert "http://localhost:8000" in code


def test_renderer_rejects_missing_endpoint():
    testcase = _get_testcase("TC-CUST-008")

    renderer = APITestRenderer()

    try:
        renderer.render(
            testcase,
            {
                "http_method": "POST",
                "endpoint": None,
            },
        )
    except ValueError as exc:
        assert "Missing API endpoint" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for missing endpoint"
        )

def test_renderer_resolves_customer_id_from_approved_test_data():
    renderer = APITestRenderer()

    testcase = {
        "testcase_id": "TC-CUST-011",
        "title": "Verify created customer can be retrieved",
        "objective": "Verify successful creation is confirmed through subsequent retrieval.",
        "expected_result": [
            "GET returns HTTP 200.",
        ],
    }

    automation_spec = {
        "http_method": "GET",
        "endpoint": "/customers/{customerId}",
    }

    resolved_test_data = [
        {
            "data_id": "TD-CUST-008",
            "section": "customers",
            "data": {
                "customerId": 101,
                "customerName": "ABC Corp",
                "country": "India",
            },
        }
    ]

    rendered = renderer.render(
        testcase,
        automation_spec,
        resolved_test_data,
    )

    assert 'endpoint = "/customers/101"' in rendered
    assert "requests.get(" in rendered
    assert "assert response.status_code == 200" in rendered

def test_renderer_blocks_unresolved_customer_id():
    renderer = APITestRenderer()

    testcase = {
        "testcase_id": "TC-CUST-011",
        "title": "Verify created customer can be retrieved",
        "objective": "Verify successful creation is confirmed through subsequent retrieval.",
        "expected_result": [
            "GET returns HTTP 200.",
        ],
    }

    automation_spec = {
        "http_method": "GET",
        "endpoint": "/customers/{customerId}",
    }

    rendered = renderer.render(
        testcase,
        automation_spec,
        [],
    )

    assert "Runtime customerId dependency was not resolved" in rendered
    assert "Required customerId was not resolved" in rendered
    assert "12345" not in rendered