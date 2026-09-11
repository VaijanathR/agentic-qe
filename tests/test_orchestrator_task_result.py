import pytest

from agents.orchestrator import Orchestrator
from memory.task_result import TaskResult
from memory.task_state import TaskStatus


def test_successful_task_result_completes_task():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-801",
        objective="Execute customer API test",
        agent="ExecutionAgent",
    )

    result = TaskResult(
        task_id="TASK-801",
        source_agent="ExecutionAgent",
        objective="Execute customer API test",
        status="COMPLETED",
        findings=["Customer created successfully"],
        evidence=["EVID-801"],
        decisions=["DEC-801"],
    )

    task = orchestrator.complete_task(result)

    assert task.status == TaskStatus.COMPLETED
    assert "EVID-801" in task.evidence
    assert "DEC-801" in task.decisions


def test_failed_task_result_marks_task_failed():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-802",
        objective="Validate customer persistence",
        agent="ExecutionAgent",
    )

    result = TaskResult(
        task_id="TASK-802",
        source_agent="ExecutionAgent",
        objective="Validate customer persistence",
        status=TaskStatus.FAILED.value,
        findings=["POST returned 201 but GET returned 404"],
        evidence=["EVID-802"],
        decisions=["DEC-802"],
        next_action="ANALYZE_FAILURE",
    )

    task = orchestrator.complete_task(result)

    assert task.status == TaskStatus.FAILED
    assert task.next_action == "ANALYZE_FAILURE"


def test_blocked_task_result_blocks_task():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-803",
        objective="Perform restricted operation",
        agent="SecurityAgent",
    )

    result = TaskResult(
        task_id="TASK-803",
        source_agent="SecurityAgent",
        objective="Perform restricted operation",
        status=TaskStatus.BLOCKED.value,
        human_approval_required=False,
        next_action="BYPASS_SECURITY",
    )

    task = orchestrator.complete_task(result)

    assert task.status == TaskStatus.BLOCKED


def test_human_approval_takes_priority():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-804",
        objective="Change approved requirement",
        agent="RequirementsAgent",
    )

    result = TaskResult(
        task_id="TASK-804",
        source_agent="RequirementsAgent",
        objective="Change approved requirement",
        status="COMPLETED",
        human_approval_required=True,
        next_action="CHANGE_REQUIREMENT_BASELINE",
    )

    task = orchestrator.complete_task(result)

    assert task.status == TaskStatus.WAITING_FOR_HUMAN
    assert task.human_approval_required is True


def test_task_result_is_stored_as_task_output():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-805",
        objective="Generate test data",
        agent="TestDataAgent",
    )

    result = TaskResult(
        task_id="TASK-805",
        source_agent="TestDataAgent",
        objective="Generate test data",
        status="COMPLETED",
        activities=["Generated country variants"],
    )

    task = orchestrator.complete_task(result)

    assert len(task.outputs) == 1
    assert task.outputs[0]["task_id"] == "TASK-805"
    assert task.outputs[0]["source_agent"] == "TestDataAgent"


def test_invalid_task_result_is_rejected():
    orchestrator = Orchestrator()

    with pytest.raises(TypeError):
        orchestrator.complete_task("not a task result")


def test_missing_task_result_task_is_rejected():
    orchestrator = Orchestrator()

    result = TaskResult(
        task_id="TASK-999",
        source_agent="ExecutionAgent",
        objective="Unknown task",
        status="COMPLETED",
    )

    with pytest.raises(KeyError):
        orchestrator.complete_task(result)