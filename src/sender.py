from .role import Role

class Sender:
    """
    ChatMessageの送信者情報。
    """
    def __init__(self, persona_name: str, display_name: str, role: Role):
        self.persona_name = persona_name
        self.display_name = display_name
        self.role = role