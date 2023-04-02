from homeassistant.components.tts import DOMAIN as TTS_DOMAIN, SpeechManager
from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.plugin.google_translate.plugin import load as load_google_translate_plugin
from custom_components.react.plugin.google_translate.const import TTS_GOOGLE_TRANSLATE_PROVIDER
from custom_components.react.plugin.media_player.plugin import load as load_media_player_plugin
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests._plugins.media_player_plugin_mock import MEDIA_PLAYER_PROVIDER_MOCK, setup_mock_media_player_provider
from tests.const import ATTR_ENTITY_STATE, ATTR_MEDIA_PLAYER_PROVIDER, ATTR_TTS_PROVIDER


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_google_translate_plugin(plugin_api, hass_api_mock, config)

    load_media_player_plugin(
        plugin_api, 
        hass_api_mock, 
        { 
            ATTR_MEDIA_PLAYER_PROVIDER: MEDIA_PLAYER_PROVIDER_MOCK,
            ATTR_TTS_PROVIDER: TTS_GOOGLE_TRANSLATE_PROVIDER,
        }
    )
    
    setup_mock_media_player_provider(plugin_api, hass_api, MEDIA_PLAYER_PROVIDER_MOCK)

    media_player_entity_id = config.get(ATTR_ENTITY_ID)
    media_player_state = config.get(ATTR_ENTITY_STATE, None)
    if media_player_entity_id and media_player_state != None:
        hass_api_mock.hass_register_state(media_player_entity_id, media_player_state)

        