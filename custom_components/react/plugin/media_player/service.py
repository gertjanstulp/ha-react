from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_PLAY_MEDIA
)
from homeassistant.const import (
    ATTR_ENTITY_ID
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase


class MediaPlayerService():
    def __init__(self, react: ReactBase) -> None:
        self.react = react

    
    async def async_play_favorite(self, context: Context, entity_id: str, favorite_id: str):
        raise NotImplementedError()