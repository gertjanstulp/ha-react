from __future__ import annotations

from homeassistant.const import ATTR_COMMAND

from ..default_task import DefaultTask
from ....base import ReactBase
from ....plugin.notify_plugin import NotifyPlugin, NotifyFeedbackEventDataReader

from ....const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_TYPE,
    EVENT_REACT_ACTION,
    REACT_ACTION_FEEDBACK,
    REACT_TYPE_NOTIFY
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    
    notify_plugin = react.plugin_factory.get_notify_plugin()
    if not notify_plugin:
        react.log.warn("No notify plugin configured, notify feedback default handler will be disabled")
        return None
        
    return Task(react=react, notify_plugin=notify_plugin)


class Task(DefaultTask):

    def __init__(self, react: ReactBase, notify_plugin: NotifyPlugin) -> None:
        super().__init__(react, notify_plugin.get_notify_feedback_reader_type())

        self.notify_plugin = notify_plugin
        self.events_with_filters = [(notify_plugin.feedback_event, self.async_filter)]


    async def async_execute_default(self, event_reader: NotifyFeedbackEventDataReader) -> None:
        await self.send_action_event(event_reader.create_action_event_data())
        await self.notify_plugin.async_acknowledge_feedback(event_reader.create_feedback_data(), event_reader.hass_context)


    async def send_action_event(self, action_event_data: dict):
        self.react.hass.bus.async_fire(EVENT_REACT_ACTION, action_event_data)
