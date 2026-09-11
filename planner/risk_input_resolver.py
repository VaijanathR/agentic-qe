class RiskInputResolver:
    """
    Validates whether the information required for deterministic
    risk prioritization is available.

    This component does not invent risk values and does not
    modify approved testcase data.
    """

    REQUIRED_FIELDS = (
        "business_criticality",
        "technical_complexity",
        "probability_of_failure",
    )

    def resolve(self, testcase):
        missing_fields = [
            field
            for field in self.REQUIRED_FIELDS
            if field not in testcase
            or testcase[field] is None
        ]

        if missing_fields:
            return {
                "status": "BLOCKED",
                "testcase_id": testcase.get(
                    "testcase_id"
                ),
                "risk_inputs": {},
                "missing_fields": missing_fields,
                "reason": (
                    "Required risk inputs are unavailable; "
                    "no risk values were invented"
                ),
            }

        return {
            "status": "RESOLVED",
            "testcase_id": testcase.get(
                "testcase_id"
            ),
            "risk_inputs": {
                field: testcase[field]
                for field in self.REQUIRED_FIELDS
            },
            "missing_fields": [],
            "reason": None,
        }

    def resolve_all(self, testcases):
        results = [
            self.resolve(testcase)
            for testcase in testcases
        ]

        blocked = any(
            result["status"] == "BLOCKED"
            for result in results
        )

        return {
            "status": "BLOCKED" if blocked else "RESOLVED",
            "results": results,
        }