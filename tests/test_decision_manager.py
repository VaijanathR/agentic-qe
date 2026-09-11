import pytest

from memory.decision import Decision
from memory.decision_manager import DecisionManager


def test_decision_can_be_created():
    manager = DecisionManager()

    decision = Decision(
        decision_id="DEC-101",
        task_id="TASK-501",
        decision="FAIL_TEST",
        rationale="Persistence validation failed",
    )

    result = manager.create_decision(decision)

    assert result.decision_id == "DEC-101"
    assert manager.count() == 1


def test_decision_can_be_retrieved():
    manager = DecisionManager()

    decision = Decision(
        decision_id="DEC-102",
        task_id="TASK-502",
        decision="CONTINUE",
        rationale="Evidence is sufficient",
    )

    manager.create_decision(decision)

    result = manager.get_decision("DEC-102")

    assert result.decision == "CONTINUE"


def test_task_decisions_can_be_retrieved():
    manager = DecisionManager()

    manager.create_decision(
        Decision(
            decision_id="DEC-103",
            task_id="TASK-503",
            decision="FAIL_TEST",
            rationale="Test failed",
        )
    )

    manager.create_decision(
        Decision(
            decision_id="DEC-104",
            task_id="TASK-503",
            decision="REPLAN",
            rationale="Additional testing required",
        )
    )

    manager.create_decision(
        Decision(
            decision_id="DEC-105",
            task_id="TASK-504",
            decision="CONTINUE",
            rationale="Test passed",
        )
    )

    results = manager.get_task_decisions("TASK-503")

    assert len(results) == 2
    assert all(decision.task_id == "TASK-503" for decision in results)


def test_duplicate_decision_is_rejected():
    manager = DecisionManager()

    decision = Decision(
        decision_id="DEC-106",
        task_id="TASK-505",
        decision="APPROVE",
        rationale="Acceptance criteria satisfied",
    )

    manager.create_decision(decision)

    with pytest.raises(ValueError):
        manager.create_decision(decision)


def test_invalid_decision_type_is_rejected():
    manager = DecisionManager()

    with pytest.raises(TypeError):
        manager.create_decision("not a decision")


def test_missing_decision_is_rejected():
    manager = DecisionManager()

    with pytest.raises(KeyError):
        manager.get_decision("DEC-999")


def test_decision_count():
    manager = DecisionManager()

    manager.create_decision(
        Decision(
            decision_id="DEC-107",
            task_id="TASK-506",
            decision="CONTINUE",
            rationale="Execution can continue",
        )
    )

    manager.create_decision(
        Decision(
            decision_id="DEC-108",
            task_id="TASK-506",
            decision="REPLAN",
            rationale="New evidence requires replanning",
        )
    )

    assert manager.count() == 2