from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.utils.component import async_setup_component



async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.STARTUP


    async def async_execute(self) -> None:
        """Execute the task."""
        await async_setup_component(self.react)
