import pytest

from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_EVENT_MESSAGE, ATTR_PLUGIN_MODULE, DOMAIN

from custom_components.react.plugin.tts.const import ATTR_EVENT_LANGUAGE, ATTR_EVENT_OPTIONS

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
    
    plugin_data = {
        ATTR_ENTITY_ID: "browser",
        ATTR_EVENT_MESSAGE: "This is a test",
        ATTR_EVENT_LANGUAGE: "nl",
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
        
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(plugin_data)