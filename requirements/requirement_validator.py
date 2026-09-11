import re


class RequirementValidator:

    REQUIREMENT_ID_PATTERN = re.compile(
        r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+$"
    )

    def validate(self, requirement):
        errors = []

        requirement_id = requirement.get("requirement_id")
        title = requirement.get("title")
        description = requirement.get("description")
        source_knowledge_id = requirement.get("source_knowledge_id")
        source_document = requirement.get("source_document")

        if not requirement_id:
            errors.append("Requirement ID is missing")
        elif not isinstance(requirement_id, str):
            errors.append("Requirement ID must be a string")
        elif not self.REQUIREMENT_ID_PATTERN.match(requirement_id):
            errors.append(
                f"Invalid requirement ID structure: {requirement_id}"
            )

        if not description or not str(description).strip():
            errors.append("Requirement description is missing")

        if title is not None and not isinstance(title, str):
            errors.append("Requirement title must be a string")

        if not source_knowledge_id:
            errors.append("Source knowledge ID is missing")

        if not source_document:
            errors.append("Source document is missing")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "requirement_id": requirement_id,
        }

    def validate_all(self, requirements):
        results = []
        seen_ids = set()

        for requirement in requirements:
            result = self.validate(requirement)

            requirement_id = result["requirement_id"]

            if requirement_id in seen_ids:
                result["valid"] = False
                result["errors"].append(
                    f"Duplicate requirement ID: {requirement_id}"
                )

            if requirement_id:
                seen_ids.add(requirement_id)

            results.append(result)

        return results