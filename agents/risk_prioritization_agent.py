import json
from pathlib import Path

from agents.base_agent import BaseAgent
from memory.task_result import TaskResult
from planner.prioritizer import TestPrioritizer


class RiskPrioritizationAgent(BaseAgent):
    """
    Agent responsible for orchestrating testcase risk prioritization.

    The approved testcase baseline is loaded as read-only input.
    Deterministic risk calculation remains inside TestPrioritizer.

    Missing or invalid risk inputs are never invented.
    """

    __test__ = False

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.prioritizer = TestPrioritizer()

    @property
    def name(self):
        return "RiskPrioritizationAgent"

    def _load_testcases(self):
        testcase_file = (
            self.project_root
            / "testcases"
            / "testcases.json"
        )

        with testcase_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            testcases = data.get("testcases", [])

            if isinstance(testcases, list):
                return testcases

        return []

    def _write_artifact(self, task_id, artifact):
        run_directory = (
            self.project_root
            / "runs"
            / task_id
        )

        run_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        artifact_file = (
            run_directory
            / "risk_prioritization.json"
        )

        with artifact_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                artifact,
                file,
                indent=2,
            )

        return artifact_file

    def execute(self, task):
        testcases = self._load_testcases()

        prioritization = self.prioritizer.prioritize(
            testcases
        )

        blocked_testcases = [
            result
            for result in prioritization[
                "risk_input_resolution"
            ]["results"]
            if result["status"] == "BLOCKED"
        ]

        status = prioritization["status"]

        human_approval_required = (
            status == "BLOCKED"
        )

        if status == "COMPLETED":
            next_action = (
                "Proceed to the next QE lifecycle activity "
                "using the prioritized testcase order"
            )
        else:
            next_action = (
                "Provide or resolve the missing risk inputs "
                "before risk prioritization can continue"
            )

        artifact = {
            "task_id": task.task_id,
            "status": status,
            "input_testcase_count": len(testcases),
            "risk_input_resolution": prioritization[
                "risk_input_resolution"
            ],
            "prioritized_testcases": prioritization[
                "prioritized_testcases"
            ],
            "blocked_testcases": blocked_testcases,
            "human_approval_required": (
                human_approval_required
            ),
            "reason": prioritization["reason"],
            "next_action": next_action,
            "evidence": [
                "Approved testcase baseline consumed as read-only input",
                "RiskInputResolver result",
                "Deterministic TestPrioritizer result",
            ],
        }

        artifact_file = self._write_artifact(
            task.task_id,
            artifact,
        )

        findings = [
            (
                f"Risk prioritization processed "
                f"{len(testcases)} testcase(s)"
            ),
            f"Risk prioritization status: {status}",
            (
                f"Risk prioritization blocked "
                f"{len(blocked_testcases)} testcase(s) "
                "due to unavailable risk inputs"
                if blocked_testcases
                else "All testcase risk inputs were available"
            ),
            "No risk values were invented",
            "Approved testcase baseline was treated as read-only",
            f"Persisted risk prioritization artifact: {artifact_file}",
        ]

        return TaskResult(
            task_id=task.task_id,
            source_agent=self.name,
            objective=task.objective,
            status=status,
            activities=[
                "Loaded approved testcase baseline",
                "Validated testcase risk inputs",
                "Executed deterministic risk prioritization",
                "Captured prioritization and governance state",
                "Persisted risk prioritization artifact",
            ],
            findings=findings,
            evidence=[
                str(artifact_file)
            ],
            confidence="HIGH",
            human_approval_required=(
                human_approval_required
            ),
            next_action=next_action,
        )