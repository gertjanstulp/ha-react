from homeassistant.components.mqtt import ATTR_PAYLOAD
from homeassistant.components.mqtt.models import PublishPayloadType
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_MQTT
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.mqtt.setup import Setup as MqttSetup
from custom_components.react.plugin.mqtt.provider import MqttProvider
from custom_components.react.utils.session import Session

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

MQTT_MOCK_PROVIDER = "mqtt_mock"


class Setup(MqttSetup, HassApiMockExtend):

    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        
        mqtt_entity_id = test_config.get(ATTR_ENTITY_ID)
        mqtt_state = test_config.get(ATTR_ENTITY_STATE, None)
        if mqtt_entity_id and mqtt_state != None:
            self.hass_api_mock.hass_register_state(mqtt_entity_id, mqtt_state)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(MqttProviderMock, PROVIDER_TYPE_MQTT, MQTT_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)
    

class MqttProviderMock(MqttProvider):

    async def async_publish(self, session: Session, context: Context, entity_id: str, payload: PublishPayloadType):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_PAYLOAD: payload,
        }
        test_context.register_plugin_data(data)
