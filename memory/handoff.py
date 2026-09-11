from memory.task_result import TaskResult


class HandoffManager:
    def __init__(self):
        self.handoffs = {}

    def create_handoff(
        self,
        result,
        receiving_agent,
    ):
        if not isinstance(result, TaskResult):
            raise TypeError(
                "Handoff requires a TaskResult"
            )

        if not receiving_agent:
            raise ValueError(
                "Receiving agent is required"
            )

        handoff_id = (
            f"HANDOFF-{result.task_id}-{receiving_agent}"
        )

        if handoff_id in self.handoffs:
            raise ValueError(
                f"Handoff already exists: {handoff_id}"
            )

        handoff = {
            "handoff_id": handoff_id,
            "task_id": result.task_id,
            "source_agent": result.source_agent,
            "receiving_agent": receiving_agent,
            "objective": result.objective,
            "status": result.status,
            "activities": result.activities.copy(),
            "findings": result.findings.copy(),
            "evidence": result.evidence.copy(),
            "decisions": result.decisions.copy(),
            "dependencies": result.dependencies.copy(),
            "confidence": result.confidence,
            "human_approval_required": (
                result.human_approval_required
            ),
            "next_action": result.next_action,
        }

        self.handoffs[handoff_id] = handoff

        return handoff

    def get_handoff(self, handoff_id):
        if handoff_id not in self.handoffs:
            raise KeyError(
                f"Handoff not found: {handoff_id}"
            )

        return self.handoffs[handoff_id]