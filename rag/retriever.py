# Retrieves relevant approved knowledge from the knowledge store given a query or context.
from rag.authority import rank_documents
from rag.conflict_detector import detect_country_requirement_conflict
import re
from datetime import datetime, timezone
# Added for progressive retrieval:
# allows retrieval to be constrained to a specific knowledge scope.
from rag.retrieval_scope import (
    RetrievalScope,
    document_matches_scope,
) #this was added on 8th Sept 2026 20.42 IST

class KnowledgeRetriever:
    """
    Simple local keyword-based retriever for the Agentic QE MVP.

    Retrieval is governed by:
    - approval status
    - document authority
    - retrieval priority
    - query relevance

    This is intentionally not a vector database.
    """

    def __init__(self, knowledge_store):
        self.knowledge_store = knowledge_store

    @staticmethod
    def _tokenize(text):
        return set(
            re.findall(
                r"\b[a-zA-Z0-9_]+\b",
                text.lower(),
            )
        )

    def retrieve(
        self,
        query,
        requesting_agent,
        task_id,
        top_k=3,
        scope=None,
    ):
        if not query or not query.strip():
            raise ValueError(
                "Retrieval query cannot be empty"
            )

        query_terms = self._tokenize(query)

        candidates = []

        for metadata in (
            self.knowledge_store.metadata_registry.get_approved()
        ):
            document = self.knowledge_store.get_document(
                metadata["knowledge_id"]
            )

            if (
                scope is not None
                and not document_matches_scope(
                document,
                scope,
                )
                ):
                continue

            content_terms = self._tokenize(
                document["content"]
            )

            matching_terms = query_terms.intersection(
                content_terms
            )


            relevance_score = len(matching_terms)

            if relevance_score == 0:
                continue

            priority = metadata.get(
                "retrieval_priority",
                99,
            )

            candidates.append(
                {
                    "knowledge_id": metadata[
                        "knowledge_id"
                    ],
                    "document_name": metadata[
                        "document_name"
                    ],
                    "version": metadata.get(
                        "version"
                    ),
                    "approval_status": metadata.get(
                        "approval_status"
                    ),
                    "authority": metadata.get(
                        "authority_level" # Changed: knowledge metadata stores the authority classification
                                          # under "authority_level"; map it to the retriever's "authority" field.
                    ),
                    "retrieval_priority": priority,
                    "relevance_score": relevance_score,
                    "matching_terms": sorted(
                        matching_terms
                    ),
                    "content": document["content"],
                }
            )

        candidates.sort(
            key=lambda item: (
                -item["relevance_score"],
                item["retrieval_priority"],
            )
        )

        results = candidates[:top_k]

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        for result in results:
            result["retrieval_trace"] = {
                "task_id": task_id,
                "requesting_agent": requesting_agent,
                "query": query,
                "retrieval_reason": (
                    "Document retrieved because it is "
                    "approved knowledge and contains "
                    "terms relevant to the requested objective."
                ),
                "timestamp": timestamp,
            }

        return results
    
    def retrieve_with_governance(
    self,
    query,
    requesting_agent,
    task_id,
    top_k=5,
    ):

        """
        Retrieve relevant knowledge, rank by authority,
        detect conflicts, and determine governance requirements.
        """

        documents = self.retrieve(
            query=query,
            requesting_agent=requesting_agent,
            task_id=task_id,
            top_k=top_k,
        )

        ranked_documents = rank_documents(documents)

        conflict_result = detect_country_requirement_conflict(
            ranked_documents
        )

        return {
            "task_id": task_id,
            "requesting_agent": requesting_agent,
            "query": query,
            "evidence": ranked_documents,
            "conflict": conflict_result,
            "human_approval_required": conflict_result[
                "human_approval_required"
            ],
            "recommended_action": (
                "WAIT_FOR_HUMAN_APPROVAL"
                if conflict_result["human_approval_required"]
                else "CONTINUE"
            ),
        }