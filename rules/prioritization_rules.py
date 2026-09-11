# Encodes deterministic rules for prioritizing test cases for execution.
MOSCOW_WEIGHT = {
    "MUST": 4,
    "SHOULD": 3,
    "COULD": 2,
    "WOULD": 1,
}


def calculate_risk_score(
    business_criticality,
    technical_complexity,
    probability_of_failure,
):
    """
    Risk Score =
        Business Criticality
        x Technical Complexity
        x Probability of Failure

    Each input must be between 1 and 5.

    Maximum score = 125.
    """

    values = {
        "business_criticality": business_criticality,
        "technical_complexity": technical_complexity,
        "probability_of_failure": probability_of_failure,
    }

    for name, value in values.items():
        if not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")

        if value < 1 or value > 5:
            raise ValueError(f"{name} must be between 1 and 5")

    return (
        business_criticality
        * technical_complexity
        * probability_of_failure
    )


def calculate_execution_priority(
    risk_score,
    moscow="MUST",
    historical_failure=False,
    security_relevant=False,
):
    """
    Produces a practical prioritization score.

    Risk remains the primary driver.

    Additional weight is given to:
    - MoSCoW importance
    - historical failures
    - security relevance
    """

    moscow = moscow.upper()

    if moscow not in MOSCOW_WEIGHT:
        raise ValueError(
            f"Invalid MoSCoW value: {moscow}"
        )

    priority_score = risk_score

    priority_score += MOSCOW_WEIGHT[moscow] * 5

    if historical_failure:
        priority_score += 15

    if security_relevant:
        priority_score += 20

    return priority_score


def prioritize_testcases(testcases):
    prioritized = []

    for testcase in testcases:
        risk_score = calculate_risk_score(
            testcase["business_criticality"],
            testcase["technical_complexity"],
            testcase["probability_of_failure"],
        )

        execution_priority = calculate_execution_priority(
            risk_score=risk_score,
            moscow=testcase.get("moscow", "MUST"),
            historical_failure=testcase.get(
                "historical_failure",
                False,
            ),
            security_relevant=testcase.get(
                "security_relevant",
                False,
            ),
        )

        enriched_testcase = testcase.copy()
        enriched_testcase["risk_score"] = risk_score
        enriched_testcase[
            "execution_priority"
        ] = execution_priority

        prioritized.append(enriched_testcase)

    return sorted(
        prioritized,
        key=lambda item: item["execution_priority"],
        reverse=True,
    )


if __name__ == "__main__":
    sample_testcases = [
        {
            "testcase_id": "TC-CUST-001",
            "business_criticality": 5,
            "technical_complexity": 3,
            "probability_of_failure": 3,
            "moscow": "MUST",
            "historical_failure": True,
            "security_relevant": False,
        },
        {
            "testcase_id": "TC-CUST-012",
            "business_criticality": 5,
            "technical_complexity": 4,
            "probability_of_failure": 4,
            "moscow": "MUST",
            "historical_failure": True,
            "security_relevant": True,
        },
    ]

    for testcase in prioritize_testcases(sample_testcases):
        print(testcase)