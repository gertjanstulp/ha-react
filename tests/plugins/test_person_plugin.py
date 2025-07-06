import pytest

from homeassistant.components.person import DOMAIN as PERSON_DOMAIN
from homeassistant.const import STATE_NOT_HOME

from custom_components.react.const import ACTION_CHANGE, ACTION_TOGGLE, ATTR_PLUGIN_MODULE
from custom_components.react.plugin.const import ATTR_CONFIG

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
) -> dict:
    test_context.hass.data[TEST_CONFIG] = {}


def get_mock_plugin(
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.person_mock",
        ATTR_CONFIG: {} 
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person_state_test"])
async def test_person_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "person_state_test"
    mock_plugin = get_mock_plugin()
    await test_context.async_start_virtual()
    dtc = await test_context.async_start_device_tracker()
    await test_context.async_start_person()
    await test_context.async_start_react([mock_plugin])

    async with test_context.async_listen_action_event():
        await dtc.async_see(entity_id, STATE_NOT_HOME)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=PERSON_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=PERSON_DOMAIN,
            expected_action=STATE_NOT_HOME,
            event_with_action_name=STATE_NOT_HOME)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=PERSON_DOMAIN,
            expected_action=ACTION_TOGGLE,
            event_with_action_name=ACTION_TOGGLE)
        test_context.verify_has_no_log_issues()
