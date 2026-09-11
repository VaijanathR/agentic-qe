from enum import Enum


class RetrievalScope(str, Enum):
    REQUIREMENT = "REQUIREMENT"
    TECHNICAL = "TECHNICAL"
    QE = "QE"
    HISTORICAL = "HISTORICAL"
    ALL = "ALL"


AUTHORITY_TO_SCOPE = {
    "AUTHORITATIVE_REQUIREMENT_BASELINE": RetrievalScope.REQUIREMENT,
    "TECHNICAL_BASELINE": RetrievalScope.TECHNICAL,
    "API_CONTRACT_BASELINE": RetrievalScope.TECHNICAL,
    "TRACEABILITY_BASELINE": RetrievalScope.QE,
    "TEST_BASELINE": RetrievalScope.QE,
    "TEST_DATA_BASELINE": RetrievalScope.QE,
    "HISTORICAL_EVIDENCE": RetrievalScope.HISTORICAL,
    "HISTORICAL_EXECUTION_EVIDENCE": RetrievalScope.HISTORICAL,
}


def get_scope_for_authority(authority):
    return AUTHORITY_TO_SCOPE.get(authority)


def document_matches_scope(document, scope):
    if scope == RetrievalScope.ALL:
        return True

    document_scope = get_scope_for_authority(
        document.get("authority")
    )

    return document_scope == scope