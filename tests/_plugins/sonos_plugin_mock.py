from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.components.sonos import DOMAIN as SONOS_DOMAIN

from custom_components.react.plugin.media_player.plugin import load as load_media_player_plugin
from custom_components.react.plugin.sonos.plugin import load as load_sonos_plugin
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests._plugins.media_player_plugin_mock import (
    TTS_PROVIDER_MOCK, 
    setup_mock_tts_provider
)
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_MEDIA_PLAYER_PROVIDER, 
    ATTR_TTS_PROVIDER
)


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_sonos_plugin(plugin_api, hass_api_mock, config)

    load_media_player_plugin(
        plugin_api, 
        hass_api_mock, 
        { 
            ATTR_MEDIA_PLAYER_PROVIDER: SONOS_DOMAIN,
            ATTR_TTS_PROVIDER: TTS_PROVIDER_MOCK,
        }
    )
    
    if tts_provider := config.get(ATTR_TTS_PROVIDER, None):
        setup_mock_tts_provider(plugin_api, hass_api, tts_provider)
    media_player_entity_id = config.get(ATTR_ENTITY_ID)
    media_player_state = config.get(ATTR_ENTITY_STATE, None)
    if media_player_entity_id and media_player_state != None:
        hass_api_mock.hass_register_state(media_player_entity_id, media_player_state)

        