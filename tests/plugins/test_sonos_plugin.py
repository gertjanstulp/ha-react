import pytest

from homeassistant.components.media_player import (
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_VOLUME_LEVEL,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_PLAY_MEDIA,
    SERVICE_VOLUME_SET,
    STATE_OFF,
)
from homeassistant.components.sonos.const import DOMAIN as SONOS_DOMAIN
from homeassistant.components.sonos.media_player import (
    SERVICE_RESTORE,
    SERVICE_SNAPSHOT,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    Platform
)

from custom_components.react.const import (
    ATTR_EVENT_MESSAGE,
    ATTR_PLUGIN_MODULE,
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.media_player.const import ATTR_MEDIA_PLAYER_PROVIDER, ATTR_TTS_PROVIDER
from custom_components.react.plugin.sonos.const import CONTENT_TYPE_FAVORITE_ITEM_ID, MEDIA_PLAYER_SONOS_PROVIDER
from tests._plugins.media_player_mock.const import ATTR_SETUP_MOCK_TTS_PROVIDER
from tests._plugins.media_player_mock.setup import TTS_PROVIDER_MOCK

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_MEDIA_PLAYER_FAVORITE_ID,
    ATTR_TTS_EVENT_ANNOUNCE,
    ATTR_TTS_EVENT_LANGUAGE,
    ATTR_VOLUME,
    TEST_CONFIG, 
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_tts_provider: bool = False,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_TTS_PROVIDER: setup_mock_tts_provider,
    }
    if media_player_entity_id:
        result[ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_ENTITY_STATE] = media_player_entity_state
    

def get_mock_plugins():
    result = [
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.sonos_mock", 
            ATTR_CONFIG: {}
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.media_player_mock", 
            ATTR_CONFIG: { 
                ATTR_MEDIA_PLAYER_PROVIDER: MEDIA_PLAYER_SONOS_PROVIDER,
                ATTR_TTS_PROVIDER: TTS_PROVIDER_MOCK,
            }
        },
    ]
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_sonos_plugin_provider_play_favorite(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.media_player_play_favorite_test"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        media_player_entity_id = entity_id,
        media_player_entity_state = STATE_OFF,
    )

    await test_context.async_start_react(mock_plugins)
        
    favorite_id = "test_id"
    data_in = {
        ATTR_MEDIA_PLAYER_FAVORITE_ID: favorite_id
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_TYPE: CONTENT_TYPE_FAVORITE_ITEM_ID,
        ATTR_MEDIA_CONTENT_ID: favorite_id
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(Platform.MEDIA_PLAYER, SERVICE_PLAY_MEDIA, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speak_with_volume_test"])
async def test_sonos_plugin_provider_speak_with_volume(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugins)
        
    data_in = {
        ATTR_EVENT_MESSAGE: "This is a test with volume",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_VOLUME: 0.1,
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_VOLUME_LEVEL: 0.1
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_VOLUME_SET, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speak_with_announce_test"])
async def test_sonos_plugin_provider_speak_with_announce(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugins)
        
    data_in = {
        ATTR_EVENT_MESSAGE: "This is a test with announce",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_TTS_EVENT_ANNOUNCE: True,
    }
    data_out_suspend = {
        ATTR_ENTITY_ID: entity_id,
    }
    data_out_resume = {
        ATTR_ENTITY_ID: entity_id,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent(expected_count=2)
    test_context.verify_service_call_content(SONOS_DOMAIN, SERVICE_SNAPSHOT, data_out_suspend, data_index=0)
    test_context.verify_service_call_content(SONOS_DOMAIN, SERVICE_RESTORE, data_out_resume, data_index=1)
