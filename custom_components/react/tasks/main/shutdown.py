from __future__ import annotations

from homeassistant.const import EVENT_HOMEASSISTANT_CLOSE
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.tasks.base import ReactTask


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        
        self.events = [EVENT_HOMEASSISTANT_CLOSE]
        self.can_run_disabled = True


    async def async_execute(self, event: Event) -> None:
        """Execute the task."""
        await self.react.async_shutdown()