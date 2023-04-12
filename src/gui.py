from .ui_base import UIBase
from .chat_message import ChatMessage
from .talker import Talker
from .role import Role
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextEdit, QLineEdit, QWidget, QSizePolicy
from PyQt6.QtGui import QTextOption, QTextBlockFormat, QTextCursor, QKeyEvent
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QEventLoop, QEvent
from typing import Optional, Callable
import sys
import asyncio

class InputArea(QTextEdit):
    def __init__(self, user_input_queue: asyncio.Queue[str], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.user_input_queue = user_input_queue


    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Return:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.textCursor().insertText("\n")
            else:
                self.send_message()
        else:
            super().keyPressEvent(event)


    def send_message(self) -> None:
        text = self.toPlainText()
        if text:
            self.clear()
            asyncio.create_task(self.user_input_queue.put(text))


    def adjust_height(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        height = self.document().size().height()
        self.setFixedHeight(int(min(height, 200)))



class GUI(UIBase):
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.main_window = QMainWindow()
        self.user_input_queue: asyncio.Queue[str] = asyncio.Queue()
        self.init_ui()


    def get_app_instance(self) -> QApplication:
        return self.app


    def init_ui(self) -> None:
        # メインウィンドウの設定
        self.main_window.setWindowTitle("PlayWithGPT GUI Mode")
        self.main_window.resize(800, 600)

        # レイアウトとウィジェットの設定
        central_widget = QWidget(self.main_window)
        layout = QVBoxLayout(central_widget)
        self.main_window.setCentralWidget(central_widget)

        # メッセージ欄の設定
        self.message_area = QTextEdit(central_widget)
        self.message_area.setReadOnly(True)
        layout.addWidget(self.message_area)

        # 入力欄の設定
        self.input_area = InputArea(self.user_input_queue, self.main_window)
        self.input_area.setPlaceholderText("メッセージを入力：Shift+Enterで改行、Enterで送信")
        self.input_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.input_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.input_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.input_area.setFixedHeight(self.input_area.fontMetrics().height() + 10)
        layout.addWidget(self.input_area)
        # テキストが入力されたら、必要に応じて高さを調整する。
        self.input_area.textChanged.connect(self.input_area.adjust_height)
        self.input_area.setFocus()


    async def request_user_input(self) -> str:
        return await self.user_input_queue.get()


    def print_message(self, message: ChatMessage) -> None:
        # カーソルを末尾へ移動する。
        cursor = self.message_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.message_area.setTextCursor(cursor)

        if message.sender_info.role == Role.assistant:
            color = QColor("yellow")
        elif message.sender_info.role == Role.system:
            color = QColor("cyan")
        else :
            color = QApplication.palette().text().color()

        # Set name color
        char_format = QTextCharFormat()
        char_format.setForeground(color)
        self.message_area.setCurrentCharFormat(char_format)

        # Insert name
        if message.sender_info.role == Role.user:
            name = "You: "
        elif message.sender_info.role == Role.assistant:
            name = message.sender_info.display_name + ": "
        else:
            name = ""
        self.message_area.insertPlainText(name)

        # Insert message text
        self.message_area.insertPlainText(message.text + "\n\n")

    def enable_user_input(self) -> None:
        self.input_area.setEnabled(True)
        self.input_area.setFocus()

    def disable_user_input(self) -> None:
        self.input_area.setEnabled(False)

    def show_waiting_animation(self) -> None:
        self.main_window.setWindowTitle("PlayWithGPT GUI Mode (Waiting...)")
        self.main_window.repaint()

    def hide_waiting_animation(self) -> None:
        self.main_window.setWindowTitle("PlayWithGPT GUI Mode")
        self.main_window.repaint()

    def process_event(self) -> None:
        self.app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, -1)