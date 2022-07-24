""""Store React data."""
from __future__ import annotations

from homeassistant.const import EVENT_HOMEASSISTANT_FINAL_WRITE
from homeassistant.core import Event

from ..base import ReactBase
from .base import ReactTask


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """ "React task base."""

    events = [EVENT_HOMEASSISTANT_FINAL_WRITE]
    _can_run_disabled = True

    async def async_execute(self, event: Event) -> None:
        """Execute the task."""
        await self.react.data.async_write(force=True)
