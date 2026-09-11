from requirements.requirement_model import Requirement


def test_requirement_to_dict():
    requirement = Requirement(
        requirement_id="CUST-CREATE-001",
        title="Create customer",
        description="Authenticated users can create a customer.",
        source_knowledge_id="KNOW-CUST-001",
        source_document="SRS v1.md",
    )

    data = requirement.to_dict()

    assert data["requirement_id"] == "CUST-CREATE-001"
    assert data["title"] == "Create customer"
    assert (
        data["source_knowledge_id"]
        == "KNOW-CUST-001"
    )
    assert (
        data["source_document"]
        == "SRS v1.md"
    )