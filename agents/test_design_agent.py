import csv
import json
from pathlib import Path

from agents.base_agent import BaseAgent
from memory.task_result import TaskResult
from rag.metadata import KnowledgeMetadata
from rag.knowledge_store import KnowledgeStore
from rag.retriever import KnowledgeRetriever
from rag.retrieval_scope import (
    RetrievalScope,
    document_matches_scope,
)
from requirements.traceability import TraceabilityAnalyzer


__test__ = False


class TestDesignAgent(BaseAgent):
    """
    Agent responsible for preparing the knowledge required
    for test design and performing requirement-to-testcase
    traceability analysis.

    Approved baseline artifacts are read-only.
    Derived traceability analysis is produced separately.
    """

    __test__ = False

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)

        metadata_file = (
            self.project_root
            / "rag"
            / "knowledge_metadata.json"
        )

        metadata_registry = KnowledgeMetadata(metadata_file)

        knowledge_store = KnowledgeStore(
            self.project_root,
            metadata_registry,
        )

        self.retriever = KnowledgeRetriever(
            knowledge_store
        )

        self.traceability_analyzer = TraceabilityAnalyzer()

    @property
    def name(self):
        return "TestDesignAgent"

    def _retrieve_by_scope(
        self,
        query,
        scope,
        task_id,
    ):
        retrieval = self.retriever.retrieve(
            query=query,
            requesting_agent=self.name,
            task_id=task_id,
            top_k=10,
        )

        return [
            item
            for item in retrieval
            if document_matches_scope(item, scope)
        ]

    def _load_rtm(self):
        """
        Load the approved RTM baseline without modifying it.
        """

        rtm_file = (
            self.project_root
            / "requirements"
            / "RTM.csv"
        )

        with rtm_file.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            return list(csv.DictReader(file))

    def _load_testcases(self):
        """
        Load the approved testcase baseline without modifying it.
        """

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

    def _write_traceability_artifact(
        self,
        task_id,
        traceability,
    ):
        """
        Persist traceability analysis as a derived artifact.

        Approved baseline artifacts are never modified.
        """

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
            / "traceability_analysis.json"
        )

        with artifact_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                traceability,
                file,
                indent=2,
            )

        return artifact_file

    def execute(self, task):
        requirement_knowledge = self._retrieve_by_scope(
            query="customer requirements",
            scope=RetrievalScope.REQUIREMENT,
            task_id=task.task_id,
        )

        technical_knowledge = self._retrieve_by_scope(
            query="customer API OpenAPI technical specification",
            scope=RetrievalScope.TECHNICAL,
            task_id=task.task_id,
        )

        qe_knowledge = self._retrieve_by_scope(
            query="RTM approved testcases test design",
            scope=RetrievalScope.QE,
            task_id=task.task_id,
        )

        rtm_rows = self._load_rtm()
        testcases = self._load_testcases()

        requirements = []

        for item in requirement_knowledge:
            content = item.get("content")

            if isinstance(content, list):
                requirements.extend(content)

            elif isinstance(content, dict):
                requirements.append(content)

        traceability = self.traceability_analyzer.analyze(
            requirements=requirements,
            rtm_rows=rtm_rows,
            testcases=testcases,
        )

        traceability_artifact = (
            self._write_traceability_artifact(
                task.task_id,
                traceability,
            )
        )

        findings = [
            (
                "Retrieved "
                f"{len(requirement_knowledge)} requirement baseline "
                "document(s)"
            ),
            (
                "Retrieved "
                f"{len(technical_knowledge)} technical/API baseline "
                "document(s)"
            ),
            (
                "Retrieved "
                f"{len(qe_knowledge)} QE baseline document(s)"
            ),
            (
                "Historical evidence was excluded from the "
                "primary test design context"
            ),
            (
                "Approved baseline artifacts will not be modified"
            ),
            (
                "Traceability analysis completed with "
                f"{len(traceability['matched'])} matched mapping(s)"
            ),
            (
                "Traceability analysis identified "
                f"{len(traceability['mismatches'])} mismatch(es)"
            ),
            (
                "Traceability analysis identified "
                f"{len(traceability['gaps'])} gap(s)"
            ),
        ]

        evidence = []

        for collection in (
            requirement_knowledge,
            technical_knowledge,
            qe_knowledge,
        ):
            evidence.extend(
                item["knowledge_id"]
                for item in collection
            )

        evidence.append(
            str(traceability_artifact)
        )

        return TaskResult(
            task_id=task.task_id,
            source_agent=self.name,
            objective=task.objective,
            status="COMPLETED",
            activities=[
                "Retrieved requirement baseline",
                "Retrieved technical/API baseline",
                "Retrieved QE baseline",
                "Scoped retrieved knowledge for test design",
                "Loaded approved RTM baseline",
                "Loaded approved testcase baseline",
                "Performed requirement-to-testcase traceability analysis",
                "Persisted traceability analysis artifact",
            ],
            
            findings=findings,
            evidence=evidence,
            confidence=(
                "HIGH"
                if (
                    requirement_knowledge
                    and technical_knowledge
                    and qe_knowledge
                )
                else "MEDIUM"
            ),
            human_approval_required=bool(
                traceability["mismatches"]
            ),
            next_action=(
                "Review traceability mismatches and gaps, "
                "then proceed to risk-based test prioritization"
            ),
        )