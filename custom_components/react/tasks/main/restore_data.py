from __future__ import annotations

from ..base import ReactTask

from ...base import ReactBase
from ...enums import ReactDisabledReason, ReactStage


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Restore React data."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        
        self.stages = [ReactStage.SETUP]


    async def async_execute(self) -> None:
        """Execute the task."""
        if not await self.react.data.async_restore():
            self.react.disable_react(ReactDisabledReason.RESTORE)
