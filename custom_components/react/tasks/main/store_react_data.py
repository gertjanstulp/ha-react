from __future__ import annotations

from homeassistant.const import EVENT_HOMEASSISTANT_FINAL_WRITE
from homeassistant.core import Event

from ..base import ReactTask

from ...base import ReactBase


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        
        self.events = [EVENT_HOMEASSISTANT_FINAL_WRITE]
        self.can_run_disabled = True


    async def async_execute(self, event: Event) -> None:
        """Execute the task."""
        await self.react.data.async_write(force=True)
