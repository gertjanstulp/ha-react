from custom_components.react.utils.struct import DynamicData


class MqttConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.mqtt_provider: str = None
        self.load(source)