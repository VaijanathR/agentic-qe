import pytest

from memory.decision import Decision
from memory.decision_governance import DecisionGovernance


def test_green_action_can_proceed():
    decision = Decision(
        decision_id="DEC-GREEN-001",
        task_id="TASK-601",
        decision="CONTINUE",
        rationale="Evidence is sufficient",
        next_action="RETRIEVE_KNOWLEDGE",
    )

    result = DecisionGovernance().evaluate(decision)

    assert result["decision_id"] == "DEC-GREEN-001"
    assert result["governance_level"] == "GREEN"
    assert result["allowed"] is True
    assert result["human_approval_required"] is False


def test_yellow_action_requires_human_approval():
    decision = Decision(
        decision_id="DEC-YELLOW-001",
        task_id="TASK-602",
        decision="REPLAN",
        rationale="Approved baseline may need modification",
        next_action="CHANGE_REQUIREMENT_BASELINE",
    )

    result = DecisionGovernance().evaluate(decision)

    assert result["governance_level"] == "YELLOW"
    assert result["allowed"] is False
    assert result["human_approval_required"] is True


def test_red_action_is_blocked():
    decision = Decision(
        decision_id="DEC-RED-001",
        task_id="TASK-603",
        decision="STOP",
        rationale="Action violates security boundary",
        next_action="BYPASS_SECURITY",
    )

    result = DecisionGovernance().evaluate(decision)

    assert result["governance_level"] == "RED"
    assert result["allowed"] is False
    assert result["human_approval_required"] is False


def test_unknown_action_defaults_to_human_governance():
    decision = Decision(
        decision_id="DEC-UNKNOWN-001",
        task_id="TASK-604",
        decision="REVIEW",
        rationale="Action is not explicitly classified",
        next_action="SOME_NEW_ACTION",
    )

    result = DecisionGovernance().evaluate(decision)

    assert result["governance_level"] == "YELLOW"
    assert result["allowed"] is False
    assert result["human_approval_required"] is True


def test_missing_next_action_is_rejected():
    decision = Decision(
        decision_id="DEC-INVALID-001",
        task_id="TASK-605",
        decision="CONTINUE",
        rationale="Evidence is sufficient",
    )

    with pytest.raises(ValueError):
        DecisionGovernance().evaluate(decision)


def test_governance_result_preserves_reason():
    decision = Decision(
        decision_id="DEC-REASON-001",
        task_id="TASK-606",
        decision="EXECUTE",
        rationale="Approved execution step",
        next_action="EXECUTE_APPROVED_TEST",
    )

    result = DecisionGovernance().evaluate(decision)

    assert result["reason"]
    assert result["action"] == "EXECUTE_APPROVED_TEST"