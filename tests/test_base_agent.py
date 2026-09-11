import pytest

from agents.base_agent import BaseAgent
from memory.task_result import TaskResult


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
        )


def test_agent_has_name():
    agent = TestAgent()

    assert agent.name == "TestAgent"


def test_agent_can_execute_task():
    from memory.task_state import TaskState

    agent = TestAgent()

    task = TaskState(
        task_id="TASK-301",
        objective="Test agent execution",
        agent="TestAgent",
    )

    result = agent.execute(task)

    assert isinstance(result, TaskResult)
    assert result.task_id == "TASK-301"
    assert result.source_agent == "TestAgent"
    assert result.status == "COMPLETED"


def test_base_agent_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseAgent()