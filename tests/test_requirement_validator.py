from requirements.requirement_validator import RequirementValidator


def valid_requirement(requirement_id="CUST-CREATE-001"):
    return {
        "requirement_id": requirement_id,
        "title": "Create customer",
        "description": "Authorized users can create a customer.",
        "source_knowledge_id": "KNOW-CUST-001",
        "source_document": "SRS v1.md",
    }


def test_valid_requirement():
    validator = RequirementValidator()

    result = validator.validate(valid_requirement())

    assert result["valid"] is True
    assert result["errors"] == []


def test_missing_requirement_id():
    validator = RequirementValidator()

    requirement = valid_requirement()
    requirement["requirement_id"] = None

    result = validator.validate(requirement)

    assert result["valid"] is False
    assert "Requirement ID is missing" in result["errors"]


def test_invalid_requirement_id():
    validator = RequirementValidator()

    requirement = valid_requirement("INVALID")

    result = validator.validate(requirement)

    assert result["valid"] is False
    assert any(
        "Invalid requirement ID structure" in error
        for error in result["errors"]
    )


def test_missing_description():
    validator = RequirementValidator()

    requirement = valid_requirement()
    requirement["description"] = ""

    result = validator.validate(requirement)

    assert result["valid"] is False
    assert "Requirement description is missing" in result["errors"]


def test_missing_source():
    validator = RequirementValidator()

    requirement = valid_requirement()
    requirement["source_knowledge_id"] = None

    result = validator.validate(requirement)

    assert result["valid"] is False
    assert "Source knowledge ID is missing" in result["errors"]


def test_duplicate_requirement_ids():
    validator = RequirementValidator()

    requirements = [
        valid_requirement("REQ-001"),
        valid_requirement("REQ-002"),
        valid_requirement("REQ-001"),
    ]

    results = validator.validate_all(requirements)

    assert results[0]["valid"] is True
    assert results[1]["valid"] is True
    assert results[2]["valid"] is False
    assert "Duplicate requirement ID: REQ-001" in results[2]["errors"]