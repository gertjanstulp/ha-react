from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN

from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, 
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID, 
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID, 
    ATTR_EVENT_FEEDBACK_ITEM_TEXT, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE
)
from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.notify.plugin import load as load_plugin
from custom_components.react.plugin.notify.provider import NotifyProvider
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData
from tests._plugins.common import HassApiMock

from tests.common import TEST_CONTEXT
from tests.const import ATTR_ENTITY_STATE, ATTR_NOTIFY_PROVIDER, ATTR_SERVICE_NAME
from tests.tst_context import TstContext


NOTIFY_PROVIDER_MOCK = "notify_mock"


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_plugin(plugin_api, hass_api_mock, config)
    if notify_provider := config.get(ATTR_NOTIFY_PROVIDER, None):
        setup_mock_notify_provider(plugin_api, hass_api, notify_provider)
    notify_service = config.get(ATTR_SERVICE_NAME)
    if notify_service:
        hass_api_mock.hass_register_service(NOTIFY_DOMAIN, notify_service)


def setup_mock_notify_provider(plugin_api: PluginApi, hass_api: HassApi, notify_provider: str):
    plugin_api.register_plugin_provider(
        PROVIDER_TYPE_NOTIFY, 
        notify_provider,
        NotifyProviderMock(plugin_api, hass_api))


class NotifyProviderMock(NotifyProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        context: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_EVENT_MESSAGE: message,
            ATTR_EVENT_FEEDBACK_ITEMS: ",".join(
                map(lambda x: "|".join([ x.title, x.feedback, x.acknowledgement ]), 
                feedback_items))
        })


    async def async_confirm_feedback(self, context: Context, conversation_id: str, message_id: str, text: str, acknowledgement: str):
        context: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        context.register_plugin_data({
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: conversation_id,
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: message_id,
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: text,
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: acknowledgement
        })