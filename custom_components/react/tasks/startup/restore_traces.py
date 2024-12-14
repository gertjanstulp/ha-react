from __future__ import annotations

from homeassistant.components.trace.util import async_restore_traces
from homeassistant.components.trace.const import DATA_TRACE_STORE

from custom_components.react.base import ReactBase
from custom_components.react.tasks.base import ReactTask, ReactTaskType


async def async_setup_task(react: ReactBase) -> Task:
    return Task(react=react)


class Task(ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.STARTUP


    async def async_execute(self) -> None:
        self.task_logger.debug("Restoring trace data")
        if DATA_TRACE_STORE in self.react.hass.data:
            await async_restore_traces(self.react.hass)
