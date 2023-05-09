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
    ATTR_PLUGIN_MODULE,
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.media_player.const import ATTR_TTS_PROVIDER
from custom_components.react.plugin.sonos.const import CONTENT_TYPE_FAVORITE_ITEM_ID
from tests._plugins.media_player_mock.plugin import TTS_PROVIDER_MOCK

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE,
    TEST_CONFIG, 
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    tts_provider: str = None,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if tts_provider:
        result[ATTR_TTS_PROVIDER] = tts_provider
    if media_player_entity_id:
        result[ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_ENTITY_STATE] = media_player_entity_state
    

def get_mock_plugin():
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.sonos_mock", 
        ATTR_CONFIG: {}
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_sonos_plugin_provider_play_favorite(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.media_player_play_favorite_test"
    mock_plugin = get_mock_plugin(
    )
    set_test_config(test_context,
        media_player_entity_id = entity_id,
        media_player_entity_state = STATE_OFF,
    )

    await test_context.async_start_react(mock_plugin)
        
    service_data = {
        ATTR_ENTITY_ID: "media_player_play_favorite_test",
        ATTR_MEDIA_CONTENT_TYPE: CONTENT_TYPE_FAVORITE_ITEM_ID,
        ATTR_MEDIA_CONTENT_ID: "test_id"
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(Platform.MEDIA_PLAYER, SERVICE_PLAY_MEDIA, service_data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_volume_test"])
async def test_sonos_plugin_provider_speek_with_volume(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        tts_provider=TTS_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugin)
        
    plugin_data_volume = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_VOLUME_LEVEL: 0.1
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_VOLUME_SET, plugin_data_volume)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_announce_test"])
async def test_sonos_plugin_provider_speek_with_announce(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        tts_provider=TTS_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugin)
        
    data_suspend = {
        ATTR_ENTITY_ID: entity_id,
    }
    data_resume = {
        ATTR_ENTITY_ID: entity_id,
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent(expected_count=2)
        test_context.verify_service_call_content(SONOS_DOMAIN, SERVICE_SNAPSHOT, data_suspend, data_index=0)
        test_context.verify_service_call_content(SONOS_DOMAIN, SERVICE_RESTORE, data_resume, data_index=1)
