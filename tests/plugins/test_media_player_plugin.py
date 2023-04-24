import pytest

from homeassistant.components.media_player import ATTR_MEDIA_VOLUME_LEVEL
from homeassistant.components.tts import ATTR_CACHE
from homeassistant.const import (
    ATTR_ENTITY_ID
)

from custom_components.react.const import ATTR_EVENT_MESSAGE, ATTR_MODE, ATTR_PLUGIN_MODULE, ATTR_WAIT, DOMAIN
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.media_player.const import ATTR_MEDIA_PLAYER_PROVIDER, ATTR_TTS_PROVIDER
from tests._plugins.media_player_mock.plugin import MEDIA_PLAYER_PROVIDER_MOCK, TTS_PROVIDER_MOCK

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
)
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_MEDIA_PLAYER_FAVORITE_ID,
    ATTR_TTS_EVENT_LANGUAGE, 
    ATTR_TTS_EVENT_OPTIONS, 
    TEST_CONFIG
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


def get_mock_plugin(
    media_player_provider: str = None,
    tts_provider: str = None,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.media_player_mock", 
        ATTR_CONFIG : {
        }
    }
    if media_player_provider:
        result[ATTR_CONFIG][ATTR_MEDIA_PLAYER_PROVIDER] = media_player_provider
    if tts_provider:
        result[ATTR_CONFIG][ATTR_TTS_PROVIDER] = tts_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_plugin_api_play_favorite_no_mediaplayer_entity(test_context: TstContext, workflow_name: str):
    await run_media_player_plugin_api_entity_test(test_context, workflow_name, "media_player_play_favorite_test")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek_no_mediaplayer_entity(test_context: TstContext, workflow_name: str):
    await run_media_player_plugin_api_entity_test(test_context, workflow_name, "browser")


async def run_media_player_plugin_api_entity_test(test_context: TstContext, workflow_name: str, media_player_entity_id: str):
    entity_id = f"media_player.{media_player_entity_id}"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
    )
    
    await test_context.async_start_react(mock_plugin)
        
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_plugin_data_not_sent()
        test_context.verify_has_log_warning(f"Mediaplayer plugin: Api - {entity_id} not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_plugin_api_play_favorite_no_mediaplayer_provider(test_context: TstContext, workflow_name: str):
    await run_media_player_plugin_api_no_provider_test(test_context, workflow_name, "media_player_play_favorite_test", fake_media_player_provider=True)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek_no_mediaplayer_provider(test_context: TstContext, workflow_name: str):
    await run_media_player_plugin_api_no_provider_test(test_context, workflow_name, "browser", fake_media_player_provider=True)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek_no_tts_provider(test_context: TstContext, workflow_name: str):
    await run_media_player_plugin_api_no_provider_test(test_context, workflow_name, "browser", fake_media_player_provider=True)


async def run_media_player_plugin_api_no_provider_test(test_context: TstContext, workflow_name: str, media_player_entity_id: str, fake_media_player_provider: bool = False, fake_tts_provider: bool = False):
    entity_id = f"media_player.{media_player_entity_id}"
    mock_plugin = get_mock_plugin(
        media_player_provider=None if fake_media_player_provider else MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=None if fake_tts_provider else TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped"
    )
    
    await test_context.async_start_react(mock_plugin)
        
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_plugin_data_not_sent()
        test_context.verify_has_log_error(f"Mediaplayer plugin: Api - {'Mediaplayer' if fake_media_player_provider else 'Tts'} provider for '{entity_id if fake_media_player_provider else TTS_PROVIDER_MOCK}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_plugin_api_play_favorite(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.media_player_play_favorite_test"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )
   
    await test_context.async_start_react(mock_plugin)
        
    plugin_data = {
        ATTR_ENTITY_ID: "media_player_play_favorite_test",
        ATTR_MEDIA_PLAYER_FAVORITE_ID: "test_id"
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(plugin_data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugin)
        
    plugin_data_speek = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test without volume",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent(expected_count=1)
        test_context.verify_plugin_data_content(plugin_data_speek, data_index=0)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_volume_test"])
async def test_media_player_plugin_api_speek_with_volume(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugin)
        
    plugin_data_speek = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test with volume",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }

    plugin_data_volume = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_MEDIA_VOLUME_LEVEL: 0.1
    }
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_content(plugin_data_volume, data_index=0)
        test_context.verify_plugin_data_content(plugin_data_speek, data_index=1)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_announce_test"])
async def test_media_player_plugin_api_speek_with_announce(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugin)
        
    plugin_data_suspend = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_MODE: "suspend"
    }

    plugin_data_speek = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test with announce",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }

    plugin_data_resume = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_MODE: "resume"
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent(expected_count=3)
        test_context.verify_plugin_data_content(plugin_data_suspend, data_index=0)
        test_context.verify_plugin_data_content(plugin_data_speek, data_index=1)
        test_context.verify_plugin_data_content(plugin_data_resume, data_index=2)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_wait_test"])
async def test_media_player_plugin_api_speek_with_wait(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugin)
        
    plugin_data_speek = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test with wait",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }

    plugin_data_wait = {
        ATTR_WAIT: 3,
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent(expected_count=2)
        test_context.verify_plugin_data_content(plugin_data_speek, data_index=0)
        test_context.verify_plugin_data_content(plugin_data_wait, data_index=1)
