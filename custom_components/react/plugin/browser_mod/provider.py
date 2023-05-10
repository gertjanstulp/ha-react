from custom_components.react.plugin.media_player.provider import MediaPlayerProvider
from custom_components.react.utils.struct import DynamicData


class BrowserModProvider(MediaPlayerProvider[DynamicData]):

    @property
    def support_announce(self) -> bool:
        return True
