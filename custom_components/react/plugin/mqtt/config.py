from custom_components.react.utils.struct import DynamicData


class MqttConfigEntityMap(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.entity_id: str = None
        self.mapped_entity_id: str = None
        self.short_press_action: str = None
        self.long_press_action: str = None
        self.double_press_action: str = None
        self.load(source)


class MqttConfig(DynamicData):
    type_hints: dict = {"entity_maps": MqttConfigEntityMap}

    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.mqtt_provider: str = None
        self.entity_maps: list[MqttConfigEntityMap] = []
        self.load(source)
