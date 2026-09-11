# Placeholder for tests covering RAG knowledge storage and retrieval.
from pathlib import Path

from rag.metadata import KnowledgeMetadata
from rag.knowledge_store import KnowledgeStore
from rag.retriever import KnowledgeRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]

METADATA_FILE = (
    PROJECT_ROOT
    / "rag"
    / "knowledge_metadata.json"
)


def create_retriever():
    metadata = KnowledgeMetadata(
        METADATA_FILE
    )

    store = KnowledgeStore(
        PROJECT_ROOT,
        metadata,
    )

    return KnowledgeRetriever(store)


def test_metadata_loads():
    metadata = KnowledgeMetadata(
        METADATA_FILE
    )

    documents = metadata.get_all()

    assert len(documents) >= 8


def test_approved_documents_are_available():
    metadata = KnowledgeMetadata(
        METADATA_FILE
    )

    approved = metadata.get_approved()

    assert len(approved) >= 8


def test_srs_can_be_loaded():
    metadata = KnowledgeMetadata(
        METADATA_FILE
    )

    store = KnowledgeStore(
        PROJECT_ROOT,
        metadata,
    )

    document = store.get_document(
        "KNOW-CUST-001"
    )

    assert document["approval_status"] == "Approved"
    assert "Customer" in document["content"]


def test_retrieve_customer_country_requirement():
    retriever = create_retriever()

    results = retriever.retrieve(
        query=(
            "Is country mandatory for customer creation?"
        ),
        requesting_agent="RequirementsAgent",
        task_id="TASK-RAG-001",
    )

    assert len(results) > 0

    knowledge_ids = [
        result["knowledge_id"]
        for result in results
    ]

    assert "KNOW-CUST-001" in knowledge_ids


def test_retrieval_contains_traceability():
    retriever = create_retriever()

    results = retriever.retrieve(
        query="duplicate customer validation",
        requesting_agent="TestDesignAgent",
        task_id="TASK-RAG-002",
    )

    assert len(results) > 0

    trace = results[0]["retrieval_trace"]

    assert trace["task_id"] == "TASK-RAG-002"
    assert (
        trace["requesting_agent"]
        == "TestDesignAgent"
    )
    assert trace["query"] == (
        "duplicate customer validation"
    )
    assert trace["retrieval_reason"]


def test_empty_query_is_rejected():
    retriever = create_retriever()

    try:
        retriever.retrieve(
            query="",
            requesting_agent="RequirementsAgent",
            task_id="TASK-RAG-003",
        )

        assert False, "Expected ValueError"

    except ValueError as error:
        assert "empty" in str(error).lower()

from rag.authority import (
    AuthorityLevel,
    get_authority_level,
    rank_documents,
)

from rag.conflict_detector import (
    detect_country_requirement_conflict,
)


def test_requirement_has_highest_authority():
    assert (
        get_authority_level(
            "AUTHORITATIVE_REQUIREMENT_BASELINE"
        )
        == AuthorityLevel.REQUIREMENT
    )


def test_authority_ranking():
    documents = [
        {
            "knowledge_id": "TEST",
            "authority": "TEST_BASELINE",
            "retrieval_priority": 3,
        },
        {
            "knowledge_id": "SRS",
            "authority": "AUTHORITATIVE_REQUIREMENT_BASELINE",
            "retrieval_priority": 1,
        },
        {
            "knowledge_id": "API",
            "authority": "API_CONTRACT_BASELINE",
            "retrieval_priority": 2,
        },
    ]

    ranked = rank_documents(documents)

    assert ranked[0]["knowledge_id"] == "SRS"
    assert ranked[1]["knowledge_id"] == "API"
    assert ranked[2]["knowledge_id"] == "TEST"


def test_country_requirement_conflict():
    documents = [
        {
            "knowledge_id": "SRS",
            "document_name": "SRS v1.md",
            "authority": "AUTHORITATIVE_REQUIREMENT_BASELINE",
            "content": "Country is mandatory.",
        },
        {
            "knowledge_id": "API",
            "document_name": "customer_api.yaml",
            "authority": "API_CONTRACT_BASELINE",
            "content": "Country is optional.",
        },
    ]

    result = detect_country_requirement_conflict(documents)

    assert result["conflict_detected"] is True
    assert result["human_approval_required"] is True
    assert len(result["findings"]) == 2

def test_retrieval_with_governance_detects_conflict():
    from rag.retriever import KnowledgeRetriever
    from rag.metadata import KnowledgeMetadata
    from rag.knowledge_store import KnowledgeStore

    metadata_registry = KnowledgeMetadata(
        "rag/knowledge_metadata.json"
    )

    knowledge_store = KnowledgeStore(
        ".",
        metadata_registry
    )

    retriever = KnowledgeRetriever(
        knowledge_store
    )

    result = retriever.retrieve_with_governance(
        query="country mandatory optional",
        requesting_agent="RequirementsAgent",
        task_id="TASK-001",
        top_k=5,
    )

    assert "evidence" in result
    assert "conflict" in result
    assert result["conflict"]["conflict_detected"] is True
    assert result["human_approval_required"] is True
    assert (
        result["recommended_action"]
        == "WAIT_FOR_HUMAN_APPROVAL"
    )