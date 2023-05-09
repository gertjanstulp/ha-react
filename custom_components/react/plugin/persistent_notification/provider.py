from homeassistant.components.notify.const import (
    ATTR_MESSAGE,
)
from homeassistant.components.persistent_notification import (
    DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN,
    ATTR_NOTIFICATION_ID
)
from homeassistant.core import Context

from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.notify.provider import NotifyProvider
from custom_components.react.plugin.persistent_notification.const import SERVICE_CREATE
from custom_components.react.plugin.api import HassApi, PluginApi


class PersistentNotificationProvider(NotifyProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        await self.hass_api.async_hass_call_service(
            PERSISTENT_NOTIFICATION_DOMAIN, 
            SERVICE_CREATE,
            {
                ATTR_MESSAGE: message,
                ATTR_NOTIFICATION_ID: entity_id
            }, 
            context
        )
