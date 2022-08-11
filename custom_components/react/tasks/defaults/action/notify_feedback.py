from __future__ import annotations

from homeassistant.const import ATTR_COMMAND

from ..default_task import DefaultTask
from ....base import ReactBase
from ....impl.impl_factory import NotifyProvider
from ....utils.events import NotifyFeedbackEventDataReader

from ....const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_TYPE,
    EVENT_REACT_ACTION,
    REACT_ACTION_FEEDBACK,
    REACT_TYPE_NOTIFY
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    
    notify_provider = await react.impl_factory.async_get_notify_provider()
    if not notify_provider:
        react.log.info("No notify provider configured, notify feedback default handler will be disabled")
        return None
        
    return Task(react=react, notify_provider=notify_provider)


class Task(DefaultTask[NotifyFeedbackEventDataReader]):

    def __init__(self, react: ReactBase, notify_provider: NotifyProvider) -> None:
        super().__init__(react, notify_provider.get_reader_type())

        self.notify_provider = notify_provider
        self.events_with_filters = [(notify_provider.feedback_event, self.async_filter)]


    async def async_execute_default(self, event_reader: NotifyFeedbackEventDataReader) -> None:
        await self.send_react_event(event_reader)
        await self.notify_provider.async_send_feedback(event_reader)


    async def send_react_event(self, event_reader: NotifyFeedbackEventDataReader):
        react_event = {
            ATTR_ENTITY: event_reader.entity,
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK,
            ATTR_DATA: {
                ATTR_COMMAND: event_reader.command
            }
        }
        self.react.hass.bus.async_fire(EVENT_REACT_ACTION, react_event)
