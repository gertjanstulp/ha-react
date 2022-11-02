from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.const import EVENT_REACT_ACTION
from custom_components.react.plugin.notify_plugin import NotifyFeedbackEvent, NotifyPlugin
from custom_components.react.tasks.defaults.default_task import DefaultTask
from custom_components.react.utils.logger import format_data


async def async_setup_task(react: ReactBase) -> Task:
    notify_plugin = react.plugin_factory.get_notify_plugin()
    if not notify_plugin:
        react.log.warn("No notify plugin configured, notify feedback default handler will be disabled")
        return None
        
    return Task(react=react, notify_plugin=notify_plugin)


class Task(DefaultTask):

    def __init__(self, react: ReactBase, notify_plugin: NotifyPlugin) -> None:
        super().__init__(react, notify_plugin.get_notify_feedback_event_type())

        self.notify_plugin = notify_plugin
        self.events_with_filters = [(notify_plugin.feedback_event, self.async_filter)]


    async def async_execute_default(self, action_event: NotifyFeedbackEvent) -> None:
        await self.send_action_event(action_event.create_action_event_data(self.react))
        await self.notify_plugin.async_acknowledge_feedback(action_event.create_feedback_data(self.react), action_event.context)


    async def send_action_event(self, action_event_data: dict):
        self.react.log.debug(f"NotifyFeedbackTask: sending action event: {format_data(**action_event_data)}")
        self.react.hass.bus.async_fire(EVENT_REACT_ACTION, action_event_data)
