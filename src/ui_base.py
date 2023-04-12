from .chat_message import ChatMessage
from abc import ABC, abstractmethod

class UIBase(ABC):
    @abstractmethod
    async def request_user_input(self) -> str:
        """
        ユーザーからの入力を待機し、入力された文字列を返す。
        """
        pass

    @abstractmethod
    def print_message(self, message: ChatMessage) -> None:
        """
        チャットメッセージを表示する。
        """
        pass

    @abstractmethod
    def process_event(self) -> None:
        """
        待機中にUIを固まらせないためにコールする
        """
        pass