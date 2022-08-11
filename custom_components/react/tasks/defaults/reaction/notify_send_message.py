from __future__ import annotations

from homeassistant.const import Platform

from ..default_task import DefaultTask
from ....base import ReactBase
from ....plugin.notify_plugin import NotifyPlugin, NotifySendMessageReactionEventDataReader

from ....const import (
     EVENT_REACT_REACTION
)

async def async_setup_task(react: ReactBase) -> Task:
    
    notify_plugin = react.plugin_factory.get_notify_plugin()
    if not notify_plugin:
        react.log.warn("No notify plugin configured, notify sendmessage default handler will be disabled")
        return None

    """Set up this task."""
    return Task(react=react, notify_plugin=notify_plugin)


class Task(DefaultTask):

    def __init__(self, react: ReactBase, notify_plugin: NotifyPlugin) -> None:

        super().__init__(react, react.plugin_factory.get_notify_plugin().get_notify_send_message_reader_type())
        
        self.notify_plugin = notify_plugin
        self.events_with_filters = [(EVENT_REACT_REACTION, self.async_filter)]


    async def async_execute_default(self, event_reader: NotifySendMessageReactionEventDataReader):
        notify_data = event_reader.create_plugin_data()
        await self.notify_plugin.async_send_notification(
            event_reader.entity, 
            notify_data, 
            event_reader.hass_context
        )
        # await self.react.hass.services.async_call(
        #     Platform.NOTIFY, 
        #     event_reader.entity,
        #     notify_data, 
        #     context=event_reader.hass_context)
