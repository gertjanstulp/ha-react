from homeassistant.components.hassio import ATTR_ADDON
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_HASSIO
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.hassio.setup import Setup as HassioSetup
from custom_components.react.plugin.hassio.provider import HassioProvider
from custom_components.react.utils.session import Session

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

HASSIO_MOCK_PROVIDER = "hassio_mock"


class Setup(HassioSetup, HassApiMockExtend):
    
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        

    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(HassioProviderMock, PROVIDER_TYPE_HASSIO, HASSIO_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)


class HassioProviderMock(HassioProvider):

    async def async_restart_addon(self, session: Session, context: Context, addon: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ADDON: addon,
        }
        test_context.register_plugin_data(data)
