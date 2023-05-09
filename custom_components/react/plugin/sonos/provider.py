from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    SERVICE_PLAY_MEDIA
)
from homeassistant.components.sonos.const import (
    DOMAIN as SONOS_DOMAIN
)
from homeassistant.components.sonos.media_player import (
    SERVICE_RESTORE,
    SERVICE_SNAPSHOT,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    Platform,
)
from homeassistant.core import Context

from custom_components.react.plugin.media_player.provider import MediaPlayerProvider
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.sonos.const import CONTENT_TYPE_FAVORITE_ITEM_ID
from custom_components.react.utils.logger import get_react_logger

_LOGGER = get_react_logger()


class SonosProvider(MediaPlayerProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    def _debug(self, message: str):
        _LOGGER.debug(f"Sonos plugin: Provider - {message}")


    @property
    def support_announce(self) -> bool:
        return False


    async def async_suspend(self, context: Context, entity_id: str):
        self._debug(f"Suspending '{entity_id}'")
        try:
            await self.hass_api.async_hass_call_service(
                SONOS_DOMAIN,
                SERVICE_SNAPSHOT,
                {
                    ATTR_ENTITY_ID: entity_id,
                },
                context,
            )
        except:
            _LOGGER.exception("Interrupting mediaplayer failed")


    async def async_resume(self, context: Context, entity_id: str):
        self._debug(f"Resuming '{entity_id}'")
        try:
            await self.hass_api.async_hass_call_service(
                SONOS_DOMAIN,
                SERVICE_RESTORE,
                {
                    ATTR_ENTITY_ID: entity_id,
                },
                context,
            )
        except:
            _LOGGER.exception("Resuming mediaplayer failed")
        

    async def async_play_favorite(self, context: Context, entity_id: str, favorite_id: str):
        data: dict = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_CONTENT_TYPE: CONTENT_TYPE_FAVORITE_ITEM_ID,
            ATTR_MEDIA_CONTENT_ID: favorite_id
        }

        await self.hass_api.async_hass_call_service(
            Platform.MEDIA_PLAYER, 
            SERVICE_PLAY_MEDIA,
            data, 
            context
        )
