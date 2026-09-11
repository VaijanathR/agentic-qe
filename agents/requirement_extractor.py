import re

from requirements.requirement_model import Requirement


class RequirementExtractor:

    REQUIREMENT_PATTERN = re.compile(
        r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b"
    )

    def extract(
        self,
        content,
        source_knowledge_id,
        source_document,
    ):
        if not content or not content.strip():
            raise ValueError(
                "Requirement content cannot be empty"
            )

        requirements = []

        lines = content.splitlines()

        for line in lines:

            match = self.REQUIREMENT_PATTERN.search(
                line
            )

            if not match:
                continue

            requirement_id = match.group(0)

            description = line.strip()

            title = (
                description
                .split(":", 1)[-1]
                .strip()
            )

            requirement = Requirement(
                requirement_id=requirement_id,
                title=title,
                description=description,
                source_knowledge_id=source_knowledge_id,
                source_document=source_document,
            )

            requirements.append(requirement)

        return requirements

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