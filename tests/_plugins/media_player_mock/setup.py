from __future__ import annotations

from homeassistant.components.media_player import ATTR_MEDIA_VOLUME_LEVEL
from homeassistant.components.tts import ATTR_CACHE
from homeassistant.core import Context
from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.const import (
    ATTR_EVENT_MESSAGE, 
    ATTR_MODE,
)
from custom_components.react.plugin.const import (
    PROVIDER_TYPE_MEDIA_PLAYER,
    PROVIDER_TYPE_TTS
)
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.media_player.setup import Setup as MediaPlayerSetup
from custom_components.react.plugin.media_player.provider import MediaPlayerProvider, TtsProvider
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMockExtend
from tests._plugins.media_player_mock.const import (
    ATTR_SETUP_MOCK_MEDIA_PLAYER_PROVIDER, 
    ATTR_SETUP_MOCK_TTS_PROVIDER,
    ATTR_SUPPORT_ANNOUNCE, 
    MEDIA_PLAYER_PROVIDER_MOCK, 
    TTS_PROVIDER_MOCK,
)
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_MEDIA_PLAYER_FAVORITE_ID,
    ATTR_TTS_EVENT_LANGUAGE, 
    ATTR_TTS_EVENT_OPTIONS,
    TEST_CONFIG
)
from tests.tst_context import TstContext


class Setup(MediaPlayerSetup, HassApiMockExtend):
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_media_player_provider = test_config.get(ATTR_SETUP_MOCK_MEDIA_PLAYER_PROVIDER, False)
        self.setup_mock_tts_provider = test_config.get(ATTR_SETUP_MOCK_TTS_PROVIDER, None)
        self.support_announce = test_config.get(ATTR_SUPPORT_ANNOUNCE, False)
        media_player_entity_id = test_config.get(ATTR_ENTITY_ID, None)
        media_player_state = test_config.get(ATTR_ENTITY_STATE, None)
        if media_player_entity_id and media_player_state != None:
            self.hass_api_mock.hass_register_state(media_player_entity_id, media_player_state)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_tts_provider:
            setup(
                TtsProviderMock,
                PROVIDER_TYPE_TTS, 
                TTS_PROVIDER_MOCK,
            )

        if self.setup_mock_media_player_provider:
            setup(
                MediaPlayerProviderMock,
                PROVIDER_TYPE_MEDIA_PLAYER,
                MEDIA_PLAYER_PROVIDER_MOCK,
                support_announce=self.support_announce,
            )
            

class MediaPlayerProviderMock(MediaPlayerProvider):
    def __init__(self, support_announce: bool = False) -> None:
        super().__init__()
        self._support_announce = support_announce


    @property
    def support_announce(self) -> bool:
        return self._support_announce


    async def async_play_favorite(self, session: Session, context: Context, entity_id: str, favorite_id: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_PLAYER_FAVORITE_ID: favorite_id,
        })


    async def async_pause(self, session: Session, context: Context, entity_id: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
        })


    async def async_suspend(self, session: Session, context: Context, entity_id: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MODE: "suspend",
        })


    async def async_resume(self, session: Session, context: Context, entity_id: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MODE: "resume",
        })

    
    async def async_set_volume(self, session: Session, context: Context, entity_id: str, volume: float):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_VOLUME_LEVEL: volume
        })


class TtsProviderMock(TtsProvider):
    def __init__(self) -> None:
        super().__init__()
        
    async def async_speek(self, session: Session, context: Context, entity_id: str, message: str, language: str, cache: bool, options: DynamicData):
        context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_EVENT_MESSAGE: message,
            ATTR_TTS_EVENT_LANGUAGE: language,
            ATTR_CACHE: cache,
            ATTR_TTS_EVENT_OPTIONS: options
        })
