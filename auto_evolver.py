from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEventLoop
from src.session import Session
from src.cui import CUI
from src.gui import GUI
import gettext
import asyncio
import qasync
import os

def run_with_gui() -> None:
    """
    Run in GUI mode.
    """
    view = GUI()
    view.main_window.show()
    session = Session(view)
    # Run Qt event loop and asyncio event loop together
    loop = qasync.QEventLoop(view.get_app_instance())
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(session.run())
    finally:
        loop.close()

def run_with_cui() -> None:
    """
    Run in CUI mode.
    """
    view = CUI()
    session = Session(view)
    asyncio.run(session.run())
    

if __name__ == "__main__":
    ui_mode = os.getenv("UI_MODE", "")
    if ui_mode == "GUI":
        run_with_gui()
    else:
        run_with_cui()