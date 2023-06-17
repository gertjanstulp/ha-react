from homeassistant.components.mqtt import (
    DOMAIN as MQTT_DOMAIN,
    SERVICE_PUBLISH, 
    ATTR_TOPIC,
    ATTR_PAYLOAD,
)
from homeassistant.components.mqtt.models import PublishPayloadType
from homeassistant.core import Context

from custom_components.react.plugin.mqtt.config import MqttConfig
from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session


class MqttProvider(PluginProviderBase[MqttConfig]):

    async def async_publish(self, session: Session, context: Context, entity_id: str, payload: PublishPayloadType = None):
        data = {
            ATTR_TOPIC: entity_id,
        }
        if payload != None:
            data[ATTR_PAYLOAD] = payload
        await self.plugin.hass_api.async_hass_call_service(
            MQTT_DOMAIN,
            SERVICE_PUBLISH,
            data,
            context,
        )
