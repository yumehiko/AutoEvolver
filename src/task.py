from enum import Enum

class TaskTag(Enum):
    """
    タスクタグを表す列挙型
    """
    unsolvable = 0
    ask_user = 1
    use_python = 2
    use_bot = 3
    subdivide = 4

class Task:
    """
    AutoEvolverにおける、Botが解決するタスクを表すクラス
    """
    def __init__(self, content: str, tag: TaskTag) -> None:
        self.content = content
        self.tag = tag
        self.completed = False
        self.result: str = ""

    def complete(self, result: str) -> None:
        """
        タスクを完了する
        """
        self.completed = True
        self.result = result

    @property
    def subdividable(self) -> bool:
        """
        タスクが細分化可能かを返す
        """
        return self.tag == TaskTag.subdivide