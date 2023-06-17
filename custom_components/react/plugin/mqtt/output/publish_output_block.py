from __future__ import annotations

from homeassistant.components.mqtt import SERVICE_PUBLISH
from homeassistant.components.mqtt.models import PublishPayloadType
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_MQTT
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.mqtt.api import MqttApi
from custom_components.react.plugin.mqtt.config import MqttConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class MqttPublishOutputBlock(OutputBlock[MqttConfig], ApiType[MqttApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MqttPublishReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_MQTT, 
            SERVICE_PUBLISH
        )]


    async def async_handle_event(self, react_event: MqttPublishReactionEvent):
        react_event.session.debug(self.logger, f"Mqtt publish reaction caught: '{react_event.payload.entity}'")
        await self.api.async_mqtt_publish(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.payload if react_event.payload.data else None,
            react_event.payload.data.mqtt_provider if react_event.payload.data else None,
        )
        

class MqttPublishReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.mqtt_provider: str = None
        self.payload: PublishPayloadType = None

        self.load(source)


class MqttPublishReactionEvent(ReactionEvent[MqttPublishReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, MqttPublishReactionEventData)
