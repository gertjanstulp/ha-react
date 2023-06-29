import pytest

from homeassistant.const import ATTR_DEVICE_ID

from custom_components.react.const import (
    ATTR_EVENT,
    ATTR_PLUGIN_MODULE,
    CONF_ENTITY_MAPS,
    REACT_ACTION_DOUBLE_PRESS,
    REACT_ACTION_LONG_PRESS,
    REACT_ACTION_SHORT_PRESS,
    REACT_TYPE_BUTTON,
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.deconz.const import (
    DECONZ_CODE_DOUBLE_PRESS,
    DECONZ_CODE_LONG_PRESS,
    DECONZ_CODE_SHORT_PRESS, 
    EVENT_DECONZ_EVENT,
)

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext) -> dict:
    test_context.hass.data[TEST_CONFIG] = {}


def get_mock_plugin(
    entity_map: dict = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.deconz_mock",
        ATTR_CONFIG: {} 
    }
    if entity_map:
        result[ATTR_CONFIG][CONF_ENTITY_MAPS] = entity_map
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_deconz_task_short_press_input_block(test_context: TstContext):
    DEVICE_ID = "device_id"
    MAPPED_DEVICE_ID = f"mapped_{DEVICE_ID}"
    
    mock_plugins = get_mock_plugin(
        entity_map={
            DEVICE_ID: MAPPED_DEVICE_ID
        }
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugins)

    data_in = {
        ATTR_EVENT: DECONZ_CODE_SHORT_PRESS,
        ATTR_DEVICE_ID: DEVICE_ID,
        "test_attr": "test_value",
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_DECONZ_EVENT, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=MAPPED_DEVICE_ID, 
            expected_type=REACT_TYPE_BUTTON,
            expected_action=REACT_ACTION_SHORT_PRESS)
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_deconz_task_long_press_input_block(test_context: TstContext):
    DEVICE_ID = "device_id"
    MAPPED_DEVICE_ID = f"mapped_{DEVICE_ID}"
    
    mock_plugins = get_mock_plugin(
        entity_map={
            DEVICE_ID: MAPPED_DEVICE_ID
        }
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugins)

    data_in = {
        ATTR_EVENT: DECONZ_CODE_LONG_PRESS,
        ATTR_DEVICE_ID: DEVICE_ID,
        "test_attr": "test_value",
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_DECONZ_EVENT, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=MAPPED_DEVICE_ID, 
            expected_type=REACT_TYPE_BUTTON,
            expected_action=REACT_ACTION_LONG_PRESS)
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_deconz_task_double_press_input_block(test_context: TstContext):
    DEVICE_ID = "device_id"
    MAPPED_DEVICE_ID = f"mapped_{DEVICE_ID}"
    
    mock_plugins = get_mock_plugin(
        entity_map={
            DEVICE_ID: MAPPED_DEVICE_ID
        }
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugins)

    data_in = {
        ATTR_EVENT: DECONZ_CODE_DOUBLE_PRESS,
        ATTR_DEVICE_ID: DEVICE_ID,
        "test_attr": "test_value",
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_DECONZ_EVENT, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=MAPPED_DEVICE_ID, 
            expected_type=REACT_TYPE_BUTTON,
            expected_action=REACT_ACTION_DOUBLE_PRESS)
        test_context.verify_has_no_log_issues()
