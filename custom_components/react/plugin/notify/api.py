from homeassistant.core import Context

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from custom_components.react.plugin.const import (
    PROVIDER_TYPE_NOTIFY
)
from custom_components.react.plugin.notify.config import NotifyConfig
from custom_components.react.plugin.notify.const import NOTIFY_RESOLVER_KEY, FeedbackItem
from custom_components.react.plugin.notify.resolver import NotifyPluginResolver
from custom_components.react.plugin.notify.provider import NotifyProvider
from custom_components.react.plugin.plugin_factory import ApiBase, HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger

_LOGGER = get_react_logger()


class NotifyApi(ApiBase):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi, config: NotifyConfig) -> None:
        super().__init__(plugin_api, hass_api)
        self.config = config
        self.resolver: NotifyPluginResolver = self.hass_api.hass_set_data(NOTIFY_RESOLVER_KEY, NotifyPluginResolver(plugin_api, hass_api))


    def _debug(self, message: str):
        _LOGGER.debug(f"Notify plugin: Api - {message}")


    def _exception(self, message: str):
        _LOGGER.exception(f"Notify plugin: Api - {message}")


    async def async_send_message(self, 
        context: Context, 
        entity_id: str, 
        message: str, 
        feedback_items: list[FeedbackItem],
        notify_provider_name: str,
    ):
        self._debug("Sending notify message")
        try:
            if not self.hass_api.hass_service_available(NOTIFY_DOMAIN, entity_id):
                _LOGGER.warn(f"Notify plugin: Api - {NOTIFY_DOMAIN}.{entity_id} not found")
                return

            provider = self.get_notify_provider(entity_id, notify_provider_name)
            if provider:
                await provider.async_notify(context, entity_id, message, feedback_items)
        except:
            self._exception("Sending message failed")


    async def async_confirm_feedback(self, 
        context: Context,
        conversation_id: str,
        message_id: str,
        text: str, 
        acknowledgement: str,
        notify_provider_name: str, 
    ):
        self._debug("Confirming notify feedback")
        try:
            provider = self.get_notify_provider(None, notify_provider_name)
            if provider:
                await provider.async_confirm_feedback(context, conversation_id, message_id, text, acknowledgement)
        except:
            self._exception("Confirming notify feedback failed")
    
        
    def get_notify_provider(self, entity_id: str, notify_provider_name: str) -> NotifyProvider:
        notify_provider = None
        
        self.resolver.load()
        
        if entity_id:
            notify_provider_name = self.resolver.reverse_lookup_entity(entity_id, None)
            if notify_provider_name:
                notify_provider = self.plugin_api.get_provider(PROVIDER_TYPE_NOTIFY, notify_provider_name)

        if not notify_provider:
            notify_provider_name = notify_provider_name or self.config.notify_provider_name
            if notify_provider_name:
                notify_provider = self.plugin_api.get_provider(PROVIDER_TYPE_NOTIFY, notify_provider_name)
    
        if not notify_provider:
            if entity_id or notify_provider:
                target = entity_id
                if notify_provider_name:
                    target = f"{target}/{notify_provider_name}"
                _LOGGER.error(f"Notify plugin: Api - Notify provider for '{target}' not found")
            else:
                _LOGGER.error(f"Notify plugin: Api - Notify provider not found")
            return None
        return notify_provider
    