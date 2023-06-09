from __future__ import annotations

from homeassistant.const import EVENT_HOMEASSISTANT_CLOSE
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.tasks.filters import EVENT_TYPE_FILTER_STRATEGY


async def async_setup_task(react: ReactBase) -> ShutdownTask:
    return ShutdownTask(react=react)


class ShutdownTask(ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        self.track_event_filters = [EVENT_TYPE_FILTER_STRATEGY.get_filter(EVENT_HOMEASSISTANT_CLOSE)]


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.RUNTIME


    async def async_execute(self, ha_event: HaEvent) -> None:
        self.task_logger.debug("Shutting down react")

        async def async_shutdown():
            await self.react.async_shutdown()
            self.task_logger.debug("Shutdown complete")

        self.react.hass.async_add_job(async_shutdown)
