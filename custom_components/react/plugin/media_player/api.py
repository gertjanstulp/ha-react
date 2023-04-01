from homeassistant.core import Context

from custom_components.react.plugin.const import (
    SERVICE_TYPE_DEFAULT
)
from custom_components.react.plugin.media_player.const import PLUGIN_NAME
from custom_components.react.plugin.media_player.service import MediaPlayerService
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class MediaPlayerApiConfig(DynamicData):
    """ api config """
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.default_service_type: str = SERVICE_TYPE_DEFAULT
        self.load(source)


class MediaPlayerApi():
    def __init__(self, plugin_api: PluginApi, config: MediaPlayerApiConfig) -> None:
        self.plugin_api = plugin_api
        self.config = config
        self.default_service_type = config.default_service_type


    def _debug(self, message: str):
        _LOGGER.debug(f"Mediaplayer plugin: Api - {message}")

    
    async def async_play_favorite(self, 
        context: Context,
        service_type: str, 
        entity_id: str,
        favorite_id: str
    ):
        self._debug(f"Playing favorite {favorite_id} '{favorite_id}' on '{entity_id}'")
        try:
            if not service_type:
                service_type = self.default_service_type
            service: MediaPlayerService = self.plugin_api.get_service(PLUGIN_NAME, service_type)
            if service:
                await service.async_play_favorite(context, entity_id, favorite_id)
            else:
                _LOGGER.error(f"Mediaplayer plugin: Api - Service for '{service_type}' not found")
            
        except:
            _LOGGER.exception("Mediaplayer plugin: Api - Playing media failed")
