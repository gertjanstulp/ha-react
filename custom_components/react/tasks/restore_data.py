""""Starting setup task: Restore"."""
from __future__ import annotations

from ..base import ReactBase
from ..enums import ReactDisabledReason, ReactStage
from .base import ReactTask


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Restore React data."""

    stages = [ReactStage.SETUP]

    async def async_execute(self) -> None:
        """Execute the task."""
        if not await self.react.data.async_restore():
            self.react.disable_react(ReactDisabledReason.RESTORE)
