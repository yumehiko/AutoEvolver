from .chat_message import ChatMessage
from .role import Role
from .ui_base import UIBase
from aioconsole import ainput
import colorama
import asyncio


class CUI(UIBase):
    """
    CUIのUIクラス。
    """
    def __init__(self) -> None:
        colorama.init()


    async def request_user_input(self) -> str:
        """
        ユーザーからの入力を待機し、入力された文字列を返す。
        """
        input_text: str = await ainput("You: ")
        return input_text


    def print_message(self, message: ChatMessage) -> None:
        """
        メッセージを表示する。
        """
        
        # CUIでは、ユーザーの出力は表示済みなので、その場合空行だけ入れて無視する。
        if message.sender_info.role == Role.user:
            print()
            return

        color = colorama.Fore.WHITE
        reset = colorama.Style.RESET_ALL
        talker_mark = ""

        if message.sender_info.role == Role.assistant:
            color = colorama.Fore.YELLOW
        elif message.sender_info.role == Role.system:
            color = colorama.Fore.CYAN

        if message.sender_info.role == Role.assistant:
            talker_mark = "Bot: "

        print(color + talker_mark + message.text + reset)

        # 空行を入れる
        print()
