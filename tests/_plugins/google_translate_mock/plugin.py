from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.plugin.google_translate.const import TTS_GOOGLE_TRANSLATE_PROVIDER
from custom_components.react.plugin.google_translate.plugin import Plugin as GoogleTranslatePlugin
from custom_components.react.plugin.media_player.const import (
    ATTR_MEDIA_PLAYER_PROVIDER, 
    ATTR_TTS_PROVIDER
)
from custom_components.react.plugin.media_player.plugin import Plugin as MediaPlayerPlugin
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests._plugins.media_player_mock.plugin import MEDIA_PLAYER_PROVIDER_MOCK, setup_mock_media_player_provider
from tests.const import (
    ATTR_ENTITY_STATE,
    TEST_CONFIG
)


class Plugin(GoogleTranslatePlugin):
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        hass_api_mock = HassApiMock(hass_api.hass)
        super().load(plugin_api, hass_api_mock, config)

        MediaPlayerPlugin().load(
            plugin_api, 
            hass_api_mock, 
            { 
                ATTR_MEDIA_PLAYER_PROVIDER: MEDIA_PLAYER_PROVIDER_MOCK,
                ATTR_TTS_PROVIDER: TTS_GOOGLE_TRANSLATE_PROVIDER,
            }
        )
        
        setup_mock_media_player_provider(plugin_api, hass_api, MEDIA_PLAYER_PROVIDER_MOCK)

        test_config: dict = hass_api.hass_get_data(TEST_CONFIG, {})
        media_player_entity_id = test_config.get(ATTR_ENTITY_ID)
        media_player_state = test_config.get(ATTR_ENTITY_STATE, None)
        if media_player_entity_id and media_player_state != None:
            hass_api_mock.hass_register_state(media_player_entity_id, media_player_state)
