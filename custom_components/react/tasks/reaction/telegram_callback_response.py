from __future__ import annotations

# from homeassistant.components.telegram_bot import EVENT_TELEGRAM_CALLBACK
from homeassistant.const import ATTR_COMMAND
from homeassistant.core import Event, callback

from ..base import ReactTask

from ...base import ReactBase

from ...const import (
    ATTR_ACTION,
    ATTR_ENTITY,
    ATTR_TYPE,
    EVENT_REACT_ACTION,
    EVENT_TELEGRAM_CALLBACK
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        self.events_with_filters = [(EVENT_TELEGRAM_CALLBACK, self.async_filter)]


    async def async_execute(self, event: Event) -> None:
        args = event.data.get("args", [])
        command = None
        acknowledgement = None
        if len(args) > 0:
            command = args[0]
        if len(args) > 1:
            acknowledgement = args[1]

        await self.send_react_event(command)
        # self.task_logger(self.react.log.info, "test")


    async def send_react_event(self, command):
        react_event = {
            ATTR_ENTITY: "telegram",
            ATTR_TYPE: "notify",
            ATTR_ACTION: command
        }
        self.react.hass.bus.async_fire(EVENT_REACT_ACTION, react_event)


    @callback
    def async_filter(self, event: Event) -> bool:
        if ATTR_COMMAND in event.data and event.data[ATTR_COMMAND] == "/telegram_react":
            return True
        return False