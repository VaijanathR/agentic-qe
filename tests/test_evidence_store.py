from memory.evidence_store import EvidenceStore


def test_evidence_can_be_added():
    store = EvidenceStore()

    evidence = store.add_evidence(
        evidence_id="EVID-001",
        task_id="TASK-301",
        source="SRS v1.md",
        evidence_type="REQUIREMENT",
        description="Country is mandatory",
    )

    assert evidence["evidence_id"] == "EVID-001"
    assert evidence["task_id"] == "TASK-301"
    assert evidence["source"] == "SRS v1.md"


def test_evidence_can_be_retrieved():
    store = EvidenceStore()

    store.add_evidence(
        evidence_id="EVID-002",
        task_id="TASK-302",
        source="API",
        evidence_type="API_RESPONSE",
        description="Customer created",
        content={"status_code": 201},
    )

    evidence = store.get_evidence(
        "EVID-002"
    )

    assert evidence["content"]["status_code"] == 201


def test_task_evidence_can_be_retrieved():
    store = EvidenceStore()

    store.add_evidence(
        evidence_id="EVID-003",
        task_id="TASK-303",
        source="SRS v1.md",
        evidence_type="REQUIREMENT",
        description="Country is mandatory",
    )

    store.add_evidence(
        evidence_id="EVID-004",
        task_id="TASK-303",
        source="OpenAPI",
        evidence_type="API_CONTRACT",
        description="Country is optional",
    )

    store.add_evidence(
        evidence_id="EVID-005",
        task_id="TASK-304",
        source="API",
        evidence_type="API_RESPONSE",
        description="Customer created",
    )

    evidence = store.get_task_evidence(
        "TASK-303"
    )

    assert len(evidence) == 2


def test_duplicate_evidence_is_rejected():
    store = EvidenceStore()

    store.add_evidence(
        evidence_id="EVID-006",
        task_id="TASK-305",
        source="SRS v1.md",
        evidence_type="REQUIREMENT",
        description="Country is mandatory",
    )

    try:
        store.add_evidence(
            evidence_id="EVID-006",
            task_id="TASK-305",
            source="SRS v1.md",
            evidence_type="REQUIREMENT",
            description="Duplicate evidence",
        )
        assert False
    except ValueError:
        assert True


def test_evidence_count():
    store = EvidenceStore()

    store.add_evidence(
        evidence_id="EVID-007",
        task_id="TASK-306",
        source="Test",
        evidence_type="TEST_RESULT",
        description="Test passed",
    )

    assert store.count() == 1