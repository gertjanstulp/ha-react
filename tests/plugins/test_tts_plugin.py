import pytest

from homeassistant.core import HomeAssistant
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_VOLUME_LEVEL
)
from homeassistant.const import (
    ATTR_ENTITY_ID
)

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_EVENT_MESSAGE, 
    ATTR_PLUGIN_MODULE, 
    DOMAIN
)

from custom_components.react.plugin.tts.const import (
    ATTR_EVENT_LANGUAGE, 
    ATTR_EVENT_OPTIONS,
    ATTR_INTERRUPT_SERVICE,
    ATTR_RESUME_SERVICE,
)

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["tts_media_player_speek"])
async def test_tts_media_player_speek(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for tts speek
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.tts_plugin_media_player_speek_mock"}
    await react_component.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data_speek = {
        ATTR_ENTITY_ID: "browser",
        ATTR_EVENT_MESSAGE: "This is a test without volume",
        ATTR_EVENT_LANGUAGE: "en",
        ATTR_EVENT_OPTIONS: None

    }

    tc = TstContext(hass, workflow_name)
    react.hass.data["test_context"] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_plugin_data_sent(expected_count=1)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=0)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["tts_media_player_speek_with_volume"])
async def test_tts_media_player_speek_with_volume(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for tts speek
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.tts_plugin_media_player_speek_mock"}
    await react_component.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data_volume = {
        ATTR_ENTITY_ID: "browser",
        ATTR_MEDIA_VOLUME_LEVEL: 0.1
    }
    
    plugin_data_speek = {
        ATTR_ENTITY_ID: "browser",
        ATTR_EVENT_MESSAGE: "This is a test with volume",
        ATTR_EVENT_LANGUAGE: "en",
        ATTR_EVENT_OPTIONS: None

    }

    tc = TstContext(hass, workflow_name)
    react.hass.data["test_context"] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_plugin_data_sent(expected_count=2)
        tc.verify_plugin_data_content(plugin_data_volume, data_index=0)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=1)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["tts_media_player_speek_with_interrupt"])
async def test_tts_media_player_speek_with_interrupt(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for tts speek
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.tts_plugin_media_player_speek_mock"}
    await react_component.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data_interrupt = {
        ATTR_ENTITY_ID: "browser",
        ATTR_INTERRUPT_SERVICE: "sonos.snapshot"
    }
    
    plugin_data_speek = {
        ATTR_ENTITY_ID: "browser",
        ATTR_EVENT_MESSAGE: "This is a test with interrupt service",
        ATTR_EVENT_LANGUAGE: "en",
        ATTR_EVENT_OPTIONS: None

    }

    tc = TstContext(hass, workflow_name)
    react.hass.data["test_context"] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_plugin_data_sent(expected_count=2)
        tc.verify_plugin_data_content(plugin_data_interrupt, data_index=0)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=1)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["tts_media_player_speek_with_resume"])
async def test_tts_media_player_speek_with_resume(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for tts speek
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.tts_plugin_media_player_speek_mock"}
    await react_component.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data_resume = {
        ATTR_ENTITY_ID: "browser",
        ATTR_RESUME_SERVICE: "sonos.restore"
    }
    
    plugin_data_speek = {
        ATTR_ENTITY_ID: "browser",
        ATTR_EVENT_MESSAGE: "This is a test with resume service",
        ATTR_EVENT_LANGUAGE: "en",
        ATTR_EVENT_OPTIONS: None

    }

    tc = TstContext(hass, workflow_name)
    react.hass.data["test_context"] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_plugin_data_sent(expected_count=2)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=0)
        tc.verify_plugin_data_content(plugin_data_resume, data_index=1)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["tts_media_player_speek_with_all"])
async def test_tts_media_player_speek_with_all(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for tts speek
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.tts_plugin_media_player_speek_mock"}
    await react_component.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data_interrupt = {
        ATTR_ENTITY_ID: "browser",
        ATTR_INTERRUPT_SERVICE: "sonos.snapshot"
    }
    
    plugin_data_volume = {
        ATTR_ENTITY_ID: "browser",
        ATTR_MEDIA_VOLUME_LEVEL: 0.1
    }

    plugin_data_resume = {
        ATTR_ENTITY_ID: "browser",
        ATTR_RESUME_SERVICE: "sonos.restore"
    }
    
    plugin_data_speek = {
        ATTR_ENTITY_ID: "browser",
        ATTR_EVENT_MESSAGE: "This is a test with resume service",
        ATTR_EVENT_LANGUAGE: "en",
        ATTR_EVENT_OPTIONS: None

    }

    tc = TstContext(hass, workflow_name)
    react.hass.data["test_context"] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_plugin_data_sent(expected_count=4)
        tc.verify_plugin_data_content(plugin_data_interrupt, data_index=0)
        tc.verify_plugin_data_content(plugin_data_volume, data_index=1)
        tc.verify_plugin_data_content(plugin_data_speek, data_index=2)
        tc.verify_plugin_data_content(plugin_data_resume, data_index=3)