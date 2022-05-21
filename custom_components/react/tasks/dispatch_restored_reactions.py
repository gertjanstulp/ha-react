from __future__ import annotations

from ..base import ReactBase
from ..enums import ReactDisabledReason, ReactStage
from .base import ReactTask


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    stages = [ReactStage.RUNNING]

    async def async_execute(self) -> None:
        """Execute the task."""
        for reaction in self.react.reactions.list_all:
            self.react.dispatcher.dispatch(reaction.data.id)
