from __future__ import annotations

from ..base import ReactTask

from ...base import ReactBase
from ...const import SIGNAL_DISPATCH


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Restore React data."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        
        self.signals = [SIGNAL_DISPATCH]


    async def async_execute(self, reaction_id: str) -> None:
        """Execute the task."""
        self.react.dispatcher.dispatch(reaction_id)
