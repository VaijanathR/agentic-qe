from pathlib import Path


class APITestRenderer:
    """
    Renders an API automation specification into executable
    pytest + requests test code.

    Responsibilities:
    - Convert an already-resolved API automation specification
      into executable test code.
    - Preserve testcase intent and expected-result evidence.
    - Never execute the generated test.
    - Never invent an expected HTTP status.
    """

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)

    def _resolve_expected_status(self, testcase):
        """
        Resolve the expected HTTP status only when the approved testcase
        contains exactly one explicit HTTP status.

        If multiple HTTP statuses are present, the testcase is treated
        as a multi-step or multi-outcome flow and the renderer does not
        guess which status belongs to the current operation.

        Returns:
            int when exactly one deterministic status is identified
            None when status is absent or ambiguous
        """
        expected_result = testcase.get("expected_result", [])

        if isinstance(expected_result, str):
            expected_result = [expected_result]

        statuses = []

        for result in expected_result:
            text = str(result).strip().upper()

            for status in (200, 201, 400, 401, 403, 404, 409, 500):
                if f"HTTP {status}" in text:
                    statuses.append(status)

        unique_statuses = list(dict.fromkeys(statuses))

        if len(unique_statuses) == 1:
            return unique_statuses[0]

        return None

    def _flatten_resolved_data(self, resolved_test_data):
        """
        Build a deterministic lookup of approved resolved test data.

        The resolver remains responsible for locating approved data.
        The renderer only consumes the already-resolved records.
        """
        flattened = {}

        for record in resolved_test_data:
            if not isinstance(record, dict):
                continue

            data_id = record.get("data_id")
            data = record.get("data", {})

            if data_id and isinstance(data, dict):
                flattened[data_id] = data

        return flattened

    def render(self, testcase, automation_spec, resolved_test_data=None):
        """
        Render one testcase into executable pytest + requests code.
        """

        testcase_id = testcase.get("testcase_id")
        title = testcase.get("title", "")
        objective = testcase.get("objective", "")
        resolved_test_data = resolved_test_data or []
        resolved_data = self._flatten_resolved_data(
            resolved_test_data
            )

        method = automation_spec.get("http_method")
        endpoint = automation_spec.get("endpoint")

        if not method:
            raise ValueError(
                f"Missing HTTP method for {testcase_id}"
            )

        if not endpoint:
            raise ValueError(
                f"Missing API endpoint for {testcase_id}"
            )

        expected_status = self._resolve_expected_status(testcase)

        method = method.upper()

        function_name = (
            str(testcase_id)
            .lower()
            .replace("-", "_")
        )

        lines = [
            "import os",
            "",
            "import requests",
            "",
            "",
            'BASE_URL = os.getenv("CUSTOMER_API_BASE_URL", "http://localhost:8000")',
            'AUTH_TOKEN = os.getenv("CUSTOMER_API_TOKEN")',
            "",
            "",
            f"def test_{function_name}():",
            f'    """{objective}"""',
            "",
            f'    endpoint = "{endpoint}"',
            "    headers = {}",
            "",
            "    if AUTH_TOKEN:",
            '        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"',
            "",
        ]

        if method == "GET":
            if "{customerId}" in endpoint:
                customer_id = self._resolve_customer_id(resolved_data)

                if customer_id is not None:
                    lines.extend([
                        f'    endpoint = "{endpoint.replace("{customerId}", str(customer_id))}"',
                    ])
                else:
                    lines.extend([
                        "    # Runtime customerId dependency was not resolved.",
                        "    # Execution must be blocked rather than using an invented ID.",
                        "    customer_id = None",
                        "    if customer_id is None:",
                        "        raise RuntimeError(",
                        '            "Required customerId was not resolved from approved test data"',
                        "        )",
                        "    endpoint = endpoint.replace(",
                        '        "{customerId}",',
                        "        str(customer_id),",
                        "    )",
                    ])

            lines.extend([
                '    response = requests.get(',
                "        f\"{BASE_URL}{endpoint}\",",
                "        headers=headers,",
                "        timeout=8,",
                "    )",
            ])        

        elif method == "POST":
            lines.extend(
                [
                    "    payload = {",
                    '        "customerName": "AUTO-GENERATED-TEST-CUSTOMER",',
                    '        "country": "India",',
                    "    }",
                    "",
                    '    response = requests.post(',
                    "        f\"{BASE_URL}{endpoint}\",",
                    "        json=payload,",
                    "        headers=headers,",
                    "        timeout=8,",
                    "    )",
                ]
            )

        elif method == "PUT":
            lines.extend(
                [
                    "    payload = {",
                    '        "customerName": "AUTO-GENERATED-TEST-CUSTOMER",',
                    '        "country": "India",',
                    "    }",
                    "",
                    '    response = requests.put(',
                    "        f\"{BASE_URL}{endpoint}\",",
                    "        json=payload,",
                    "        headers=headers,",
                    "        timeout=8,",
                    "    )",
                ]
            )

        else:
            raise ValueError(
                f"Unsupported HTTP method for {testcase_id}: {method}"
            )

        lines.extend(
            [
                "",
                "    assert response is not None",
            ]
        )

        if expected_status is not None:
            lines.extend(
                [
                    f"    assert response.status_code == {expected_status}",
                ]
            )
        else:
            lines.extend(
                [
                    "    # Expected HTTP status is not explicitly stated",
                    "    # in the approved testcase baseline.",
                    "    # Status assertion intentionally deferred.",
                ]
            )

        lines.extend(
            [
                "",
            ]
        )

        return "\n".join(lines)

    def _resolve_customer_id(self, resolved_data):
        """
        Resolve an approved customerId from resolved test data.

        Returns None when the approved data does not contain a
        usable customerId. The renderer must never invent one.
        """
        for data in resolved_data.values():
            customer_id = data.get("customerId")

            if customer_id is not None:
                return customer_id

            customer_id = data.get("customer_id")

            if customer_id is not None:
                return customer_id

        return None