from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from homeassistant.components.media_player.const import (
    DOMAIN, 
    SERVICE_PLAY_MEDIA,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
)

from custom_components.react.base import ReactBase
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()

class ApiConfig(DynamicData):
    """ api config """

class Api():
    def __init__(self, react: ReactBase, config: ApiConfig) -> None:
        self.react = react
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Media-player plugin: Api - {message}")

    
    async def async_play_media(self, context: Context, entity_id: str, media_content_type: str, media_content_id: str):
        self._debug(f"Playing media {media_content_type} '{media_content_id}' on '{entity_id}'")
        try:
            media_data = {
                ATTR_ENTITY_ID: entity_id,
                ATTR_MEDIA_CONTENT_TYPE: media_content_type,
                ATTR_MEDIA_CONTENT_ID: media_content_id
            }
            await self.react.hass.services.async_call(
                DOMAIN,
                SERVICE_PLAY_MEDIA,
                media_data,
                context,
            )
        except:
            _LOGGER.exception("Playing media failed")
