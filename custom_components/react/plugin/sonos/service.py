from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    SERVICE_PLAY_MEDIA
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    Platform,
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.media_player.service import MediaPlayerService
from custom_components.react.plugin.sonos.const import CONTENT_TYPE_FAVORITE_ITEM_ID


class SonosService(MediaPlayerService):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    async def async_play_favorite(self, context: Context, entity_id: str, favorite_id: str):
        data: dict = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_CONTENT_TYPE: CONTENT_TYPE_FAVORITE_ITEM_ID,
            ATTR_MEDIA_CONTENT_ID: favorite_id
        }

        await self.react.hass.services.async_call(
            Platform.MEDIA_PLAYER, 
            SERVICE_PLAY_MEDIA,
            data, 
            context
        )
