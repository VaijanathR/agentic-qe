from agents.risk_prioritization_agent import RiskPrioritizationAgent
from memory.task_result import TaskResult
from memory.task_state import TaskState, TaskStatus
from agents.orchestrator import Orchestrator


def test_orchestrator_can_execute_risk_prioritization_agent():
    orchestrator = Orchestrator()
    agent = RiskPrioritizationAgent()

    task = orchestrator.create_task(
        task_id="TASK-ORCH-RISK-001",
        objective="Prioritize approved testcases by risk",
        agent=agent.name,
    )

    result = agent.execute(task)

    assert isinstance(result, TaskResult)
    assert result.status == "BLOCKED"
    assert result.human_approval_required is True

    completed_task = orchestrator.complete_task(result)

    assert completed_task.status == TaskStatus.WAITING_FOR_HUMAN


def test_orchestrator_preserves_risk_governance_state():
    orchestrator = Orchestrator()
    agent = RiskPrioritizationAgent()

    task = orchestrator.create_task(
        task_id="TASK-ORCH-RISK-002",
        objective="Prioritize approved testcases by risk",
        agent=agent.name,
    )

    result = agent.execute(task)

    assert result.status == "BLOCKED"
    assert result.human_approval_required is True

    completed_task = orchestrator.complete_task(result)

    assert completed_task.status == TaskStatus.WAITING_FOR_HUMAN


def test_orchestrator_captures_risk_prioritization_evidence():
    orchestrator = Orchestrator()
    agent = RiskPrioritizationAgent()

    task = orchestrator.create_task(
        task_id="TASK-ORCH-RISK-003",
        objective="Prioritize approved testcases and capture evidence",
        agent=agent.name,
    )

    result = agent.execute(task)

    completed_task = orchestrator.complete_task(result)

    assert len(completed_task.evidence) > 0
    assert any(
        "risk_prioritization.json" in evidence
        for evidence in completed_task.evidence
    )


def test_risk_prioritization_artifact_is_created_through_agent():
    orchestrator = Orchestrator()
    agent = RiskPrioritizationAgent()

    task = orchestrator.create_task(
        task_id="TASK-ORCH-RISK-004",
        objective="Create risk prioritization artifact",
        agent=agent.name,
    )

    result = agent.execute(task)

    artifact = (
        agent.project_root
        / "runs"
        / task.task_id
        / "risk_prioritization.json"
    )

    assert artifact.exists()
    assert str(artifact) in result.evidence

def test_orchestrator_execute_task_runs_risk_prioritization_agent():
    orchestrator = Orchestrator()
    agent = RiskPrioritizationAgent()

    task = orchestrator.create_task(
        task_id="TASK-ORCH-RISK-005",
        objective="Prioritize approved testcases by risk",
        agent=agent.name,
    )

    final_task = orchestrator.execute_task(
        task.task_id,
        agent,
    )

    assert isinstance(final_task, TaskState)

    assert final_task.task_id == task.task_id
    assert final_task.status == TaskStatus.WAITING_FOR_HUMAN

    assert final_task.human_approval_required is True
    assert len(final_task.evidence) > 0