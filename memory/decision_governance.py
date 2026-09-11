from rules.governance_rules import GovernanceRules


class DecisionGovernance:

    def __init__(self):
        self.governance_rules = GovernanceRules()

    def evaluate(self, decision):
        if not decision.next_action:
            raise ValueError("Decision next action is required")

        governance_result = self.governance_rules.evaluate(
            decision.next_action
        )

        return {
            "decision_id": decision.decision_id,
            "task_id": decision.task_id,
            "action": governance_result["action"],
            "governance_level": governance_result["governance_level"],
            "allowed": governance_result["allowed"],
            "human_approval_required": governance_result[
                "human_approval_required"
            ],
            "reason": governance_result["reason"],
        }