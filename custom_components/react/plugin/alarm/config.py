from custom_components.react.utils.struct import DynamicData


class AlarmConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.code: str = None
        self.alarm_provider_name: str = None
        self.load(source)