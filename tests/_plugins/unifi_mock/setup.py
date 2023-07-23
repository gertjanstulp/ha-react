from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_UNIFI
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.unifi.setup import Setup as UnifiSetup
from custom_components.react.plugin.unifi.provider import UnifiProvider
from custom_components.react.utils.session import Session

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_DEVICE_DISABLED,
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

UNIFI_MOCK_PROVIDER = "unifi_mock"


class Setup(UnifiSetup, HassApiMockExtend):
    
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        
        unifi_device_id = test_config.get(ATTR_DEVICE_ID)
        unifi_device_disabled = test_config.get(ATTR_DEVICE_DISABLED, False)
        if unifi_device_id:
            self.hass_api_mock.hass_register_device(unifi_device_id, unifi_device_disabled)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(UnifiProviderMock, PROVIDER_TYPE_UNIFI, UNIFI_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)


class UnifiProviderMock(UnifiProvider):

    async def async_unifi_set_value(self, session: Session, context: Context, device_id: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_DEVICE_ID: device_id,
        }
        test_context.register_plugin_data(data)
