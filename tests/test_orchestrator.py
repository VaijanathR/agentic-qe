import pytest

from agents.orchestrator import Orchestrator
from memory.decision import Decision
from memory.task_state import TaskStatus


def test_task_can_be_created():
    orchestrator = Orchestrator()

    task = orchestrator.create_task(
        task_id="TASK-701",
        objective="Validate customer creation",
        agent="ExecutionAgent",
    )

    assert task.task_id == "TASK-701"
    assert task.status == TaskStatus.NOT_STARTED


def test_task_can_be_started():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-702",
        objective="Execute customer API test",
        agent="ExecutionAgent",
    )

    task = orchestrator.start_task("TASK-702")

    assert task.status == TaskStatus.RUNNING


def test_task_with_incomplete_dependency_is_blocked():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-703-A",
        objective="Prepare test data",
        agent="TestDataAgent",
    )

    orchestrator.create_task(
        task_id="TASK-703-B",
        objective="Execute test",
        agent="ExecutionAgent",
        dependencies=["TASK-703-A"],
    )

    task = orchestrator.start_task("TASK-703-B")

    assert task.status == TaskStatus.BLOCKED


def test_evidence_is_added_to_task():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-704",
        objective="Validate persistence",
        agent="ExecutionAgent",
    )

    evidence = orchestrator.add_evidence(
        evidence_id="EVID-704",
        task_id="TASK-704",
        source="Customer API",
        evidence_type="API_RESPONSE",
        description="POST returned 201 but GET returned 404",
    )

    task = orchestrator.get_task("TASK-704")

    assert evidence["evidence_id"] == "EVID-704"
    assert "EVID-704" in task.evidence


def test_green_decision_keeps_task_running():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-705",
        objective="Analyze test failure",
        agent="RCAAgent",
    )

    decision = Decision(
        decision_id="DEC-705",
        task_id="TASK-705",
        decision="ANALYZE_FAILURE",
        rationale="Persistence failure requires RCA",
        evidence_ids=["EVID-705"],
        next_action="ANALYZE_FAILURE",
    )

    result = orchestrator.apply_decision(decision)
    task = orchestrator.get_task("TASK-705")

    assert result["governance_level"] == "GREEN"
    assert result["allowed"] is True
    assert task.status == TaskStatus.RUNNING


def test_yellow_decision_waits_for_human():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-706",
        objective="Change requirement baseline",
        agent="RequirementsAgent",
    )

    decision = Decision(
        decision_id="DEC-706",
        task_id="TASK-706",
        decision="CHANGE_REQUIREMENT",
        rationale="Current evidence conflicts with approved baseline",
        next_action="CHANGE_REQUIREMENT_BASELINE",
    )

    result = orchestrator.apply_decision(decision)
    task = orchestrator.get_task("TASK-706")

    assert result["governance_level"] == "YELLOW"
    assert result["allowed"] is False
    assert result["human_approval_required"] is True
    assert task.status == TaskStatus.WAITING_FOR_HUMAN


def test_red_decision_blocks_task():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-707",
        objective="Attempt restricted operation",
        agent="SecurityAgent",
    )

    decision = Decision(
        decision_id="DEC-707",
        task_id="TASK-707",
        decision="BYPASS",
        rationale="Restricted operation must never be performed",
        next_action="BYPASS_SECURITY",
    )

    result = orchestrator.apply_decision(decision)
    task = orchestrator.get_task("TASK-707")

    assert result["governance_level"] == "RED"
    assert result["allowed"] is False
    assert task.status == TaskStatus.BLOCKED


def test_duplicate_task_is_rejected():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-708",
        objective="Test duplicate handling",
        agent="ExecutionAgent",
    )

    with pytest.raises(ValueError):
        orchestrator.create_task(
            task_id="TASK-708",
            objective="Duplicate task",
            agent="ExecutionAgent",
        )


def test_missing_task_is_rejected():
    orchestrator = Orchestrator()

    with pytest.raises(KeyError):
        orchestrator.get_task("TASK-999")