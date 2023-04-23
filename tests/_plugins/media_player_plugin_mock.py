from __future__ import annotations

from homeassistant.components.media_player import ATTR_MEDIA_VOLUME_LEVEL
from homeassistant.components.tts import ATTR_CACHE
from homeassistant.core import Context
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)

from custom_components.react.const import (
    ATTR_EVENT_MESSAGE, 
    ATTR_MODE,
)
from custom_components.react.plugin.const import (
    PROVIDER_TYPE_MEDIA_PLAYER,
    PROVIDER_TYPE_TTS
)
from custom_components.react.plugin.media_player.api import MediaPlayerConfig
from custom_components.react.plugin.media_player.plugin import load as load_plugin
from custom_components.react.plugin.media_player.provider import MediaPlayerProvider, TtsProvider
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData
from tests._plugins.common import HassApiMock

from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_MEDIA_PLAYER_FAVORITE_ID,
    ATTR_MEDIA_PLAYER_PROVIDER,
    ATTR_TTS_EVENT_LANGUAGE, 
    ATTR_TTS_EVENT_OPTIONS,
    ATTR_TTS_PROVIDER
)
from tests.tst_context import TstContext


MEDIA_PLAYER_PROVIDER_MOCK = "media_player_mock"
TTS_PROVIDER_MOCK = "tts_mock"


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_plugin(plugin_api, hass_api_mock, config)
    if media_player_provider := config.get(ATTR_MEDIA_PLAYER_PROVIDER, None):
        setup_mock_media_player_provider(plugin_api, hass_api, media_player_provider)
    if tts_provider := config.get(ATTR_TTS_PROVIDER, None):
        setup_mock_tts_provider(plugin_api, hass_api, tts_provider)
    media_player_entity_id = config.get(ATTR_ENTITY_ID)
    media_player_state = config.get(ATTR_ENTITY_STATE, None)
    if media_player_entity_id and media_player_state != None:
        hass_api_mock.hass_register_state(media_player_entity_id, media_player_state)


def setup_mock_media_player_provider(plugin_api: PluginApi, hass_api: HassApi, media_player_provider: str):
    plugin_api.register_plugin_provider(
        PROVIDER_TYPE_MEDIA_PLAYER, 
        media_player_provider,
        MediaPlayerProviderMock(plugin_api, hass_api))


def setup_mock_tts_provider(plugin_api: PluginApi, hass_api: HassApi, tts_provider: str):
    plugin_api.register_plugin_provider(
        PROVIDER_TYPE_TTS, 
        tts_provider,
        TtsProviderMock(plugin_api, hass_api))


class MediaPlayerConfigMock(MediaPlayerConfig):
    def __init__(self, source: dict = None) -> None:
        self.fail: str = None
        self.support_announce: bool = False
        super().__init__(source)


class MediaPlayerProviderMock(MediaPlayerProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi, support_announce: bool = False) -> None:
        super().__init__(plugin_api, hass_api)
        self._support_announce = support_announce


    @property
    def support_announce(self) -> bool:
        return self._support_announce


    async def async_play_favorite(self, context: Context, entity_id: str, favorite_id: str):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_PLAYER_FAVORITE_ID: favorite_id,
        })


    async def async_suspend(self, context: Context, entity_id: str):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MODE: "suspend",
        })


    async def async_resume(self, context: Context, entity_id: str):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MODE: "resume",
        })

    
    async def async_set_volume(self, context: Context, entity_id: str, volume: float):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_VOLUME_LEVEL: volume
        })


class TtsProviderMock(TtsProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_speek(self, context: Context, entity_id: str, message: str, language: str, cache: bool, options: DynamicData):
        context: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_EVENT_MESSAGE: message,
            ATTR_TTS_EVENT_LANGUAGE: language,
            ATTR_CACHE: cache,
            ATTR_TTS_EVENT_OPTIONS: options
        })
