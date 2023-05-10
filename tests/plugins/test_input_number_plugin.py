from typing import Any
import pytest

from homeassistant.components.input_number import (
    ATTR_VALUE,
    DOMAIN,
    SERVICE_SET_VALUE,
    ATTR_MIN,
    ATTR_MAX,
)
from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.const import (
    ACTION_CHANGE,
    ATTR_PLUGIN_MODULE,
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.input_number.const import ATTR_INPUT_NUMBER_PROVIDER

from tests._plugins.input_number_mock.setup import INPUT_NUMBER_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

FIXTURE_EXPECTED_VALUE = "expected_value"
FIXTURE_VALUE = "value"
FIXTURE_MIN = "min"
FIXTURE_MAX = "max"
FIXTURE_ENTITY_ID = "entity_id"


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    input_number_entity_id: str = None,
    input_number_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if input_number_entity_id:
        result[ATTR_ENTITY_ID] = input_number_entity_id
    if input_number_entity_state != None:
        result[ATTR_ENTITY_STATE] = input_number_entity_state


def get_mock_plugin(
    input_number_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.input_number_mock",
        ATTR_CONFIG: {} 
    }
    if input_number_provider:
        result[ATTR_CONFIG][ATTR_INPUT_NUMBER_PROVIDER] = input_number_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [
    "input_number_set_test",
    "input_number_increase_test",
    "input_number_decrease_test",
])
async def test_input_number_plugin_api_set_invalid_entity(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react([mock_plugin])
        
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_record("WARNING", f"Input number plugin: Api - input_number.input_number_value_test not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [
    "input_number_set_test",
    "input_number_increase_test",
    "input_number_decrease_test",
])
async def test_input_number_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str):
    entity_id = "input_number.input_number_value_test"
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        input_number_entity_id=entity_id,
        input_number_entity_state=50
    )
    
    data = {
        ATTR_INPUT_NUMBER_PROVIDER: invalid_provider,
        ATTR_VALUE: 1
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"Input number plugin: Api - Input number provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_EXPECTED_VALUE},{FIXTURE_VALUE},{FIXTURE_MIN},{FIXTURE_MAX}", [
    ("input_number_set_test", 12.34, 12.34, None, None),
    ("input_number_increase_test", 51.5,  1.5, None,None), 
    ("input_number_increase_with_max_test", 51,  1.5, None, 51),
    ("input_number_decrease_test", 48.5, 1.5, None, None),
    ("input_number_decrease_with_min_test", 49, 1.5, 49, None),
])
async def test_input_number_plugin_api_set_value_config_provider(test_context: TstContext, workflow_name: str, expected_value: Any, value: float, min: float, max: float):
    entity_id = "input_number.input_number_value_test"
    mock_plugin = get_mock_plugin(
        input_number_provider=INPUT_NUMBER_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        input_number_entity_id=entity_id,
        input_number_entity_state=50
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_VALUE: value
    }
    if min:
        data_in[ATTR_MIN] = min
    if max:
        data_in[ATTR_MAX] = max
    
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_VALUE: expected_value,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_EXPECTED_VALUE},{FIXTURE_VALUE},{FIXTURE_MIN},{FIXTURE_MAX}", [
    ("input_number_set_test", 12.34, 12.34, None, None),
    ("input_number_increase_test", 51.5,  1.5, None,None), 
    ("input_number_increase_with_max_test", 51,  1.5, None, 51),
    ("input_number_decrease_test", 48.5, 1.5, None, None),
    ("input_number_decrease_with_min_test", 49, 1.5, 49, None),
])
async def test_input_number_plugin_api_set_value_event_provider(test_context: TstContext, workflow_name: str, expected_value: Any, value: float, min: float, max: float):
    entity_id = "input_number.input_number_value_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        input_number_entity_id=entity_id,
        input_number_entity_state=50
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_VALUE: value,
        ATTR_INPUT_NUMBER_PROVIDER: INPUT_NUMBER_MOCK_PROVIDER,
    }
    if min:
        data_in[ATTR_MIN] = min
    if max:
        data_in[ATTR_MAX] = max
    
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_VALUE: expected_value,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_state_test"])
async def test_input_number_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "input_number_state_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    inc = await test_context.async_start_input_number()
    await test_context.async_start_react([mock_plugin])

    async with test_context.async_listen_action_event():
        await inc.async_set_value(entity_id, 123.45)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=1)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=DOMAIN,
            expected_action=ACTION_CHANGE,
            event_index=0)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_set_test"])
async def test_input_number_plugin_generic_provider_set(test_context: TstContext, workflow_name: str):
    entity_id = "input_number.input_number_value_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        input_number_entity_id=entity_id,
        input_number_entity_state=50
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_VALUE: 12.34
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_VALUE: 12.34,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(DOMAIN, SERVICE_SET_VALUE, data_out)
