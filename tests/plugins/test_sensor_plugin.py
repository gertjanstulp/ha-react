import pytest

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN

from custom_components.react.const import ACTION_CHANGE, ATTR_PLUGIN_MODULE
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
        ATTR_PLUGIN_MODULE: "tests._plugins.sensor_mock",
        ATTR_CONFIG: {} 
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["sensor_state_test"])
async def test_sensor_plugin_input_block_state_change(test_context: TstContext):
    entity_id = "sensor_state_test"
    mock_plugin = get_mock_plugin()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_sensor()
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await vc.async_set(SENSOR_DOMAIN, entity_id, 10)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=1)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=SENSOR_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_index=0)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()