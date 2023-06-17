from homeassistant.core import Context

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from custom_components.react.plugin.const import (
    PROVIDER_TYPE_NOTIFY
)
from custom_components.react.plugin.notify.config import NotifyConfig
from custom_components.react.plugin.notify.const import NOTIFY_RESOLVER_KEY, FeedbackItem
from custom_components.react.plugin.notify.resolver import NotifyPluginResolver
from custom_components.react.plugin.notify.provider import NotifyProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session


class NotifyApi(PluginApiBase[NotifyConfig]):

    def load(self):
        self.resolver: NotifyPluginResolver = self.plugin.hass_api.hass_get_data(NOTIFY_RESOLVER_KEY)

    
    async def async_send_message(self, 
        session: Session,
        context: Context, 
        entity_id: str, 
        message: str, 
        feedback_items: list[FeedbackItem],
        notify_provider: str,
    ):
        session.debug(self.logger, "Sending notify message '{message}' to {entity_id}")
        try:
            if not self.plugin.hass_api.hass_service_available(NOTIFY_DOMAIN, entity_id):
                session.warning(self.plugin.logger, f"{NOTIFY_DOMAIN}.{entity_id} not found")
                return

            provider = self.get_notify_provider(session, entity_id, notify_provider)
            if provider:
                await provider.async_notify(session, context, entity_id, message, feedback_items)
        except:
            session.exception("Sending message failed")


    async def async_confirm_feedback(self, 
        session: Session, 
        context: Context,
        conversation_id: str,
        message_id: str,
        text: str, 
        feedback: str,
        acknowledgement: str,
        notify_provider: str, 
    ):
        session.debug(self.logger, f"Confirming notify feedback {feedback}")
        try:
            provider = self.get_notify_provider(session, None, notify_provider)
            if provider:
                await provider.async_confirm_feedback(session, context, conversation_id, message_id, text, feedback, acknowledgement)
        except:
            session.exception("Confirming notify feedback failed")
    
        
    def get_notify_provider(self, session: Session, entity_id: str, notify_provider: str) -> NotifyProvider:
        provider = None
        
        self.resolver.load(self.plugin.hass_api)
        
        notify_provider_entity: str = None
        notify_provider_config: str = None

        if entity_id:
            notify_provider_entity = self.resolver.reverse_lookup_entity(entity_id, None)
            if notify_provider_entity:
                provider = self.plugin.get_provider(PROVIDER_TYPE_NOTIFY, notify_provider_entity)

        if not provider:
            notify_provider_config = notify_provider or self.plugin.config.notify_provider
            if notify_provider_config:
                provider = self.plugin.get_provider(PROVIDER_TYPE_NOTIFY, notify_provider_config)
    
        if not provider:
            if entity_id or notify_provider_config:
                target = entity_id
                if notify_provider_config:
                    if target:
                        target = f"{target}/{notify_provider_config}"
                    else:
                        target = notify_provider_config
                session.error(self.plugin.logger, f"Notify provider for '{target}' not found")
            else:
                session.error(self.plugin.logger, f"Notify provider not found")
            return None
        return provider
    