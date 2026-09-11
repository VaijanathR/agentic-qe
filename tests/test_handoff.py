from memory.task_result import TaskResult
from memory.handoff import HandoffManager


def create_result():
    result = TaskResult(
        task_id="TASK-201",
        source_agent="RequirementsAgent",
        objective="Validate customer requirements",
        status="COMPLETED",
        confidence=0.95,
        next_action="HANDOFF_TO_TEST_DESIGN",
    )

    result.add_activity(
        "Retrieved approved SRS"
    )

    result.add_finding(
        "Country is mandatory"
    )

    result.add_evidence(
        "SRS v1.md"
    )

    result.add_decision(
        "Country must be provided"
    )

    return result


def test_handoff_can_be_created():
    manager = HandoffManager()
    result = create_result()

    handoff = manager.create_handoff(
        result,
        "TestDesignAgent",
    )

    assert handoff["task_id"] == "TASK-201"
    assert (
        handoff["source_agent"]
        == "RequirementsAgent"
    )
    assert (
        handoff["receiving_agent"]
        == "TestDesignAgent"
    )


def test_handoff_preserves_agent_result():
    manager = HandoffManager()
    result = create_result()

    handoff = manager.create_handoff(
        result,
        "TestDesignAgent",
    )

    assert (
        handoff["activities"]
        == result.activities
    )

    assert (
        handoff["findings"]
        == result.findings
    )

    assert (
        handoff["evidence"]
        == result.evidence
    )

    assert (
        handoff["decisions"]
        == result.decisions
    )


def test_handoff_preserves_governance_information():
    manager = HandoffManager()

    result = TaskResult(
        task_id="TASK-202",
        source_agent="RequirementsAgent",
        objective="Resolve requirement conflict",
        status="WAITING_FOR_HUMAN",
        human_approval_required=True,
        next_action="WAIT_FOR_HUMAN_APPROVAL",
    )

    handoff = manager.create_handoff(
        result,
        "PrimaryAgent",
    )

    assert (
        handoff["human_approval_required"]
        is True
    )

    assert (
        handoff["next_action"]
        == "WAIT_FOR_HUMAN_APPROVAL"
    )


def test_handoff_can_be_retrieved():
    manager = HandoffManager()
    result = create_result()

    handoff = manager.create_handoff(
        result,
        "TestDesignAgent",
    )

    retrieved = manager.get_handoff(
        handoff["handoff_id"]
    )

    assert retrieved == handoff


def test_invalid_handoff_result_is_rejected():
    manager = HandoffManager()

    try:
        manager.create_handoff(
            "invalid-result",
            "TestDesignAgent",
        )
        assert False
    except TypeError:
        assert True


def test_missing_receiving_agent_is_rejected():
    manager = HandoffManager()
    result = create_result()

    try:
        manager.create_handoff(
            result,
            "",
        )
        assert False
    except ValueError:
        assert True