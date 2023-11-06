from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_SHORT_PRESS
from custom_components.react.plugin.mqtt.const import MQTT_BUTTON_ACTION_SINGLE
from custom_components.react.plugin.mqtt.input.button_input_block import MqttButtonInputBlock


class MqttShortPressInputBlock(MqttButtonInputBlock):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MQTT_BUTTON_ACTION_SINGLE, REACT_ACTION_SHORT_PRESS, "short press")
    