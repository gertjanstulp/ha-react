from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, 
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID, 
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID, 
    ATTR_EVENT_FEEDBACK_ITEM_TEXT, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE,
)
from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.notify.setup import Setup as NotifySetup
from custom_components.react.plugin.notify.provider import NotifyProvider

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_SERVICE_NAME,
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


NOTIFY_PROVIDER_MOCK = "notify_mock"


class Setup(NotifySetup, HassApiMockExtend):

    def setup(self):
        super().setup()
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        if notify_service := test_config.get(ATTR_SERVICE_NAME):
            self.hass_api_mock.hass_register_service(NOTIFY_DOMAIN, notify_service)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(NotifyProviderMock, PROVIDER_TYPE_NOTIFY, NOTIFY_PROVIDER_MOCK)
        else:
            super().setup_provider(setup)


class NotifyProviderMock(NotifyProvider):

    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_EVENT_MESSAGE: message,
            ATTR_EVENT_FEEDBACK_ITEMS: ",".join(
                map(lambda x: "|".join([ x.title, x.feedback, x.acknowledgement ]), 
                feedback_items))
        })


    async def async_confirm_feedback(self,
        context: Context, 
        conversation_id: str, 
        message_id: str, 
        text: str, 
        feedback: str,
        acknowledgement: str
    ):
        context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        context.register_plugin_data({
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: conversation_id,
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: message_id,
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: text,
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: acknowledgement
        })