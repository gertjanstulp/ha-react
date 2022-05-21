from __future__ import annotations

from homeassistant.helpers.dispatcher import async_dispatcher_send

from .base import ReactTask
from ..base import ReactBase
from ..enums import ReactStage

from ..const import (
    SIGNAL_ITEM_CREATED,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """ "React task base."""

    stages = [ReactStage.STARTUP]

    async def async_execute(self) -> None:
        """Execute the task."""
        for reaction in self.react.reactions.list_all:
            async_dispatcher_send(self.react.hass, SIGNAL_ITEM_CREATED, reaction)
