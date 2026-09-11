from rag.retrieval_scope import (
    RetrievalScope,
    document_matches_scope,
)


class ProgressiveRetriever:
    """
    Controls staged knowledge retrieval.

    Retrieval progresses from current authoritative
    knowledge toward broader evidence only when required.
    """

    def __init__(self, knowledge_retriever):
        self.knowledge_retriever = knowledge_retriever

    def retrieve_progressively(
        self,
        query,
        requesting_agent,
        task_id,
        initial_scope=RetrievalScope.REQUIREMENT,
        expand_scopes=None,
        top_k=5,        
    ):
        if not query or not query.strip():
            raise ValueError(
                "Retrieval query cannot be empty"
            )

        if expand_scopes is None:
            expand_scopes = [
                RetrievalScope.TECHNICAL,
                RetrievalScope.QE,
                RetrievalScope.HISTORICAL,
            ]

        scopes = [initial_scope] + [
            scope
            for scope in expand_scopes
            if scope != initial_scope
        ]

        all_evidence = []
        retrieval_stages = []

        for scope in scopes:
           
            results = self.knowledge_retriever.retrieve(
                query=query,
                requesting_agent=requesting_agent,
                task_id=task_id,
                top_k=top_k,
                scope=scope,
            )
                        
            scoped_results = [
                result
                for result in results
                if document_matches_scope(
                    result,
                    scope,
                )
            ]

            retrieval_stages.append(
                {
                    "scope": scope.value,
                    "documents_found": len(
                        scoped_results
                    ),
                }
            )

            for result in scoped_results:
                if not any(
                    existing["knowledge_id"]
                    == result["knowledge_id"]
                    for existing in all_evidence
                ):
                    all_evidence.append(result)

            if scoped_results:
                break

        return {
            "task_id": task_id,
            "requesting_agent": requesting_agent,
            "query": query,
            "evidence": all_evidence,
            "retrieval_stages": retrieval_stages,
            "initial_scope": initial_scope.value,
            "final_scope": (
                retrieval_stages[-1]["scope"]
                if retrieval_stages
                else None
            ),
            "evidence_found": bool(all_evidence),
        }