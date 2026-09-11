# Persists collected evidence in a non-overwritable, append-only manner.
from datetime import datetime, timezone


class EvidenceStore:
    def __init__(self):
        self.evidence = {}

    def add_evidence(
        self,
        evidence_id,
        task_id,
        source,
        evidence_type,
        description,
        content=None,
    ):
        if evidence_id in self.evidence:
            raise ValueError(
                f"Evidence already exists: {evidence_id}"
            )

        record = {
            "evidence_id": evidence_id,
            "task_id": task_id,
            "source": source,
            "evidence_type": evidence_type,
            "description": description,
            "content": content,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self.evidence[evidence_id] = record

        return record

    def get_evidence(self, evidence_id):
        if evidence_id not in self.evidence:
            raise KeyError(
                f"Evidence not found: {evidence_id}"
            )

        return self.evidence[evidence_id]

    def get_task_evidence(self, task_id):
        return [
            evidence
            for evidence in self.evidence.values()
            if evidence["task_id"] == task_id
        ]

    def count(self):
        return len(self.evidence)