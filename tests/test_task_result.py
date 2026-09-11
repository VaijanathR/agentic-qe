from memory.task_result import TaskResult


def test_task_result_creation():
    result = TaskResult(
        task_id="TASK-101",
        source_agent="RequirementsAgent",
        objective="Validate customer requirements",
        status="COMPLETED",
    )

    assert result.task_id == "TASK-101"
    assert result.source_agent == "RequirementsAgent"
    assert result.status == "COMPLETED"


def test_task_result_can_store_activities_and_findings():
    result = TaskResult(
        task_id="TASK-102",
        source_agent="RequirementsAgent",
        objective="Validate country requirement",
        status="COMPLETED",
    )

    result.add_activity(
        "Retrieved approved SRS"
    )

    result.add_finding(
        "Country is mandatory"
    )

    assert len(result.activities) == 1
    assert len(result.findings) == 1


def test_task_result_can_store_evidence_and_decisions():
    result = TaskResult(
        task_id="TASK-103",
        source_agent="RequirementsAgent",
        objective="Resolve country requirement",
        status="WAITING_FOR_HUMAN",
        human_approval_required=True,
    )

    result.add_evidence(
        "SRS v1.md states Country is mandatory"
    )

    result.add_decision(
        "Human approval required because approved "
        "sources contain conflicting requirements"
    )

    assert len(result.evidence) == 1
    assert len(result.decisions) == 1
    assert result.human_approval_required is True


def test_task_result_tracks_next_action():
    result = TaskResult(
        task_id="TASK-104",
        source_agent="RequirementsAgent",
        objective="Validate requirements",
        status="COMPLETED",
        next_action="HANDOFF_TO_TEST_DESIGN",
    )

    assert (
        result.next_action
        == "HANDOFF_TO_TEST_DESIGN"
    )


def test_task_result_can_be_serialized():
    result = TaskResult(
        task_id="TASK-105",
        source_agent="TestDesignAgent",
        objective="Generate test cases",
        status="COMPLETED",
        confidence=0.95,
    )

    data = result.to_dict()

    assert data["task_id"] == "TASK-105"
    assert data["confidence"] == 0.95
    assert data["status"] == "COMPLETED"

def test_task_result_preserves_requirements():

    result = TaskResult(
        task_id="TASK-001",
        source_agent="RequirementsAgent",
        objective="Extract customer requirements",
        status="COMPLETED",
        requirements=[
            {
                "requirement_id": "CUST-CREATE-001"
            }
        ],
    )

    assert len(result.requirements) == 1
    assert (
        result.requirements[0]["requirement_id"]
        == "CUST-CREATE-001"
    )


def test_task_result_add_requirement():

    result = TaskResult(
        task_id="TASK-002",
        source_agent="RequirementsAgent",
        objective="Extract customer requirements",
        status="COMPLETED",
    )

    result.add_requirement(
        {
            "requirement_id": "AUTH-001"
        }
    )

    assert len(result.requirements) == 1
    assert (
        result.requirements[0]["requirement_id"]
        == "AUTH-001"
    )


def test_task_result_to_dict_includes_requirements():

    result = TaskResult(
        task_id="TASK-003",
        source_agent="RequirementsAgent",
        objective="Extract customer requirements",
        status="COMPLETED",
        requirements=[
            {
                "requirement_id": "PERF-001"
            }
        ],
    )

    data = result.to_dict()

    assert "requirements" in data
    assert (
        data["requirements"][0]["requirement_id"]
        == "PERF-001"
    )