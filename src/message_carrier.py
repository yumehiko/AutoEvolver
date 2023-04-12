from .ui_base import UIBase
from .chat_message import ChatMessage
from .talker import Talker
from .role import Role
import json
from datetime import datetime
from typing import List, Dict



class MessageCarrier:
    """
    ChatMessageをUIに伝達し、ログに記録するクラス。
    """
    def __init__(self, ui: UIBase):
        self.ui = ui
        self.logData: List[Dict[str, str]] = []
        self.system = Talker(role=Role.system, persona_name="system", display_name="System")
        self.user = Talker(role=Role.user, persona_name="user", display_name="User")


    def print_message(self, message: ChatMessage) -> None:
        """
        チャットメッセージを表示する。
        """
        self.ui.print_message(message)
        if message.should_log:
            self.write_to_log(message)

    
    def print_message_as_system(self, text: str, should_log: bool) -> None:
        """
        テキストをシステムメッセージとして表示する。
        """
        message = ChatMessage(text, self.system.sender_info, should_log)
        self.print_message(message)


    def print_message_as_user(self, text: str, should_log: bool) -> None:
        """
        テキストをユーザーメッセージとして表示する。
        """
        message = ChatMessage(text, self.user.sender_info, should_log)
        self.print_message(message)


    def write_to_log(self, message: ChatMessage) -> None:
        """
        ChatMessageをログに記録する。
        """
        # 発言日時を取得
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        # 発言内容を整形
        formatted_prompt = {"sender": message.sender_info.display_name,
                            "content": message.text,
                            "datetime": now}
        # logDataに追加
        self.logData.append(formatted_prompt)


    def save_json(self) -> None:
        """
        これまでに記録したログデータをjson形式で保存する
        """

        # ログが空なら、何もしない
        if not self.logData:
            return

        # ファイル名を取得
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "log/" + now + ".json"

        # ログデータをjson形式で保存
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.logData, f, indent=4, ensure_ascii=False)
        
        # ログデータを初期化
        self.logData.clear()