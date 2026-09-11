from planner.risk_input_resolver import (
    RiskInputResolver,
)
from rules.prioritization_rules import (
    prioritize_testcases,
)


class TestPrioritizer:
    """
    Coordinates risk-input validation and deterministic
    testcase prioritization.

    Missing risk inputs are never invented.
    Approved testcase records are never modified.
    """
    __test__ = False

    def __init__(self):
        self.risk_input_resolver = (
            RiskInputResolver()
        )

    def prioritize(self, testcases):
        resolution = (
            self.risk_input_resolver.resolve_all(
                testcases
            )
        )

        if resolution["status"] == "BLOCKED":
            return {
                "status": "BLOCKED",
                "prioritized_testcases": [],
                "risk_input_resolution": resolution,
                "reason": (
                    "Risk prioritization blocked because "
                    "required risk inputs are unavailable"
                ),
            }

        prioritized = prioritize_testcases(
            testcases
        )

        return {
            "status": "COMPLETED",
            "prioritized_testcases": prioritized,
            "risk_input_resolution": resolution,
            "reason": None,
        }