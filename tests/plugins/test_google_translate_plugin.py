import pytest

from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_ANNOUNCE,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    MediaType,
    SERVICE_PLAY_MEDIA
)
from homeassistant.components.tts import (
    ATTR_LANGUAGE,
    ATTR_OPTIONS,
)
from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.const import ATTR_PLUGIN_MODULE
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.google_translate.const import (
    ATTR_TTS_TLD,
    TTS_GOOGLE_TRANSLATE_PROVIDER,
)
from custom_components.react.plugin.media_player.const import (
    ATTR_MEDIA_PLAYER_PROVIDER, 
    ATTR_TTS_PROVIDER, 
    TTS_DEFAULT_LANGUAGE,
)

from tests._plugins.media_player_mock.const import (
    ATTR_SETUP_MOCK_MEDIA_PLAYER_PROVIDER, 
    MEDIA_PLAYER_PROVIDER_MOCK,
)
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_MESSAGE, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_media_player_provider: bool = False,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_MEDIA_PLAYER_PROVIDER: setup_mock_media_player_provider
    }
    if media_player_entity_id:
        result[ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_ENTITY_STATE] = media_player_entity_state


def get_mock_plugins(
    google_translate_config: dict = {},
):
    result = [
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.google_translate_mock", 
            ATTR_CONFIG: google_translate_config
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.media_player_mock", 
            ATTR_CONFIG: { 
                ATTR_MEDIA_PLAYER_PROVIDER: MEDIA_PLAYER_PROVIDER_MOCK,
                ATTR_TTS_PROVIDER: TTS_GOOGLE_TRANSLATE_PROVIDER,
            }
        },
    ]
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_google_translate_plugin_provider_speek_event_language(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    language = "nl"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugins)
    
    data_in = {
        ATTR_MESSAGE: "This is a test without volume",
        ATTR_LANGUAGE: language
    }

    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_ID: f"This is a test without volume|{TTS_GOOGLE_TRANSLATE_PROVIDER}|{language}",
        ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
        ATTR_MEDIA_ANNOUNCE: True,
    }
    
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_google_translate_plugin_provider_speek_config_language(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    language = "be"
    mock_plugins = get_mock_plugins(
        google_translate_config={ATTR_LANGUAGE: language}
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugins)
    
    data_in = {
        ATTR_MESSAGE: "This is a test without volume",
    }

    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_ID: f"This is a test without volume|{TTS_GOOGLE_TRANSLATE_PROVIDER}|{language}",
        ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
        ATTR_MEDIA_ANNOUNCE: True,
    }
    
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_google_translate_plugin_provider_speek_default_language(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugins)
    
    data_in = {
        ATTR_MESSAGE: "This is a test without volume",
    }

    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_ID: f"This is a test without volume|{TTS_GOOGLE_TRANSLATE_PROVIDER}|{TTS_DEFAULT_LANGUAGE}",
        ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
        ATTR_MEDIA_ANNOUNCE: True,
    }
    
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_google_translate_plugin_provider_speek_event_options(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    tld = "co.uk"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugins)
    
    data_in = {
        ATTR_MESSAGE: "This is a test without volume",
        ATTR_OPTIONS: {ATTR_TTS_TLD: tld},
    }

    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_ID: f"This is a test without volume|{TTS_GOOGLE_TRANSLATE_PROVIDER}|{TTS_DEFAULT_LANGUAGE}|{str({ATTR_TTS_TLD: tld})}",
        ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
        ATTR_MEDIA_ANNOUNCE: True,
    }
    
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_google_translate_plugin_provider_speek_config_options(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    tld = "co.uk"
    mock_plugins = get_mock_plugins(
        google_translate_config={ATTR_OPTIONS: {ATTR_TTS_TLD: tld}}
    )
    set_test_config(test_context,
        setup_mock_media_player_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugins)
    
    data_in = {
        ATTR_MESSAGE: "This is a test without volume",
    }

    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_ID: f"This is a test without volume|{TTS_GOOGLE_TRANSLATE_PROVIDER}|{TTS_DEFAULT_LANGUAGE}|{str({ATTR_TTS_TLD: tld})}",
        ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
        ATTR_MEDIA_ANNOUNCE: True,
    }
    
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data_out)
