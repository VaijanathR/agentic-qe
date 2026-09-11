import json

from agents.risk_prioritization_agent import RiskPrioritizationAgent
from memory.task_state import TaskState


def create_task(agent, task_id):
    return TaskState(
        task_id=task_id,
        objective="Prioritize approved testcases by risk",
        agent=agent.name,
    )


def test_name():
    agent = RiskPrioritizationAgent()

    assert agent.name == "RiskPrioritizationAgent"


def test_agent_follows_generic_execute_contract():
    agent = RiskPrioritizationAgent()
    task = create_task(
        agent,
        "TASK-RISK-GENERIC-001",
    )

    result = agent.execute(task)

    assert result.task_id == task.task_id
    assert result.source_agent == agent.name
    assert result.status in {
        "COMPLETED",
        "BLOCKED",
    }


def test_agent_loads_approved_testcase_baseline():
    agent = RiskPrioritizationAgent()

    testcases = agent._load_testcases()

    assert isinstance(testcases, list)
    assert len(testcases) > 0


def test_agent_does_not_invent_missing_risk_inputs():
    agent = RiskPrioritizationAgent()
    task = create_task(
        agent,
        "TASK-RISK-GENERIC-002",
    )

    result = agent.execute(task)

    assert result.status == "BLOCKED"
    assert result.human_approval_required is True
    assert "No risk values were invented" in result.findings


def test_agent_persists_artifact():
    agent = RiskPrioritizationAgent()
    task = create_task(
        agent,
        "TASK-RISK-GENERIC-003",
    )

    result = agent.execute(task)

    artifact = (
        agent.project_root
        / "runs"
        / task.task_id
        / "risk_prioritization.json"
    )

    assert artifact.exists()
    assert artifact.is_file()
    assert str(artifact) in result.evidence


def test_artifact_contains_required_sections():
    agent = RiskPrioritizationAgent()
    task = create_task(
        agent,
        "TASK-RISK-GENERIC-004",
    )

    agent.execute(task)

    artifact = (
        agent.project_root
        / "runs"
        / task.task_id
        / "risk_prioritization.json"
    )

    with artifact.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    required_fields = {
        "task_id",
        "status",
        "input_testcase_count",
        "risk_input_resolution",
        "prioritized_testcases",
        "blocked_testcases",
        "human_approval_required",
        "reason",
        "next_action",
        "evidence",
    }

    assert required_fields.issubset(
        data.keys()
    )


def test_agent_does_not_modify_testcase_baseline():
    agent = RiskPrioritizationAgent()

    before = agent._load_testcases()

    task = create_task(
        agent,
        "TASK-RISK-GENERIC-005",
    )

    agent.execute(task)

    after = agent._load_testcases()

    assert before == after