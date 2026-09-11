from memory.decision import Decision


class DecisionManager:
    def __init__(self):
        self.decisions = {}

    def create_decision(self, decision):
        if not isinstance(decision, Decision):
            raise TypeError("decision must be a Decision object")

        if decision.decision_id in self.decisions:
            raise ValueError(
                f"Decision already exists: {decision.decision_id}"
            )

        self.decisions[decision.decision_id] = decision
        return decision

    def get_decision(self, decision_id):
        if decision_id not in self.decisions:
            raise KeyError(f"Decision not found: {decision_id}")

        return self.decisions[decision_id]

    def get_task_decisions(self, task_id):
        return [
            decision
            for decision in self.decisions.values()
            if decision.task_id == task_id
        ]

    def count(self):
        return len(self.decisions)