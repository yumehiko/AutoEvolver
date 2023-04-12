from src.session import Session
from src.cui import CUI
import asyncio

if __name__ == "__main__":
    view = CUI()
    session = Session(view)
    asyncio.run(session.run())