""""Starting setup task: Restore"."""
from __future__ import annotations

from homeassistant.components.trace import async_restore_traces

from ..base import ReactBase
from ..enums import ReactStage
from .base import ReactTask


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Restore React data."""

    stages = [ReactStage.SETUP]

    async def async_execute(self) -> None:
        """Execute the task."""
        await async_restore_traces(self.react.hass)