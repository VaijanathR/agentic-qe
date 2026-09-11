# Stores and indexes approved project knowledge (requirements, technical docs) for local retrieval.
from pathlib import Path


class KnowledgeStore:
    """
    Provides access to the actual content of registered knowledge documents.
    """

    def __init__(self, project_root, metadata_registry):
        self.project_root = Path(project_root)
        self.metadata_registry = metadata_registry

    def get_document(self, knowledge_id):
        metadata = self.metadata_registry.get_by_id(
            knowledge_id
        )

        if metadata is None:
            raise KeyError(
                f"Knowledge ID not found: {knowledge_id}"
            )

        relative_path = metadata.get("path")

        if not relative_path:
            raise ValueError(
                f"Document path missing for {knowledge_id}"
            )

        document_path = self.project_root / relative_path

        if not document_path.exists():
            raise FileNotFoundError(
                f"Knowledge document not found: {document_path}"
            )

        content = document_path.read_text(
            encoding="utf-8"
        )

        return {
            "knowledge_id": metadata.get("knowledge_id"),
            "document_name": metadata.get("document_name"),
            "version": metadata.get("version"),
            "approval_status": metadata.get(
                "approval_status"
            ),
            "authority": metadata.get("authority_level"),
            "retrieval_priority": metadata.get(
                "retrieval_priority"
            ),
            "content": content,
        }