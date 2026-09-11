from enum import IntEnum


class AuthorityLevel(IntEnum):
    REQUIREMENT = 1
    TECHNICAL = 2
    QE_ARTIFACT = 3
    HISTORICAL = 4
    AGENT_INFERENCE = 5


AUTHORITY_MAP = {
    "AUTHORITATIVE_REQUIREMENT_BASELINE": AuthorityLevel.REQUIREMENT,
    "TECHNICAL_BASELINE": AuthorityLevel.TECHNICAL,
    "API_CONTRACT_BASELINE": AuthorityLevel.TECHNICAL,
    "TRACEABILITY_BASELINE": AuthorityLevel.QE_ARTIFACT,
    "TEST_BASELINE": AuthorityLevel.QE_ARTIFACT,
    "TEST_DATA_BASELINE": AuthorityLevel.QE_ARTIFACT,
    "HISTORICAL_EVIDENCE": AuthorityLevel.HISTORICAL,
    "HISTORICAL_EXECUTION_EVIDENCE": AuthorityLevel.HISTORICAL,
}


def get_authority_level(authority):
    """
    Return the authority level for a knowledge document.

    Lower numeric value = higher authority.
    Unknown authority is treated as lowest confidence.
    """
    return AUTHORITY_MAP.get(
        authority,
        AuthorityLevel.AGENT_INFERENCE
    )


def compare_authority(document_a, document_b):
    """
    Compare two knowledge documents.

    Returns:
        -1 if A has higher authority
         0 if equal
         1 if B has higher authority
    """
    level_a = get_authority_level(document_a.get("authority"))
    level_b = get_authority_level(document_b.get("authority"))

    if level_a < level_b:
        return -1

    if level_a > level_b:
        return 1

    return 0


def rank_documents(documents):
    """
    Rank documents using authority first and retrieval priority second.
    """
    return sorted(
        documents,
        key=lambda document: (
            get_authority_level(document.get("authority")),
            document.get("retrieval_priority", 999)
        )
    )