class APIOperationResolver:
    """
    Resolves an approved testcase to an API operation.

    Resolution is deterministic and based on testcase intent.
    Ambiguous cases are returned as unresolved rather than guessed.
    """

    def resolve(self, testcase):
        testcase_id = str(testcase.get("testcase_id", "")).strip()
        category = str(testcase.get("category", "")).strip().lower()
        title = str(testcase.get("title", "")).strip().lower()

        # Agentic QE scenarios are not API automation candidates.
        if category in {
            "agentic behavior",
            "agentic governance",
            "governance",
            "agentic execution",
            "failure analysis",
        }:
            return None

        # Create/customer creation flows
        if testcase_id in {
            "TC-CUST-001",
            "TC-CUST-002",
            "TC-CUST-003",
            "TC-CUST-004",
            "TC-CUST-005",
            "TC-CUST-006",
            "TC-CUST-007",
            "TC-CUST-008",
            "TC-CUST-009",
            "TC-CUST-010",
            "TC-CUST-012",
            "TC-CUST-013",
            "TC-CUST-014",
            "TC-CUST-028",
            "TC-CUST-029",
            "TC-CUST-030",
            "TC-CUST-031",
            "TC-CUST-032",
            "TC-CUST-034",
        }:
            return {
                "path": "/customers",
                "method": "POST",
                "resolution": "DETERMINISTIC_TESTCASE_MAPPING",
            }

        # Create then retrieve
        if testcase_id == "TC-CUST-011":
            return {
                "path": "/customers/{customerId}",
                "method": "GET",
                "resolution": "RETRIEVE_CREATED_CUSTOMER",
            }

        # Retrieve flows
        if category == "retrieve":
            return {
                "path": "/customers/{customerId}",
                "method": "GET",
                "resolution": "CATEGORY_MAPPING",
            }

        # Update flows
        if category == "update":
            return {
                "path": "/customers/{customerId}",
                "method": "PUT",
                "resolution": "CATEGORY_MAPPING",
            }

        # Update-related validation / duplicate / ID immutability
        if testcase_id in {
            "TC-CUST-019",
            "TC-CUST-020",
            "TC-CUST-021",
            "TC-CUST-022",
        }:
            return {
                "path": "/customers/{customerId}",
                "method": "PUT",
                "resolution": "DETERMINISTIC_TESTCASE_MAPPING",
            }

        # Performance test is primarily an execution concern.
        if category == "performance":
            return {
                "path": "/customers",
                "method": "POST",
                "resolution": "PERFORMANCE_CREATE_OPERATION",
            }

        # Security scenarios may span multiple operations.
        if category in {"security", "authentication", "authorization"}:
            return {
                "path": "/customers",
                "method": "POST",
                "resolution": "SECURITY_CREATE_OPERATION",
            }

        # Response validation is an API response concern.
        if category == "response validation":
            return {
                "path": "/customers",
                "method": "POST",
                "resolution": "RESPONSE_VALIDATION_CREATE_OPERATION",
            }

        # Anything not confidently resolved must be surfaced.
        return {
            "path": None,
            "method": None,
            "resolution": "UNRESOLVED",
            "reason": (
                f"No deterministic API operation mapping for "
                f"{testcase.get('testcase_id')}: "
                f"{testcase.get('title')}"
            ),
        }