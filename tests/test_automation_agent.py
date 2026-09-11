import json

from agents.automation_agent import AutomationAgent
from memory.task_result import TaskResult
from memory.task_state import TaskState


def create_task(agent, task_id):
    return TaskState(
        task_id=task_id,
        objective="Convert approved testcases into automation",
        agent=agent.name,
    )


def test_name():
    agent = AutomationAgent()

    assert agent.name == "AutomationAgent"


def test_agent_follows_generic_execute_contract():
    agent = AutomationAgent()

    task = create_task(
        agent,
        "TASK-AUTO-001",
    )

    result = agent.execute(task)

    assert isinstance(result, TaskResult)
    assert result.task_id == task.task_id
    assert result.source_agent == agent.name
    assert result.status == "COMPLETED"


def test_agent_loads_approved_testcase_baseline():
    agent = AutomationAgent()

    testcases = agent._load_testcases()

    assert isinstance(testcases, list)
    assert len(testcases) > 0


def test_agent_identifies_automation_candidates():
    agent = AutomationAgent()

    testcases = agent._load_testcases()
    candidates = agent._identify_candidates(
        testcases
    )

    assert len(candidates) > 0


def test_agent_persists_automation_artifact():
    agent = AutomationAgent()

    task = create_task(
        agent,
        "TASK-AUTO-002",
    )

    result = agent.execute(task)

    artifact = (
        agent.project_root
        / "runs"
        / task.task_id
        / "automation.json"
    )

    assert artifact.exists()
    assert artifact.is_file()
    assert str(artifact) in result.evidence


def test_automation_artifact_contains_required_sections():
    agent = AutomationAgent()

    task = create_task(
        agent,
        "TASK-AUTO-003",
    )

    agent.execute(task)

    artifact = (
        agent.project_root
        / "runs"
        / task.task_id
        / "automation.json"
    )

    with artifact.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert data["task_id"] == task.task_id
    assert data["status"] == "COMPLETED"
    assert "input_testcase_count" in data
    assert "automation_candidate_count" in data
    assert "automation_items" in data
    assert data["execution_deferred"] is True


def test_agent_does_not_modify_testcase_baseline():
    agent = AutomationAgent()

    before = agent._load_testcases()

    task = create_task(
        agent,
        "TASK-AUTO-004",
    )

    agent.execute(task)

    after = agent._load_testcases()

    assert before == after