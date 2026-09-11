from dataclasses import dataclass, field
from typing import List


@dataclass
class RuntimeDependency:
    """
    Describes a runtime value required by a testcase.

    The dependency identifies:
    - what value is required
    - which testcase produces it
    - where the value comes from
    - whether it is mandatory before execution
    """

    consumer_testcase_id: str
    variable_name: str
    producer_testcase_id: str
    source: str
    required: bool = True
    description: str = ""

    def validate(self):
        if not self.consumer_testcase_id:
            raise ValueError("consumer_testcase_id is required")

        if not self.variable_name:
            raise ValueError("variable_name is required")

        if not self.producer_testcase_id:
            raise ValueError("producer_testcase_id is required")

        if not self.source:
            raise ValueError("source is required")

        return True