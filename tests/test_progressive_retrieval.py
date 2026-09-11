from rag.metadata import KnowledgeMetadata
from rag.knowledge_store import KnowledgeStore
from rag.retriever import KnowledgeRetriever
from rag.progressive_retriever import ProgressiveRetriever
from rag.retrieval_scope import RetrievalScope


def create_progressive_retriever():
    metadata_registry = KnowledgeMetadata(
        "rag/knowledge_metadata.json"
    )

    knowledge_store = KnowledgeStore(
        ".",
        metadata_registry
    )

    knowledge_retriever = KnowledgeRetriever(
        knowledge_store
    )

    return ProgressiveRetriever(
        knowledge_retriever
    )


def test_requirement_scope_retrieves_requirement():
    retriever = create_progressive_retriever()

    result = retriever.retrieve_progressively(
        query="customer country mandatory",
        requesting_agent="RequirementsAgent",
        task_id="TASK-PROG-001",
        initial_scope=RetrievalScope.REQUIREMENT,
    )

    assert result["evidence_found"] is True
    assert result["final_scope"] == "REQUIREMENT"

    assert any(
        item["authority"]
        == "AUTHORITATIVE_REQUIREMENT_BASELINE"
        for item in result["evidence"]
    )


def test_progressive_retrieval_expands_when_initial_scope_has_no_evidence():
    retriever = create_progressive_retriever()

    result = retriever.retrieve_progressively(
        query="OpenAPI schema endpoint contract",
        requesting_agent="TechnicalAgent",
        task_id="TASK-PROG-002",
        initial_scope=RetrievalScope.REQUIREMENT,
        expand_scopes=[
            RetrievalScope.TECHNICAL,
        ],
    )

    assert result["evidence_found"] is True
    assert result["final_scope"] == "TECHNICAL"

    assert any(
        item["authority"]
        in [
            "TECHNICAL_BASELINE",
            "API_CONTRACT_BASELINE",
        ]
        for item in result["evidence"]
    )


def test_progressive_retrieval_does_not_use_history_when_current_evidence_exists():
    retriever = create_progressive_retriever()

    result = retriever.retrieve_progressively(
        query="customer country mandatory",
        requesting_agent="RequirementsAgent",
        task_id="TASK-PROG-003",
        initial_scope=RetrievalScope.REQUIREMENT,
    )

    authorities = {
        item["authority"]
        for item in result["evidence"]
    }

    assert (
        "HISTORICAL_EVIDENCE"
        not in authorities
    )

    assert (
        "HISTORICAL_EXECUTION_EVIDENCE"
        not in authorities
    )


def test_retrieval_trace_is_preserved():
    retriever = create_progressive_retriever()

    result = retriever.retrieve_progressively(
        query="customer country mandatory",
        requesting_agent="RequirementsAgent",
        task_id="TASK-PROG-004",
    )

    for evidence in result["evidence"]:
        trace = evidence["retrieval_trace"]

        assert trace["task_id"] == "TASK-PROG-004"
        assert (
            trace["requesting_agent"]
            == "RequirementsAgent"
        )