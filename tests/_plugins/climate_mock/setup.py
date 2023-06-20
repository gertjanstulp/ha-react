from __future__ import annotations

from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_CLIMATE
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.climate.setup import Setup as ClimateSetup
from custom_components.react.plugin.climate.provider import ClimateProvider
from custom_components.react.utils.session import Session

from tests._plugins.common import HassApiMockExtend
from tests._plugins.climate_mock.const import (
    ATTR_SETUP_MOCK_CLIMATE_PROVIDER, 
    CLIMATE_PROVIDER_MOCK, 
)
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_ENTITY_STATE_ATTRIBUTES,
    TEST_CONFIG
)
from tests.tst_context import TstContext


class Setup(ClimateSetup, HassApiMockExtend):
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_climate_provider = test_config.get(ATTR_SETUP_MOCK_CLIMATE_PROVIDER, False)
        climate_entity_id = test_config.get(ATTR_ENTITY_ID, None)
        climate_state = test_config.get(ATTR_ENTITY_STATE, None)
        climate_state_attributes = test_config.get(ATTR_ENTITY_STATE_ATTRIBUTES, None)
        if climate_entity_id and climate_state != None:
            self.hass_api_mock.hass_register_state(climate_entity_id, climate_state, climate_state_attributes)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_climate_provider:
            setup(
                ClimateProviderMock,
                PROVIDER_TYPE_CLIMATE,
                CLIMATE_PROVIDER_MOCK,
            )
        else:
            super().setup_provider(setup)
            

class ClimateProviderMock(ClimateProvider):
    def __init__(self, support_announce: bool = False) -> None:
        super().__init__()
        self._support_announce = support_announce


    @property
    def support_announce(self) -> bool:
        return self._support_announce

    async def async_set_temperature(self, session: Session, context: Context, entity_id: str, temperature: float):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_TEMPERATURE: temperature,
        })
