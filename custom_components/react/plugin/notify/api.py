from homeassistant.core import Context
from custom_components.react.plugin.notify.service import NotifyService

from custom_components.react.plugin.plugin_factory import SERVICE_TYPE_DEFAULT, PluginApi
from custom_components.react.plugin.notify.const import CONFIG_DEFAULT_SERVICE_TYPE, PLUGIN_NAME, FeedbackItem
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()

class NotifyApiConfig(DynamicData):
    """ api config """

class NotifyApi():
    def __init__(self, plugin_api: PluginApi, config: NotifyApiConfig) -> None:
        self.plugin_api = plugin_api
        self.default_service_type = config.get(CONFIG_DEFAULT_SERVICE_TYPE, SERVICE_TYPE_DEFAULT)


    def _debug(self, message: str):
        _LOGGER.debug(f"Notify plugin: Api - {message}")


    def _exception(self, message: str):
        _LOGGER.exception(f"Notify plugin: Api - {message}")


    async def async_send_message(self, 
        context: Context, 
        service_type: str, 
        entity_id: str, 
        message: str, 
        feedback_items: list[FeedbackItem]
    ):
        self._debug("Sending notify message")
        try:
            if not service_type:
                service_type = self.default_service_type
            service: NotifyService = self.plugin_api.get_service(PLUGIN_NAME, service_type)
            if service:
                await service.async_notify(context, entity_id, message, feedback_items)
            else:
                _LOGGER.warn(f"Notify plugin: Api - Service for '{service_type}' not found")
        except:
            _LOGGER.exception("Notify plugin: Api - Sending message failed")


    async def async_confirm_feedback(self, 
        context: Context,
        service_type: str, 
        conversation_id: str,
        message_id: str,
        text: str, 
        acknowledgement: str
    ):
        self._debug("Confirming notify feedback")
        try:
            if not service_type:
                service_type = self.default_service_type
            service: NotifyService = self.plugin_api.get_service(PLUGIN_NAME, service_type)
            if service:
                await service.async_confirm_feedback(context, conversation_id, message_id, text, acknowledgement)
            else:
                _LOGGER.warn(f"Notify plugin: Api - Service for '{service_type}' not found")
        except:
            _LOGGER.exception("Notify plugin: Api - Confirming notify feedback failed")
