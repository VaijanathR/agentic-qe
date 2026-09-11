from memory.task_state import TaskState, TaskStatus


def test_task_state_creation():
    task = TaskState(
        task_id="TASK-001",
        objective="Validate customer requirements",
        agent="RequirementsAgent",
    )

    assert task.task_id == "TASK-001"
    assert task.objective == "Validate customer requirements"
    assert task.agent == "RequirementsAgent"
    assert task.status == TaskStatus.NOT_STARTED


def test_task_status_can_be_updated():
    task = TaskState(
        task_id="TASK-002",
        objective="Generate test cases",
        agent="TestDesignAgent",
    )

    task.update_status(TaskStatus.RUNNING)

    assert task.status == TaskStatus.RUNNING


def test_task_can_store_evidence_and_decisions():
    task = TaskState(
        task_id="TASK-003",
        objective="Validate country requirement",
        agent="RequirementsAgent",
    )

    task.add_evidence(
        "SRS states that Country is mandatory."
    )

    task.add_decision(
        "Country must be supplied."
    )

    assert len(task.evidence) == 1
    assert len(task.decisions) == 1


def test_task_dependencies():
    task = TaskState(
        task_id="TASK-004",
        objective="Generate automation",
        agent="AutomationAgent",
    )

    task.add_dependency("TASK-003")

    assert "TASK-003" in task.dependencies


def test_task_can_be_waiting_for_human():
    task = TaskState(
        task_id="TASK-005",
        objective="Resolve requirement conflict",
        agent="RequirementsAgent",
        human_approval_required=True,
    )

    task.update_status(TaskStatus.WAITING_FOR_HUMAN)

    assert task.human_approval_required is True
    assert task.status == TaskStatus.WAITING_FOR_HUMAN


def test_task_state_can_be_serialized():
    task = TaskState(
        task_id="TASK-006",
        objective="Generate test data",
        agent="TestDataAgent",
        status=TaskStatus.COMPLETED,
        next_action="HANDOFF_TO_AUTOMATION",
    )

    data = task.to_dict()

    assert data["task_id"] == "TASK-006"
    assert data["status"] == "COMPLETED"
    assert data["next_action"] == "HANDOFF_TO_AUTOMATION"