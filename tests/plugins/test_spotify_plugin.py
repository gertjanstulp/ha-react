import pytest

from homeassistant.components.media_player import (
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_PLAY_MEDIA,
    STATE_OFF,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    Platform
)

from custom_components.react.const import ATTR_PLUGIN_MODULE
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.media_player.const import ATTR_MEDIA_PLAYER_PROVIDER
from custom_components.react.plugin.spotify.const import (
    CONTENT_TYPE_ALBUM,
    CONTENT_TYPE_PLAYLIST, 
    MEDIA_PLAYER_SPOTIFY_PROVIDER,
)

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_MEDIA_PLAYER_ALBUM_ID,
    ATTR_MEDIA_PLAYER_PLAYLIST_ID,
    TEST_CONFIG, 
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if media_player_entity_id:
        result[ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_ENTITY_STATE] = media_player_entity_state
    

def get_mock_plugins():
    result = [
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.spotify_mock", 
            ATTR_CONFIG: {}
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.media_player_mock", 
            ATTR_CONFIG: { 
                ATTR_MEDIA_PLAYER_PROVIDER: MEDIA_PLAYER_SPOTIFY_PROVIDER,
            }
        },
    ]
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_album_test"])
async def test_spotify_plugin_provider_play_album(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.media_player_play_album_test"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        media_player_entity_id = entity_id,
        media_player_entity_state = STATE_OFF,
    )

    await test_context.async_start_react(mock_plugins)
        
    album_id = "test_id"
    data_in = {
        ATTR_MEDIA_PLAYER_ALBUM_ID: album_id
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_TYPE: CONTENT_TYPE_ALBUM,
        ATTR_MEDIA_CONTENT_ID: f"spotify:{CONTENT_TYPE_ALBUM}:{album_id}"
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_playlist_test"])
async def test_spotify_plugin_provider_play_playlist(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.media_player_play_playlist_test"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        media_player_entity_id = entity_id,
        media_player_entity_state = STATE_OFF,
    )

    await test_context.async_start_react(mock_plugins)
        
    playlist_id = "test_id"
    data_in = {
        ATTR_MEDIA_PLAYER_PLAYLIST_ID: playlist_id
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_TYPE: CONTENT_TYPE_PLAYLIST,
        ATTR_MEDIA_CONTENT_ID: f"spotify:{CONTENT_TYPE_PLAYLIST}:{playlist_id}"
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data_out)
