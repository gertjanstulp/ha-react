from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_PLAY_MEDIA
)

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.plugin.media_player.provider import MediaPlayerProvider
from custom_components.react.plugin.spotify.const import (
    CONTENT_TYPE_ALBUM,
    CONTENT_TYPE_PLAYLIST,
)
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData


class SpotifyProvider(MediaPlayerProvider[DynamicData]):

    @property
    def support_announce(self) -> bool:
        return False

    
    async def async_play_album(self, session: Session, context: Context, entity_id: str, album_id: str):
        await self.async_play_item(session, context, entity_id, CONTENT_TYPE_ALBUM, album_id)


    async def async_play_playlist(self, session: Session, context: Context, entity_id: str, playlist_id: str):
        await self.async_play_item(session, context, entity_id, CONTENT_TYPE_PLAYLIST, playlist_id)


    async def async_play_item(self, session: Session, context: Context, entity_id: str, item_type: str, item_id: str):
        data: dict = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_CONTENT_TYPE: item_type,
            ATTR_MEDIA_CONTENT_ID: f"spotify:{item_type}:{item_id}",
        }

        await self.plugin.hass_api.async_hass_call_service(
            MEDIA_PLAYER_DOMAIN,
            SERVICE_PLAY_MEDIA,
            service_data=data, 
            context=context,
        )

