import re


def _normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def detect_country_requirement_conflict(documents):
    """
    Detect conflict regarding whether Country is mandatory or optional.

    This is intentionally deterministic for the MVP.
    An LLM can later generalize this capability.
    """

    findings = []

    for document in documents:
        content = _normalize(document.get("content", ""))

        mandatory_patterns = [
            r"country.*mandatory",
            r"country.*required",
            r"country.*must be provided",
        ]

        optional_patterns = [
            r"country.*optional",
            r"country.*not required",
            r"country.*may be omitted",
        ]

        mandatory = any(
            re.search(pattern, content)
            for pattern in mandatory_patterns
        )

        optional = any(
            re.search(pattern, content)
            for pattern in optional_patterns
        )

        if mandatory:
            findings.append({
                "knowledge_id": document.get("knowledge_id"),
                "document_name": document.get("document_name"),
                "position": "mandatory",
                "authority": document.get("authority"),
            })

        if optional:
            findings.append({
                "knowledge_id": document.get("knowledge_id"),
                "document_name": document.get("document_name"),
                "position": "optional",
                "authority": document.get("authority"),
            })

    positions = {finding["position"] for finding in findings}

    conflict = "mandatory" in positions and "optional" in positions

    return {
        "conflict_detected": conflict,
        "findings": findings,
        "human_approval_required": conflict,
        "reason": (
            "Approved sources contain conflicting Country requirements."
            if conflict
            else "No Country requirement conflict detected."
        ),
    }