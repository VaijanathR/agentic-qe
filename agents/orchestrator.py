from memory.task_state import TaskState, TaskStatus
from memory.evidence_store import EvidenceStore
from memory.decision_manager import DecisionManager
from memory.decision_governance import DecisionGovernance
from memory.task_result import TaskResult
from agents.base_agent import BaseAgent   

class Orchestrator:

    def __init__(self):
        self.tasks = {}
        self.evidence_store = EvidenceStore()
        self.decision_manager = DecisionManager()
        self.decision_governance = DecisionGovernance()

    def create_task(
        self,
        task_id,
        objective,
        agent,
        parent_task_id=None,
        dependencies=None,
    ):
        if task_id in self.tasks:
            raise ValueError(f"Task already exists: {task_id}")

        task = TaskState(
            task_id=task_id,
            objective=objective,
            agent=agent,
            parent_task_id=parent_task_id,
            dependencies=dependencies,
        )

        self.tasks[task_id] = task
        return task

    def get_task(self, task_id):
        if task_id not in self.tasks:
            raise KeyError(f"Task not found: {task_id}")

        return self.tasks[task_id]

    def start_task(self, task_id):
        task = self.get_task(task_id)

        if task.dependencies:
            for dependency_id in task.dependencies:
                dependency = self.get_task(dependency_id)

                if dependency.status != TaskStatus.COMPLETED:
                    task.update_status(TaskStatus.BLOCKED)
                    return task

        task.update_status(TaskStatus.RUNNING)
        return task

    def add_evidence(self, evidence_id, task_id, source, evidence_type,
                     description, content=None):
        task = self.get_task(task_id)

        evidence = self.evidence_store.add_evidence(
            evidence_id=evidence_id,
            task_id=task_id,
            source=source,
            evidence_type=evidence_type,
            description=description,
            content=content,
        )

        task.add_evidence(evidence_id)

        return evidence

    def apply_decision(self, decision):
        task = self.get_task(decision.task_id)

        self.decision_manager.create_decision(decision)

        task.add_decision(decision.decision_id)
        task.next_action = decision.next_action

        governance_result = self.decision_governance.evaluate(decision)

        task.human_approval_required = governance_result[
            "human_approval_required"
        ]

        if governance_result["governance_level"] == "GREEN":
            task.update_status(TaskStatus.RUNNING)

        elif governance_result["governance_level"] == "YELLOW":
            task.update_status(TaskStatus.WAITING_FOR_HUMAN)

        elif governance_result["governance_level"] == "RED":
            task.update_status(TaskStatus.BLOCKED)

        return governance_result

    def complete_task(self, result):
        if not isinstance(result, TaskResult):
            raise TypeError("result must be a TaskResult object")

        task = self.get_task(result.task_id)

        task.outputs.append(result.to_dict())
        task.evidence.extend(result.evidence)
        task.decisions.extend(result.decisions)
        task.human_approval_required = result.human_approval_required
        task.next_action = result.next_action

        if result.human_approval_required:
            task.update_status(TaskStatus.WAITING_FOR_HUMAN)

        elif result.status == TaskStatus.FAILED.value:
            task.update_status(TaskStatus.FAILED)

        elif result.status == TaskStatus.BLOCKED.value:
            task.update_status(TaskStatus.BLOCKED)

        else:
            task.update_status(TaskStatus.COMPLETED)

        return task
    
    def execute_task(self, task_id, agent):
        if not isinstance(agent, BaseAgent):
            raise TypeError("agent must be a BaseAgent object")

        task = self.get_task(task_id)

        if task.status == TaskStatus.NOT_STARTED:
            self.start_task(task_id)

        if task.status != TaskStatus.RUNNING:
            return task

        result = agent.execute(task)

        self.complete_task(result)

        return self.get_task(task_id)