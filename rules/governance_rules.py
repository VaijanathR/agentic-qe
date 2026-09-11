# Encodes deterministic governance boundaries (GREEN/YELLOW/RED autonomy rules) and approval gates.
from enum import Enum


class GovernanceLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class GovernanceRules:
    """
    Deterministic governance rules for the Agentic QE system.

    GREEN  = Agent may proceed autonomously.
    YELLOW = Human approval is required.
    RED    = Action is restricted and must not be performed.
    """

    GREEN_ACTIONS = {
        "READ_APPROVED_DOCUMENT",
        "RETRIEVE_KNOWLEDGE",
        "GENERATE_CANDIDATE_TESTCASE",
        "GENERATE_TEST_DATA",
        "EXECUTE_APPROVED_TEST",
        "COLLECT_EVIDENCE",
        "ANALYZE_FAILURE",
        "GENERATE_REPORT",
        "CALCULATE_PRIORITY",
        "PERFORM_IMPACT_ANALYSIS",
        "CONTINUE_INDEPENDENT_WORK",
    }

    YELLOW_ACTIONS = {
        "MODIFY_APPROVED_TESTCASE",
        "CHANGE_REQUIREMENT_BASELINE",
        "RESOLVE_APPROVED_SOURCE_CONFLICT",
        "CHANGE_BUSINESS_RULE",
        "SECURITY_EXCEPTION",
        "APPROVE_REPLAN",
        "EXPAND_AGENT_AUTONOMY",
    }

    RED_ACTIONS = {
        "DELETE_ARTIFACT",
        "UNAUTHORIZED_PRODUCTION_CHANGE",
        "BYPASS_SECURITY",
        "BYPASS_AUTHORIZATION",
        "ALTER_RESULT_TO_FORCE_PASS",
        "SILENTLY_OVERWRITE_HISTORY",
        "UNAUTHORIZED_SECURITY_ACTION",
    }

    def evaluate(self, action: str) -> dict:
        action = action.strip().upper()

        if action in self.RED_ACTIONS:
            return {
                "action": action,
                "governance_level": GovernanceLevel.RED.value,
                "allowed": False,
                "human_approval_required": False,
                "reason": "Restricted action. The Agentic QE system must not perform it.",
            }

        if action in self.YELLOW_ACTIONS:
            return {
                "action": action,
                "governance_level": GovernanceLevel.YELLOW.value,
                "allowed": False,
                "human_approval_required": True,
                "reason": "Human approval is required before this action may proceed.",
            }

        if action in self.GREEN_ACTIONS:
            return {
                "action": action,
                "governance_level": GovernanceLevel.GREEN.value,
                "allowed": True,
                "human_approval_required": False,
                "reason": "Action is within approved autonomous boundaries.",
            }

        return {
            "action": action,
            "governance_level": GovernanceLevel.YELLOW.value,
            "allowed": False,
            "human_approval_required": True,
            "reason": (
                "Action is not explicitly classified. "
                "Defaulting to human governance."
            ),
        }


if __name__ == "__main__":
    rules = GovernanceRules()

    sample_actions = [
        "READ_APPROVED_DOCUMENT",
        "MODIFY_APPROVED_TESTCASE",
        "DELETE_ARTIFACT",
        "UNKNOWN_ACTION",
    ]

    for sample_action in sample_actions:
        print(rules.evaluate(sample_action))