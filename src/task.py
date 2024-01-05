from __future__ import annotations
from enum import Enum

class TaskTag(Enum):
    """
    Enumerated types representing task types
    """
    unsolvable = 0
    ask_user = 1
    use_python = 2
    use_bot = 3
    subdivide = 4

class Task:
    """
    Class representing the task to be solved by the bot in AutoEvolver
    """
    def __init__(self, content: str, tag: TaskTag) -> None:
        self.content = content
        self.tag = tag
        self.completed = False
        self.result: str = ""
        self.subtasks: list[Task] = []

    def complete(self, result: str) -> None:
        self.completed = True
        self.result = result

    def set_subtasks(self, subtasks: list[Task]) -> None:
        self.subtasks = subtasks

    @property
    def subdividable(self) -> bool:
        return self.tag == TaskTag.subdivide