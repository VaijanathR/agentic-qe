from agents.requirements_agent import RequirementsAgent
from memory.task_state import TaskState
from memory.task_result import TaskResult


def test_requirements_agent_has_correct_name():
    agent = RequirementsAgent()

    assert agent.name == "RequirementsAgent"


def test_requirements_agent_returns_task_result():
    agent = RequirementsAgent()

    task = TaskState(
        task_id="TASK-501",
        objective="Validate customer requirements",
        agent="RequirementsAgent",
    )

    result = agent.execute(task)

    assert isinstance(result, TaskResult)
    assert result.task_id == "TASK-501"
    assert result.source_agent == "RequirementsAgent"
    assert result.objective == "Validate customer requirements"
    assert result.status == "COMPLETED"

def test_requirements_agent_retrieves_approved_knowledge():
    agent = RequirementsAgent()

    task = TaskState(
        task_id="TASK-502",
        objective="Validate customer country requirement",
        agent="RequirementsAgent",
    )

    result = agent.execute(task)

    assert isinstance(result, TaskResult)
    assert result.status == "COMPLETED"
    assert len(result.evidence) > 0
    assert "KNOW-CUST-001" in result.evidence

def test_requirements_agent_identifies_authoritative_requirement_baseline():
    agent = RequirementsAgent()

    task = TaskState(
        task_id="REQ-AUTH-001",
        objective="customer creation requirements",
        agent=agent.name,
    )

    result = agent.execute(task)

    assert result.status == "COMPLETED"

    assert "KNOW-CUST-001" in result.evidence

    assert any(
        "Authoritative requirement baseline identified"
        in finding
        for finding in result.findings
    )

def test_requirements_agent_extracts_requirements_from_authoritative_srs():

    agent = RequirementsAgent()

    task = TaskState(
        task_id="REQ-EXTRACT-001",
        objective="customer creation requirements",
        agent=agent.name,
    )

    result = agent.execute(task)

    assert result.status == "COMPLETED"

    assert len(result.requirements) > 0

    requirement_ids = [
        requirement["requirement_id"]
        for requirement in result.requirements
    ]

    assert "CUST-CREATE-001" in requirement_ids
    assert "CUST-CREATE-002" in requirement_ids
    assert "AUTH-001" in requirement_ids
    assert "PERF-001" in requirement_ids