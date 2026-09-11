from pathlib import Path

from agents.base_agent import BaseAgent
from agents.requirement_extractor import (
    RequirementExtractor,
)
from memory.task_result import TaskResult
from rag.retriever import KnowledgeRetriever
from rag.knowledge_store import KnowledgeStore
from rag.metadata import KnowledgeMetadata
from requirements.requirement_validator import RequirementValidator

class RequirementsAgent(BaseAgent):

    def __init__(self, project_root="."):
        metadata_file = (
            Path(project_root)
            / "rag"
            / "knowledge_metadata.json"
        )

        metadata_registry = KnowledgeMetadata(
            metadata_file
        )

        knowledge_store = KnowledgeStore(
            project_root,
            metadata_registry,
        )

        self.retriever = KnowledgeRetriever(
            knowledge_store
        )

        self.extractor = RequirementExtractor()
        self.validator = RequirementValidator()

    @property
    def name(self):
        return "RequirementsAgent"

    def execute(self, task):
        retrieval = self.retriever.retrieve(
            query=task.objective,
            requesting_agent=self.name,
            task_id=task.task_id,
            top_k=3,
        )

        # Preserve every retrieved document as evidence.
        evidence = [
            item["knowledge_id"]
            for item in retrieval
        ]

        # Identify the authoritative requirement baseline.
        authoritative_documents = [
            item
            for item in retrieval
            if item.get("authority")
            == "AUTHORITATIVE_REQUIREMENT_BASELINE"
        ]

        primary_evidence = None

        if authoritative_documents:
            authoritative_documents.sort(
                key=lambda item: item.get(
                    "retrieval_priority",
                    99,
                )
            )

            primary_evidence = (
                authoritative_documents[0]
            )

        findings = [
            f"Retrieved {len(retrieval)} relevant approved documents"
        ]

        requirements = []

        if primary_evidence:
            findings.append(
                "Authoritative requirement baseline identified: "
                f"{primary_evidence['knowledge_id']} "
                f"({primary_evidence['document_name']})"
            )

            supporting_evidence = [
                item["knowledge_id"]
                for item in retrieval
                if item["knowledge_id"]
                != primary_evidence["knowledge_id"]
            ]

            if supporting_evidence:
                findings.append(
                    "Supporting evidence identified: "
                    + ", ".join(supporting_evidence)
                )

        requirements = self.extractor.extract(
            content=primary_evidence["content"],
            source_knowledge_id=primary_evidence["knowledge_id"],
            source_document=primary_evidence["document_name"],
        )

        validation_results = self.validator.validate_all(
            [requirement.to_dict() for requirement in requirements]
        )

        valid_requirements = [
            requirement
            for requirement, validation in zip(requirements, validation_results)
            if validation["valid"]
        ]

        invalid_requirements = [
            validation
            for validation in validation_results
            if not validation["valid"]
        ]

        findings.append(
            f"Extracted {len(requirements)} requirement candidates from the authoritative baseline"
        )

        findings.append(
            f"Validated {len(valid_requirements)} requirements"
        )

        if invalid_requirements:
            findings.append(
                f"Rejected {len(invalid_requirements)} invalid requirement candidates"
            )

        else:
            findings.append(
                "No authoritative requirement baseline "
                "was found in the retrieved evidence"
            )

        return TaskResult(
            task_id=task.task_id,
            source_agent=self.name,
            objective=task.objective,
            status="COMPLETED",
            activities=[
                "Retrieved approved knowledge for the requirement task",
                "Classified retrieved evidence by authority",
                "Extracted structured requirements from the "
                "authoritative requirement baseline",
            ],
            findings=findings,
            evidence=evidence,
            requirements=[requirement.to_dict() for requirement in valid_requirements],
            confidence=1.0,
        )