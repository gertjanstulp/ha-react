from custom_components.react.utils.struct import DynamicData


class MediaPlayerConfig(DynamicData):
    """ api config """
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.media_player_provider: str = None
        self.tts_provider: str = None
        self.tts_language: str = None
        self.load(source)
