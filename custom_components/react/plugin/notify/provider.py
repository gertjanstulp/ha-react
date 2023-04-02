from homeassistant.core import Context

from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.plugin.providers import PluginProvider


class NotifyProvider(PluginProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        raise NotImplementedError()
    

    async def async_confirm_feedback(self, context: Context, conversation_id: str, message_id: str, text: str, acknowledgement: str):
        raise NotImplementedError()