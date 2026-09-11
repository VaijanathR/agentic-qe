import json
from pathlib import Path

from agents.base_agent import BaseAgent
from memory.task_result import TaskResult
from automation.api_operation_resolver import APIOperationResolver
from automation.api_automation_generator import APIAutomationGenerator
from automation.test_data_resolver import TestDataResolver
from automation.api_test_renderer import APITestRenderer


class AutomationAgent(BaseAgent):
    """
    Coordinates automation specification generation from the
    approved testcase baseline.

    The agent orchestrates:
        Testcase -> Operation Resolver -> API Contract Generator

    Actual execution is delegated to the Execution Agent.
    """

    __test__ = False

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.operation_resolver = APIOperationResolver()
        self.api_generator = APIAutomationGenerator(
            self.project_root / "technical_docs" / "customer_api.yaml"
        )
        self.test_data_resolver = TestDataResolver(project_root)
        self.test_renderer = APITestRenderer(project_root)

    @property
    def name(self):
        return "AutomationAgent"

    def _load_testcases(self):
        testcase_file = self.project_root / "testcases" / "testcases.json"

        with testcase_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            testcases = data.get("testcases", [])

            if isinstance(testcases, list):
                return testcases

        return []

    def _identify_candidates(self, testcases):
        candidates = []

        for testcase in testcases:
            automation_status = (
                str(testcase.get("automation_status", ""))
                .strip()
                .lower()
            )

            if automation_status in {
                "yes",
                "candidate",
                "automatable",
                "automation candidate",
            }:
                candidates.append(testcase)

        return candidates

    def _identify_agentic_cases(self, testcases):
        agentic_cases = []

        for testcase in testcases:
            automation_status = (
                str(testcase.get("automation_status", ""))
                .strip()
                .lower()
            )

            category = (
                str(testcase.get("category", ""))
                .strip()
                .lower()
            )

            if (
                automation_status == "agentic"
                or category.startswith("agentic")
            ):
                agentic_cases.append(testcase)

        return agentic_cases

    def _determine_automation_type(self, testcase):
        category = str(testcase.get("category", "")).lower()
        objective = str(testcase.get("objective", "")).lower()

        combined = f"{category} {objective}"

        if "performance" in combined:
            return "PERFORMANCE"

        if "security" in combined or "penetration" in combined:
            return "SECURITY"

        if "ui" in combined or "browser" in combined:
            return "UI"

        return "API"

    def _write_artifact(self, task_id, artifact):
        run_directory = self.project_root / "runs" / task_id
        run_directory.mkdir(parents=True, exist_ok=True)

        artifact_file = run_directory / "automation.json"

        with artifact_file.open("w", encoding="utf-8") as file:
            json.dump(artifact, file, indent=2)

        return artifact_file

    def execute(self, task):
        testcases = self._load_testcases()

        candidates = self._identify_candidates(testcases)
        agentic_cases = self._identify_agentic_cases(testcases)

        automation_items = []
        api_automation_items = []
        unresolved_items = []

        for testcase in candidates:
            automation_type = self._determine_automation_type(testcase)

            test_data_ids = testcase.get("test_data_ids", [])
            resolved_test_data = self.test_data_resolver.resolve(test_data_ids)

            item = {
                "testcase_id": testcase.get("testcase_id"),
                "requirement_id": testcase.get("requirement_id"),
                "automation_type": automation_type,
                "title": testcase.get("title"),
                "objective": testcase.get("objective"),
                "steps": testcase.get("steps", []),
                "expected_result": testcase.get("expected_result"),
                "test_data_ids": test_data_ids,
                "resolved_test_data": resolved_test_data,
                "status": "IDENTIFIED",
            }

            automation_items.append(item)

            # API automation is generated from the OpenAPI contract.
            if automation_type == "API":
                resolution = self.operation_resolver.resolve(testcase)

                if resolution is None:
                    continue

                if resolution.get("resolution") == "UNRESOLVED":
                    unresolved_items.append({
                        "testcase_id": testcase.get("testcase_id"),
                        "requirement_id": testcase.get("requirement_id"),
                        "title": testcase.get("title"),
                        "reason": resolution.get("reason"),
                    })
                    continue

                generated = self.api_generator.generate_for_testcase(
                    testcase,
                    resolution["path"],
                    resolution["method"],
                )

                rendered_code = self.test_renderer.render(
                    testcase,
                    generated,
                    resolved_test_data,
                )

                generated["generated_test_code"] = rendered_code
                generated["render_status"] = "GENERATED"
                generated["resolution"] = resolution["resolution"]
                generated["test_data_ids"] = test_data_ids
                generated["resolved_test_data"] = resolved_test_data



                api_automation_items.append(generated)

        agentic_items = []

        for testcase in agentic_cases:
            agentic_items.append({
                "testcase_id": testcase.get("testcase_id"),
                "requirement_id": testcase.get("requirement_id"),
                "title": testcase.get("title"),
                "category": testcase.get("category"),
                "status": "DEFERRED_TO_AGENTIC_QE_LAYER",
            })

        artifact = {
            "task_id": task.task_id,
            "status": "COMPLETED",
            "input_testcase_count": len(testcases),
            "automation_candidate_count": len(candidates),
            "automation_items": automation_items,
            "api_automation_items": api_automation_items,
            "api_automation_count": len(api_automation_items),
            "rendered_api_automation_count": sum(
                1
                for item in api_automation_items
                if item.get("render_status") == "GENERATED"
            ),
            "agentic_items": agentic_items,
            "agentic_case_count": len(agentic_items),
            "unresolved_items": unresolved_items,
            "unresolved_count": len(unresolved_items),
            "execution_deferred": True,
            "evidence": [
                "Approved testcase baseline consumed as read-only input",
                "Automation candidates identified from approved testcase metadata",
                "Approved test-data IDs resolved deterministically",
                "Resolved approved test data carried into automation specifications",
                "Agentic QE cases separated from executable API automation",
                "API operations resolved deterministically",
                "OpenAPI contract used to generate API automation specifications",
                "Actual test execution is delegated to the Execution Agent",
                "API automation specifications rendered into executable pytest + requests code", 
            ],
        }

        artifact_file = self._write_artifact(
            task.task_id,
            artifact,
        )

        findings = [
            f"Loaded {len(testcases)} approved testcase(s)",
            f"Identified {len(candidates)} conventional automation candidate(s)",
            f"Identified {len(agentic_cases)} Agentic QE case(s)",
            f"Generated {len(api_automation_items)} API automation specification(s)",
            f"Found {len(unresolved_items)} unresolved automation mapping(s)",
            "Approved testcase baseline was treated as read-only",
            "Approved test data was resolved without modification",
            "Automation execution was not performed",
            f"Persisted automation artifact: {artifact_file}",
        ]

        return TaskResult(
            task_id=task.task_id,
            source_agent=self.name,
            objective=task.objective,
            status="COMPLETED",
            activities=[
                "Loaded approved testcase baseline",
                "Resolved approved test-data references",
                "Separated conventional and Agentic QE automation cases",
                "Resolved API operations",
                "Generated API automation specifications",
                "Persisted automation specification artifact",
            ],
            findings=findings,
            evidence=[str(artifact_file)],
            confidence="HIGH",
            human_approval_required=False,
            next_action=(
                "Review generated automation specifications and "
                "proceed to automation execution"
            ),
        )