from typing import Any
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.components.media_player.const import MediaType
from homeassistant.const import (
    CONF_UNIQUE_ID
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from custom_components.virtual.const import CONF_NAME


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    player = VirtualMediaPlayer(hass, config)
    async_add_entities([player])


class VirtualMediaPlayer(MediaPlayerEntity):
    # _attr_state: MediaPlayerState | None = None
    # _attr_supported_features: MediaPlayerEntityFeature = MediaPlayerEntityFeature(0)
    

    def __init__(self, hass: HomeAssistant, config: ConfigType):
        self.hass = hass
        self.config = config
        self._name = config.get(CONF_NAME)
        self._attrs = {}
        self._attr_unique_id = config.get(CONF_UNIQUE_ID)
        self._state = MediaPlayerState.IDLE

        self._media_content_type: MediaType | str = None
        self._media_content_id: str = None


    async def async_play_media(self, media_type: MediaType | str, media_id: str, **kwargs: Any) -> None:
        self._media_content_type = media_type
        self._media_content_id = media_id
        self._state = MediaPlayerState.PLAYING

    
    async def async_media_pause(self) -> None:
        self._state = MediaPlayerState.PAUSED


    async def async_media_play(self) -> None:
        self._state = MediaPlayerState.PLAYING


    @property
    def name(self):
        return self._name
    

    @property
    def state(self) -> MediaPlayerState | None:
        return self._state


    @property
    def media_content_id(self):
        return self._media_content_id


    @property
    def media_content_type(self):
        return self._media_content_type
    

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        flags: MediaPlayerEntityFeature =  MediaPlayerEntityFeature(
            MediaPlayerEntityFeature.TURN_ON |
            MediaPlayerEntityFeature.TURN_OFF |
            MediaPlayerEntityFeature.PLAY | 
            MediaPlayerEntityFeature.PAUSE |
            MediaPlayerEntityFeature.STOP | 
            MediaPlayerEntityFeature.PLAY_MEDIA
        )
        return flags
