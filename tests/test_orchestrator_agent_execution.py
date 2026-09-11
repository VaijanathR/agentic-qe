from agents.base_agent import BaseAgent
from agents.orchestrator import Orchestrator
from memory.task_result import TaskResult
from memory.task_state import TaskStatus


class TestAgent(BaseAgent):

    @property
    def name(self):
        return "TestAgent"

    def execute(self, task):
        return TaskResult(
            task_id=task.task_id,
            source_agent=self.name,
            objective=task.objective,
            status="COMPLETED",
            evidence=["Agent executed successfully"],
            next_action="HANDOFF_TO_NEXT_AGENT",
        )


def test_orchestrator_executes_agent():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-401",
        objective="Execute test agent",
        agent="TestAgent",
    )

    agent = TestAgent()

    task = orchestrator.execute_task(
        "TASK-401",
        agent,
    )

    assert task.status == TaskStatus.COMPLETED
    assert "Agent executed successfully" in task.evidence
    assert task.next_action == "HANDOFF_TO_NEXT_AGENT"


def test_orchestrator_rejects_non_agent():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-402",
        objective="Execute test agent",
        agent="TestAgent",
    )

    try:
        orchestrator.execute_task(
            "TASK-402",
            "not an agent",
        )
        assert False
    except TypeError:
        assert True


def test_orchestrator_does_not_execute_blocked_task():
    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-403",
        objective="Execute dependent task",
        agent="TestAgent",
        dependencies=["TASK-404"],
    )

    orchestrator.create_task(
        task_id="TASK-404",
        objective="Dependency",
        agent="TestAgent",
    )

    agent = TestAgent()

    task = orchestrator.execute_task(
        "TASK-403",
        agent,
    )

    assert task.status == TaskStatus.BLOCKED

def test_orchestrator_executes_automation_agent():
    from agents.automation_agent import AutomationAgent

    orchestrator = Orchestrator()

    orchestrator.create_task(
        task_id="TASK-AUTO-ORCH-001",
        objective="Convert approved testcases into automation",
        agent="AutomationAgent",
    )

    agent = AutomationAgent()

    task = orchestrator.execute_task(
        "TASK-AUTO-ORCH-001",
        agent,
    )

    assert task.status == TaskStatus.COMPLETED
    assert len(task.evidence) > 0
    assert any(
        "automation.json" in evidence
        for evidence in task.evidence
    )