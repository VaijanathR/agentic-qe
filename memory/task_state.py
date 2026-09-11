# Persists current task/workflow state across the PLAN-EXECUTE-OBSERVE-ANALYZE-RE-PLAN cycle.
from enum import Enum


class TaskStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    FAILED = "FAILED"


class TaskState:
    def __init__(
        self,
        task_id,
        objective,
        agent,
        parent_task_id=None,
        status=TaskStatus.NOT_STARTED,
        inputs=None,
        outputs=None,
        evidence=None,
        decisions=None,
        dependencies=None,
        human_approval_required=False,
        next_action=None,
    ):
        self.task_id = task_id
        self.parent_task_id = parent_task_id
        self.objective = objective
        self.agent = agent
        self.status = status
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.evidence = evidence or []
        self.decisions = decisions or []
        self.dependencies = dependencies or []
        self.human_approval_required = human_approval_required
        self.next_action = next_action

    def update_status(self, status):
        self.status = status

    def add_input(self, item):
        self.inputs.append(item)

    def add_output(self, item):
        self.outputs.append(item)

    def add_evidence(self, item):
        self.evidence.append(item)

    def add_decision(self, item):
        self.decisions.append(item)

    def add_dependency(self, task_id):
        self.dependencies.append(task_id)

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "parent_task_id": self.parent_task_id,
            "objective": self.objective,
            "agent": self.agent,
            "status": self.status.value,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "evidence": self.evidence,
            "decisions": self.decisions,
            "dependencies": self.dependencies,
            "human_approval_required": self.human_approval_required,
            "next_action": self.next_action,
        }