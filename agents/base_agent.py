from abc import ABC, abstractmethod
from memory.task_state import TaskState
from memory.task_result import TaskResult


class BaseAgent(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def execute(self, task):
        pass