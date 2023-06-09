from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING
from custom_components.react.const import ATTR_SESSION_ID


if TYPE_CHECKING:
    from custom_components.react.base import ReactBase
    from custom_components.react.utils.events import ReactEvent
    

class SessionManager:
    def __init__(self, react: ReactBase) -> None:
        self._react = react

        self._last_session_id: int = 0
        self._sessions: dict[str, Session] = {}


    def load_session(self, react_event: ReactEvent):
        result: Session = react_event.session
        if not result:
            if session_id := react_event.payload.get(ATTR_SESSION_ID, None):
                result = self._sessions.get(session_id, None)
        if not result:
            self._last_session_id += 1
            result = self._register_new_session(str(self._last_session_id))
        react_event.set_session(result)


    def _register_new_session(self, session_id: str):
        return self._sessions.setdefault(session_id, Session(session_id, self))


class Session:
    def __init__(self, id: str, session_manager: SessionManager) -> None:
        self.id = id
        self.session_manager = session_manager
        self._last_child_session_id: int = 0
        self.child_sessions: dict[str, Session] = {}


    def debug(self, logger: Logger, message: str):
        logger.debug(self.format_message(message))


    def info(self, logger: Logger, message: str):
        logger.info(self.format_message(message))


    def warning(self, logger: Logger, message: str):
        logger.warning(self.format_message(message))


    def error(self, logger: Logger, message: str):
        logger.error(self.format_message(message))


    def format_message(self, message: str):
        return f"{self.id} - {message}"
        

    def create_child_session(self) -> Session:
        self._last_child_session_id += 1
        child_session_id = f"{self.id}.{self._last_child_session_id}"
        child_session = self.session_manager._register_new_session(child_session_id)
        self.child_sessions[child_session_id] = child_session
        return child_session
