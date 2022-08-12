from __future__ import annotations

from ..base import ReactTask

from ...base import ReactBase
from ...enums import ReactStage
from ...utils.component import async_setup_component


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Setup the React sensor platform."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        
        self.stages = [ReactStage.SETUP]


    async def async_execute(self) -> None:
        """Execute the task."""
        await async_setup_component(self.react)
