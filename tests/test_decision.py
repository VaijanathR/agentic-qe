from memory.decision import Decision


def test_decision_can_be_created():
    decision = Decision(
        decision_id="DEC-001",
        task_id="TASK-401",
        decision="FAIL_TEST",
        rationale="Customer could not be retrieved after successful creation",
    )

    assert decision.decision_id == "DEC-001"
    assert decision.task_id == "TASK-401"
    assert decision.decision == "FAIL_TEST"


def test_decision_can_reference_evidence():
    decision = Decision(
        decision_id="DEC-002",
        task_id="TASK-402",
        decision="ESCALATE",
        rationale="Persistence failure requires RCA",
        evidence_ids=["EVID-001", "EVID-002"],
    )

    assert decision.evidence_ids == ["EVID-001", "EVID-002"]


def test_decision_can_add_evidence():
    decision = Decision(
        decision_id="DEC-003",
        task_id="TASK-403",
        decision="REPLAN",
        rationale="Current execution evidence requires additional testing",
    )

    decision.add_evidence("EVID-003")

    assert "EVID-003" in decision.evidence_ids


def test_duplicate_evidence_is_not_added():
    decision = Decision(
        decision_id="DEC-004",
        task_id="TASK-404",
        decision="CONTINUE",
        rationale="Evidence is sufficient",
        evidence_ids=["EVID-004"],
    )

    decision.add_evidence("EVID-004")

    assert decision.evidence_ids == ["EVID-004"]


def test_decision_to_dict():
    decision = Decision(
        decision_id="DEC-005",
        task_id="TASK-405",
        decision="APPROVE",
        rationale="All acceptance criteria satisfied",
        evidence_ids=["EVID-005"],
        confidence=0.95,
        governance_level="GREEN",
        human_approval_required=False,
        next_action="Continue execution",
    )

    result = decision.to_dict()

    assert result["decision_id"] == "DEC-005"
    assert result["evidence_ids"] == ["EVID-005"]
    assert result["confidence"] == 0.95
    assert result["governance_level"] == "GREEN"
    assert result["human_approval_required"] is False