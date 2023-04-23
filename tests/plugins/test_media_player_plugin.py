import pytest

from homeassistant.components.media_player import ATTR_MEDIA_VOLUME_LEVEL
from homeassistant.components.tts import ATTR_CACHE
from homeassistant.const import (
    ATTR_ENTITY_ID
)
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_EVENT_MESSAGE, ATTR_MODE, ATTR_PLUGIN_MODULE, ATTR_WAIT, DOMAIN
from custom_components.react.plugin.const import ATTR_CONFIG
from tests._plugins.media_player_plugin_mock import MEDIA_PLAYER_PROVIDER_MOCK, TTS_PROVIDER_MOCK

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
    TEST_CONTEXT
)
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_FAIL,
    ATTR_MEDIA_PLAYER_FAVORITE_ID,
    ATTR_MEDIA_PLAYER_PROVIDER,
    ATTR_TTS_EVENT_LANGUAGE, 
    ATTR_TTS_EVENT_OPTIONS, 
    ATTR_TTS_PROVIDER
)
from tests.tst_context import TstContext


def get_mock_plugin(
    media_player_provider: str = None,
    tts_provider: str = None,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.media_player_plugin_mock", 
        ATTR_CONFIG : {
        }
    }

    if media_player_provider:
        result[ATTR_CONFIG][ATTR_MEDIA_PLAYER_PROVIDER] = media_player_provider
    if tts_provider:
        result[ATTR_CONFIG][ATTR_TTS_PROVIDER] = tts_provider
    if media_player_entity_id:
        result[ATTR_CONFIG][ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_CONFIG][ATTR_ENTITY_STATE] = media_player_entity_state

    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_plugin_api_play_favorite_no_mediaplayer_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_media_player_plugin_api_entity_test(hass, workflow_name, react_component, "media_player_play_favorite_test")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek_no_mediaplayer_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_media_player_plugin_api_entity_test(hass, workflow_name, react_component, "browser")


async def run_media_player_plugin_api_entity_test(hass: HomeAssistant, workflow_name, react_component, media_player_entity_id: str):
    entity_id = f"media_player.{media_player_entity_id}"
    mock_plugin = get_mock_plugin()
    
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_plugin_data_not_sent()
        tc.verify_has_log_warning(f"Mediaplayer plugin: Api - {entity_id} not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_plugin_api_play_favorite_no_mediaplayer_provider(hass: HomeAssistant, workflow_name, react_component):
    await run_media_player_plugin_api_no_provider_test(hass, workflow_name, react_component, "media_player_play_favorite_test", fake_media_player_provider=True)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek_no_mediaplayer_provider(hass: HomeAssistant, workflow_name, react_component):
    await run_media_player_plugin_api_no_provider_test(hass, workflow_name, react_component, "browser", fake_media_player_provider=True)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek_no_tts_provider(hass: HomeAssistant, workflow_name, react_component):
    await run_media_player_plugin_api_no_provider_test(hass, workflow_name, react_component, "browser", fake_media_player_provider=True)


async def run_media_player_plugin_api_no_provider_test(hass: HomeAssistant, workflow_name, react_component, media_player_entity_id: str, fake_media_player_provider: bool = False, fake_tts_provider: bool = False):
    entity_id = f"media_player.{media_player_entity_id}"
    mock_plugin = get_mock_plugin(
        media_player_provider=None if fake_media_player_provider else MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=None if fake_tts_provider else TTS_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped"
    )
    
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_plugin_data_not_sent()
        tc.verify_has_log_error(f"Mediaplayer plugin: Api - {'Mediaplayer' if fake_media_player_provider else 'Tts'} provider for '{entity_id if fake_media_player_provider else TTS_PROVIDER_MOCK}' not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_plugin_api_play_favorite(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "media_player.media_player_play_favorite_test"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )
   
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "media_player_play_favorite_test",
        ATTR_MEDIA_PLAYER_FAVORITE_ID: "test_id"
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(plugin_data)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data_speek = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test without volume",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_plugin_data_sent(expected_count=1)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=0)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_volume_test"])
async def test_media_player_plugin_api_speek_with_volume(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
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
    

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_plugin_data_content(plugin_data_volume, data_index=0)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=1)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_announce_test"])
async def test_media_player_plugin_api_speek_with_announce(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
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

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_plugin_data_sent(expected_count=3)
        tc.verify_plugin_data_content(plugin_data_suspend, data_index=0)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=1)
        tc.verify_plugin_data_content(plugin_data_resume, data_index=2)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_wait_test"])
async def test_media_player_plugin_api_speek_with_wait(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
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

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_plugin_data_sent(expected_count=2)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=0)
        tc.verify_plugin_data_content(plugin_data_wait, data_index=1)
