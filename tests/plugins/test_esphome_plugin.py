import pytest

from homeassistant.const import ATTR_DEVICE_ID

from custom_components.react.const import (
    ATTR_PLUGIN_MODULE,
    REACT_TYPE_BUTTON,
    REACT_TYPE_LIGHT,
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.esphome.const import (
    ATTR_ENTITY_PROPERTY,
    ATTR_TYPE_MAPS,
    EVENT_ESPHOME_EVENT,
)

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext) -> dict:
    test_context.hass.data[TEST_CONFIG] = {}


def get_mock_plugin(
    entity_property: str = None,
    type_maps: list[dict] = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.esphome_mock",
        ATTR_CONFIG: {} 
    }
    if entity_property:
        result[ATTR_CONFIG][ATTR_ENTITY_PROPERTY] = entity_property
    if type_maps:
        result[ATTR_CONFIG][ATTR_TYPE_MAPS] = type_maps
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_esphome_task_event_input_block_common_map(test_context: TstContext):
    test_entity_property = ATTR_DEVICE_ID
    test_event_name1 = "test_event1"
    test_event_name2 = "test_event2"
    test_react_action = "test_action"
    mock_plugins = get_mock_plugin(
        entity_property=test_entity_property,
        type_maps={
            REACT_TYPE_BUTTON: {
                test_event_name1: test_react_action,
            },
            REACT_TYPE_LIGHT: {
                test_event_name2: test_react_action,
            }
        }
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugins)

    test_device_id = "test_device_id"

    data_in = {
        ATTR_DEVICE_ID: test_device_id,
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(f"{EVENT_ESPHOME_EVENT}{test_event_name1}", data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=test_device_id, 
            expected_type=REACT_TYPE_BUTTON,
            expected_action=test_react_action)
        test_context.verify_has_no_log_issues()
