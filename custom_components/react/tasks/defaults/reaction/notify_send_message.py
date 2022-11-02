from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.const import EVENT_REACT_REACTION
from custom_components.react.plugin.notify_plugin import NotifyPlugin, NotifySendMessageReactionEvent, NotifySendMessageReactionEventData, NotifySendMessageReactionEventNotificationData
from custom_components.react.tasks.defaults.default_task import DefaultTask


async def async_setup_task(react: ReactBase) -> Task:
    
    notify_plugin = react.plugin_factory.get_notify_plugin()
    if not notify_plugin:
        react.log.warn("No notify plugin configured, notify sendmessage default handler will be disabled")
        return None

    """Set up this task."""
    return Task(react=react, notify_plugin=notify_plugin)


class Task(DefaultTask):

    def __init__(self, react: ReactBase, notify_plugin: NotifyPlugin) -> None:

        super().__init__(react, react.plugin_factory.get_notify_plugin().get_notify_send_message_event_type())
        
        self.notify_plugin = notify_plugin
        self.events_with_filters = [(EVENT_REACT_REACTION, self.async_filter)]


    async def async_execute_default(self, reaction_event: NotifySendMessageReactionEvent[NotifySendMessageReactionEventData[NotifySendMessageReactionEventNotificationData]]):
        await self.notify_plugin.async_send_notification(
            reaction_event.data.entity, 
            reaction_event.data.data.create_service_data(),
            reaction_event.context
        )
