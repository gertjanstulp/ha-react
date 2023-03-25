from homeassistant.components.notify.const import (
    ATTR_MESSAGE,
)
from homeassistant.components.persistent_notification import (
    DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN,
    ATTR_NOTIFICATION_ID
)
from homeassistant.const import Platform
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.notify.service import NotifyService
from custom_components.react.plugin.persistent_notification.const import SERVICE_CREATE


class PersistentNotificationService(NotifyService):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        await self.react.hass.services.async_call(
            PERSISTENT_NOTIFICATION_DOMAIN, 
            SERVICE_CREATE,
            {
                ATTR_MESSAGE: message,
                ATTR_NOTIFICATION_ID: entity_id
            }, 
            context
        )
