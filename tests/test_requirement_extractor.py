from agents.requirement_extractor import (
    RequirementExtractor,
)


def test_requirement_extractor_extracts_structured_requirements():

    content = """
    CUST-CREATE-001: Authorized users can create a customer.
    CUST-CREATE-002: Duplicate customers must be rejected.
    AUTH-001: Authentication is required.
    PERF-001: Response time must be less than 8 seconds.
    """

    extractor = RequirementExtractor()

    requirements = extractor.extract(
        content=content,
        source_knowledge_id="KNOW-CUST-001",
        source_document="SRS v1.md",
    )

    assert len(requirements) == 4

    requirement_ids = [
        requirement.requirement_id
        for requirement in requirements
    ]

    assert "CUST-CREATE-001" in requirement_ids
    assert "CUST-CREATE-002" in requirement_ids
    assert "AUTH-001" in requirement_ids
    assert "PERF-001" in requirement_ids


def test_requirement_extractor_preserves_source():

    content = """
    CUST-CREATE-001: Authorized users can create a customer.
    """

    extractor = RequirementExtractor()

    requirements = extractor.extract(
        content=content,
        source_knowledge_id="KNOW-CUST-001",
        source_document="SRS v1.md",
    )

    assert len(requirements) == 1

    requirement = requirements[0]

    assert (
        requirement.source_knowledge_id
        == "KNOW-CUST-001"
    )

    assert (
        requirement.source_document
        == "SRS v1.md"
    )

def test_requirement_extractor_supports_new_requirement_category():

    content = """
    DATA-001: Test data must cover valid and invalid customer combinations.
    """

    extractor = RequirementExtractor()

    requirements = extractor.extract(
        content=content,
        source_knowledge_id="KNOW-CUST-001",
        source_document="SRS v1.md",
    )

    assert len(requirements) == 1

    requirement = requirements[0]

    assert requirement.requirement_id == "DATA-001"

    assert (
        requirement.source_knowledge_id
        == "KNOW-CUST-001"
    )