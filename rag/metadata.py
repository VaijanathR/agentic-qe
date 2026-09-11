# Tracks metadata (source, approval status, version) for documents in the knowledge store.
import json
from pathlib import Path


class KnowledgeMetadata:
    """
    Loads and provides access to the knowledge metadata registry.
    """

    def __init__(self, metadata_file):
        self.metadata_file = Path(metadata_file)
        self.documents = self._load()

    def _load(self):
        if not self.metadata_file.exists():
            raise FileNotFoundError(
                f"Knowledge metadata file not found: {self.metadata_file}"
            )

        with self.metadata_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data.get("knowledge_documents", [])

    def get_all(self):
        return self.documents

    def get_approved(self):
        return [
            document
            for document in self.documents
            if document.get("approval_status", "").lower()
            == "approved"
        ]

    def get_by_id(self, knowledge_id):
        for document in self.documents:
            if document.get("knowledge_id") == knowledge_id:
                return document

        return None