import pytest

from homeassistant.components.input_button import DOMAIN as BUTTON_DOMAIN

from custom_components.react.const import (
    ACTION_CHANGE,
    ACTION_PRESS,
    ATTR_PLUGIN_MODULE,
)
from custom_components.react.plugin.const import ATTR_CONFIG

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
)
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}


def get_mock_plugin(
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.input_button_mock",
        ATTR_CONFIG: {} 
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_button_state_test"])
async def test_input_button_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "input_button_state_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    ibc = await test_context.async_start_input_button()
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await ibc.async_press(entity_id)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=2)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BUTTON_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BUTTON_DOMAIN,
            expected_action=ACTION_PRESS,
            event_with_action_name=ACTION_PRESS)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()
