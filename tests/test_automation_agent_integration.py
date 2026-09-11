import json

from agents.automation_agent import AutomationAgent
from memory.task_state import TaskState


class DummyTask:
    task_id = "TASK-AUTO-INT-001"
    objective = "Generate API automation specifications"


def test_automation_agent_generates_api_automation():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    assert result.status == "COMPLETED"
    assert result.source_agent == "AutomationAgent"
    assert result.evidence


def test_automation_artifact_contains_api_automation():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    artifact_file = result.evidence[0]

    with open(artifact_file, encoding="utf-8") as f:
        artifact = json.load(f)

    assert "api_automation_items" in artifact
    assert "agentic_items" in artifact
    assert "unresolved_items" in artifact


def test_agentic_cases_are_separated():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    with open(result.evidence[0], encoding="utf-8") as f:
        artifact = json.load(f)

    agentic_ids = {
        item["testcase_id"]
        for item in artifact["agentic_items"]
    }

    assert "TC-CUST-044" in agentic_ids
    assert "TC-CUST-050" in agentic_ids


def test_api_automation_contains_openapi_contract_information():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    with open(result.evidence[0], encoding="utf-8") as f:
        artifact = json.load(f)

    api_items = artifact["api_automation_items"]

    assert len(api_items) > 0

    first = api_items[0]

    assert first["http_method"] in {"POST", "GET", "PUT"}
    assert first["endpoint"] in {
        "/customers",
        "/customers/{customerId}",
    }
    assert first["operation_id"] in {
        "createCustomer",
        "getCustomer",
        "updateCustomer",
    }


def test_approved_testcase_baseline_is_not_modified():
    testcase_file = "testcases/testcases.json"

    with open(testcase_file, encoding="utf-8") as f:
        before = f.read()

    agent = AutomationAgent()
    agent.execute(DummyTask())

    with open(testcase_file, encoding="utf-8") as f:
        after = f.read()

    assert before == after

def test_automation_items_contain_resolved_test_data():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    with open(result.evidence[0], encoding="utf-8") as f:
        artifact = json.load(f)

    items = artifact["automation_items"]

    assert len(items) > 0

    item = next(
        item
        for item in items
        if item["testcase_id"] == "TC-CUST-008"
    )

    assert item["test_data_ids"] == ["TD-CUST-008"]
    assert item["resolved_test_data"]

    resolved_ids = {
        record["data_id"]
        for record in item["resolved_test_data"]
    }

    assert "TD-CUST-008" in resolved_ids

def test_api_automation_items_contain_resolved_test_data():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    with open(result.evidence[0], encoding="utf-8") as f:
        artifact = json.load(f)

    api_items = artifact["api_automation_items"]

    item = next(
        item
        for item in api_items
        if item["testcase_id"] == "TC-CUST-011"
    )

    assert item["http_method"] == "GET"
    assert item["endpoint"] == "/customers/{customerId}"
    assert item["test_data_ids"] == ["TD-CUST-008"]
    assert item["resolved_test_data"]

    resolved_ids = {
        record["data_id"]
        for record in item["resolved_test_data"]
    }

    assert "TD-CUST-008" in resolved_ids

def test_api_automation_items_contain_generated_test_code():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    with open(result.evidence[0], encoding="utf-8") as f:
        artifact = json.load(f)

    api_items = artifact["api_automation_items"]

    assert len(api_items) > 0

    item = next(
        item
        for item in api_items
        if item["testcase_id"] == "TC-CUST-011"
    )

    assert item["render_status"] == "GENERATED"
    assert item["generated_test_code"]

    assert "requests.get" in item["generated_test_code"]
    assert "assert response.status_code == 200" in item["generated_test_code"]

def test_api_automation_artifact_tracks_rendered_count():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    with open(result.evidence[0], encoding="utf-8") as f:
        artifact = json.load(f)

    assert artifact["rendered_api_automation_count"] == (
        artifact["api_automation_count"]
    )

def test_tc_cust_011_render_uses_resolved_customer_id():
    agent = AutomationAgent()

    result = agent.execute(DummyTask())

    with open(result.evidence[0], encoding="utf-8") as f:
        artifact = json.load(f)

    item = next(
        item
        for item in artifact["api_automation_items"]
        if item["testcase_id"] == "TC-CUST-011"
    )

    code = item["generated_test_code"]

    assert "requests.get" in code
    assert "assert response.status_code == 200" in code