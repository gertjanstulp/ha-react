import pytest

from homeassistant.components.media_player import (
    ATTR_MEDIA_VOLUME_LEVEL,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    MediaPlayerState,
)
from homeassistant.components.media_player.const import ATTR_MEDIA_ANNOUNCE
from homeassistant.components.tts import ATTR_CACHE
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
)

from custom_components.react.const import (
    ACTION_CHANGE, 
    ACTION_TOGGLE, 
    ATTR_EVENT_MESSAGE, 
    ATTR_MODE, 
    ATTR_PLUGIN_MODULE, 
    ATTR_WAIT, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.media_player.const import (
    ATTR_MEDIA_PLAYER_PROVIDER, 
    ATTR_TTS_PROVIDER,
)
from tests._plugins.media_player_mock.const import (
    ATTR_SETUP_MOCK_MEDIA_PLAYER_PROVIDER,
    ATTR_SETUP_MOCK_TTS_PROVIDER,
    ATTR_SUPPORT_ANNOUNCE,
    MEDIA_PLAYER_PROVIDER_MOCK, 
    TTS_PROVIDER_MOCK,
)

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
)
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_MEDIA_PLAYER_FAVORITE_ID,
    ATTR_TTS_EVENT_LANGUAGE, 
    ATTR_TTS_EVENT_OPTIONS,
    ATTR_VOLUME, 
    TEST_CONFIG
)
from tests.tst_context import TstContext

FIXTURE_MEDIA_PLAYER_ENTITY_ID = "media_player_entity_id"
FIXTURE_FAKE_MEDIA_PLAYER_PROVIDER = "fake_media_player_provider"
FIXTURE_FAKE_TTS_PROVIDER = "fake_tts_provider"


def set_test_config(test_context: TstContext,
    setup_mock_media_player_provider: bool = False,
    setup_mock_tts_provider: bool = False,
    support_announce: bool = False,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_MEDIA_PLAYER_PROVIDER: setup_mock_media_player_provider,
        ATTR_SETUP_MOCK_TTS_PROVIDER: setup_mock_tts_provider,
        ATTR_SUPPORT_ANNOUNCE: support_announce,
    }
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


@pytest.mark.parametrize(F"{FIXTURE_WORKFLOW_NAME},{FIXTURE_MEDIA_PLAYER_ENTITY_ID}", [
    ("media_player_play_favorite_test", "media_player_play_favorite_test"),
    ("media_player_speek_test", "browser"),
])
async def test_media_player_plugin_api_entity_not_found(test_context: TstContext, workflow_name: str, media_player_entity_id: str):
    entity_id = f"media_player.{media_player_entity_id}"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    data_in = {
        ATTR_EVENT_MESSAGE: "This is a test without volume",
        ATTR_TTS_EVENT_LANGUAGE: "en"
    }
    
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - {entity_id} not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_MEDIA_PLAYER_ENTITY_ID}", [
    ("media_player_play_favorite_test", "media_player_play_favorite_test"),
    ("media_player_speek_test", "browser"),
])
async def test_media_player_plugin_api_no_media_player_provider_set_up(test_context: TstContext, workflow_name: str, media_player_entity_id: str):
    entity_id = f"media_player.{media_player_entity_id}"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=False,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped"
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Mediaplayer provider for '{entity_id}/{MEDIA_PLAYER_PROVIDER_MOCK}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_no_tts_provider_set_up(test_context: TstContext, workflow_name: str):
    entity_id = f"media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        setup_mock_tts_provider=False,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped"
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Tts provider for '{TTS_PROVIDER_MOCK}' not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_MEDIA_PLAYER_ENTITY_ID}", [
    ("media_player_play_favorite_test", "media_player_play_favorite_test"),
    ("media_player_speek_test", "browser"),
])
async def test_media_player_plugin_api_no_media_player_provider_provided(test_context: TstContext, workflow_name: str, media_player_entity_id: str):
    entity_id = f"media_player.{media_player_entity_id}"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped"
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Mediaplayer provider for '{entity_id}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_no_tts_provider_provided(test_context: TstContext, workflow_name: str):
    entity_id = f"media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped"
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Tts provider not provided")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_plugin_api_play_favorite_config_provider(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.media_player_play_favorite_test"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )
   
    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_MEDIA_PLAYER_FAVORITE_ID: "test_id"
    }
    data_out = {
        ATTR_ENTITY_ID: "media_player_play_favorite_test",
        ATTR_MEDIA_PLAYER_FAVORITE_ID: "test_id"
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_plugin_api_play_favorite_event_provider(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.media_player_play_favorite_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )
   
    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_MEDIA_PLAYER_PROVIDER: MEDIA_PLAYER_PROVIDER_MOCK,
        ATTR_MEDIA_PLAYER_FAVORITE_ID: "test_id"
    }
    data_out = {
        ATTR_ENTITY_ID: "media_player_play_favorite_test",
        ATTR_MEDIA_PLAYER_FAVORITE_ID: "test_id"
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek_config_provider(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_EVENT_MESSAGE: "This is a test without volume",
        ATTR_TTS_EVENT_LANGUAGE: "en"
    }
    data_out = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test without volume",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent(expected_count=1)
    test_context.verify_plugin_data_content(data_out, data_index=0)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_media_player_plugin_api_speek_event_provider(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_MEDIA_PLAYER_PROVIDER: MEDIA_PLAYER_PROVIDER_MOCK,
        ATTR_TTS_PROVIDER: TTS_PROVIDER_MOCK,
        ATTR_EVENT_MESSAGE: "This is a test without volume",
        ATTR_TTS_EVENT_LANGUAGE: "en"
    }
    data_out = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test without volume",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent(expected_count=1)
    test_context.verify_plugin_data_content(data_out, data_index=0)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_volume_test"])
async def test_media_player_plugin_api_speek_with_volume(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_EVENT_MESSAGE: "This is a test with volume",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_VOLUME: 0.1,
    }
    data_out_volume = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_MEDIA_VOLUME_LEVEL: 0.1
    }
    data_out_speek = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test with volume",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }
    
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_content(data_out_volume, data_index=0)
    test_context.verify_plugin_data_content(data_out_speek, data_index=1)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_announce_test"])
async def test_media_player_plugin_api_speek_with_announce_unsupported(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_EVENT_MESSAGE: "This is a test with announce",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_MEDIA_ANNOUNCE: True,
    }
    data_out_suspend = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MODE: "suspend"
    }
    data_out_speek = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_EVENT_MESSAGE: "This is a test with announce",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }
    data_out_resume = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MODE: "resume"
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent(expected_count=3)
    test_context.verify_plugin_data_content(data_out_suspend, data_index=0)
    test_context.verify_plugin_data_content(data_out_speek, data_index=1)
    test_context.verify_plugin_data_content(data_out_resume, data_index=2)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_announce_test"])
async def test_media_player_plugin_api_speek_with_announce_supported(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        setup_mock_tts_provider=True,
        support_announce=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_EVENT_MESSAGE: "This is a test with announce",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_MEDIA_ANNOUNCE: True,
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_EVENT_MESSAGE: "This is a test with announce",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_wait_test"])
async def test_media_player_plugin_api_speek_with_wait(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_provider=MEDIA_PLAYER_PROVIDER_MOCK,
        tts_provider=TTS_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react([mock_plugin])

    data_in = {
        ATTR_EVENT_MESSAGE: "This is a test with wait",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_WAIT: 3,
    }   
    data_out_speek = {
        ATTR_ENTITY_ID: "media_player.browser",
        ATTR_EVENT_MESSAGE: "This is a test with wait",
        ATTR_TTS_EVENT_LANGUAGE: "en",
        ATTR_CACHE: None,
        ATTR_TTS_EVENT_OPTIONS: None
    }
    data_out_wait = {
        ATTR_WAIT: 3,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent(expected_count=2)
    test_context.verify_plugin_data_content(data_out_speek, data_index=0)
    test_context.verify_plugin_data_content(data_out_wait, data_index=1)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_state_test"])
async def test_media_player_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "media_player_state_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    mp = await test_context.async_start_media_player()
    await test_context.async_start_react([mock_plugin])

    async with test_context.async_listen_action_event():
        await mp.async_play_media(entity_id, "content_id", "content_type")
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=2)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=MEDIA_PLAYER_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_index=0)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=MEDIA_PLAYER_DOMAIN,
            expected_action=str(MediaPlayerState.PLAYING),
            event_index=1)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()
