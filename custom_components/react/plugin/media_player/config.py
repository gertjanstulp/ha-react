from custom_components.react.utils.struct import DynamicData


class MediaPlayerConfig(DynamicData):
    """ api config """
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.media_player_provider_name: str = None
        self.tts_provider_name: str = None
        self.tts_language: str = None
        self.load(source)


class TtsConfig(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.language: str = None
        self.options: DynamicData = None
        self.load(source)