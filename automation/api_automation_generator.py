import yaml


class APIAutomationGenerator:
    """
    Deterministically converts an OpenAPI contract and approved
    testcase metadata into executable API automation specifications.

    The generator does not invent API behavior. Endpoint, method,
    parameters, schemas, and response codes come from OpenAPI.
    """

    def __init__(self, openapi_file):
        self.openapi_file = openapi_file

    def _load_openapi(self):
        with self.openapi_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return yaml.safe_load(file)

    def _find_operation(self, path, method):
        spec = self._load_openapi()

        path_definition = spec.get(
            "paths",
            {},
        ).get(path)

        if not path_definition:
            raise ValueError(
                f"OpenAPI path not found: {path}"
            )

        operation = path_definition.get(
            method.lower()
        )

        if not operation:
            raise ValueError(
                f"OpenAPI method not found: "
                f"{method.upper()} {path}"
            )

        return operation

    def generate_for_testcase(
        self,
        testcase,
        path,
        method,
    ):
        operation = self._find_operation(
            path,
            method,
        )

        responses = operation.get(
            "responses",
            {},
        )

        return {
            "testcase_id": testcase.get(
                "testcase_id"
            ),
            "requirement_id": testcase.get(
                "requirement_id"
            ),
            "title": testcase.get(
                "title"
            ),
            "objective": testcase.get(
                "objective"
            ),
            "http_method": method.upper(),
            "endpoint": path,
            "operation_id": operation.get(
                "operationId"
            ),
            "summary": operation.get(
                "summary"
            ),
            "security_required": bool(
                operation.get("security")
            ),
            "request_body": operation.get(
                "requestBody"
            ),
            "parameters": operation.get(
                "parameters",
                [],
            ),
            "expected_responses": sorted(
                responses.keys()
            ),
            "automation_framework": (
                "pytest + requests"
            ),
            "status": "GENERATED",
        }