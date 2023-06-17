from homeassistant.components.mqtt.models import PublishPayloadType
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_MQTT
from custom_components.react.plugin.mqtt.config import MqttConfig
from custom_components.react.plugin.mqtt.const import MQTT_GENERIC_PROVIDER
from custom_components.react.plugin.mqtt.provider import MqttProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session


class MqttApi(PluginApiBase[MqttConfig]):

    async def async_mqtt_publish(self, session: Session, context: Context, entity_id: str, payload: PublishPayloadType, mqtt_provider: str):
        try:
            session.debug(self.logger, f"Publishing to topic {entity_id}")
            provider = self.get_mqtt_provider(session, mqtt_provider)
            if provider:
                await provider.async_publish(session, context, entity_id, payload)
        except:
            session.exception("publishing failed")


    def get_mqtt_provider(self, session: Session, mqtt_provider: str) -> MqttProvider:
        mqtt_provider = mqtt_provider or self.plugin.config.mqtt_provider or MQTT_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_MQTT, mqtt_provider)
        if not result:
            session.error(self.plugin.logger, f"Mqtt provider for '{mqtt_provider}' not found")
            return None
        return result
