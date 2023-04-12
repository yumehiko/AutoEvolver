from enum import Enum

class Role(Enum):
    """
    ChatGPTのロールを表す列挙型
    """
    none = 0,
    user = 1,
    assistant = 2,
    system = 3