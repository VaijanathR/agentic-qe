from datetime import datetime, timezone


class Decision:
    def __init__(
        self,
        decision_id,
        task_id,
        decision,
        rationale,
        evidence_ids=None,
        confidence=None,
        governance_level=None,
        human_approval_required=False,
        next_action=None,
    ):
        self.decision_id = decision_id
        self.task_id = task_id
        self.decision = decision
        self.rationale = rationale
        self.evidence_ids = evidence_ids or []
        self.confidence = confidence
        self.governance_level = governance_level
        self.human_approval_required = human_approval_required
        self.next_action = next_action
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def add_evidence(self, evidence_id):
        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)

    def to_dict(self):
        return {
            "decision_id": self.decision_id,
            "task_id": self.task_id,
            "decision": self.decision,
            "rationale": self.rationale,
            "evidence_ids": self.evidence_ids,
            "confidence": self.confidence,
            "governance_level": self.governance_level,
            "human_approval_required": self.human_approval_required,
            "next_action": self.next_action,
            "timestamp": self.timestamp,
        }