from typing import Any, Mapping
import pytest

from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    ATTR_PERCENTAGE_STEP,
    DOMAIN as FAN_DOMAIN,
    SERVICE_SET_PERCENTAGE,
    SERVICE_INCREASE_SPEED,
    SERVICE_DECREASE_SPEED,
) 
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
)

from custom_components.react.const import (
    ACTION_CHANGE,
    ACTION_DECREASE,
    ACTION_INCREASE,
    ACTION_TOGGLE,
    ATTR_PLUGIN_MODULE,
    ATTR_STATE, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.fan.const import ATTR_FAN_PROVIDER

from tests._plugins.fan_mock.setup import FAN_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_ENTITY_STATE_ATTRIBUTES, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

FIXTURE_FAN_NAME = "fan_name"
FIXTURE_VALUE_BEFORE = "value_before"
FIXTURE_VALUE_AFTER = "value_after"
FIXTURE_PERCENTAGE_BEFORE = "percentage_before"
FIXTURE_PERCENTAGE_AFTER = "percentage_after"
FIXTURE_NAME_INITIAL = "name_initial"
FIXTURE_EXPECTED_SERVICE = "expected_service"
FIXTURE_INITIAL_STATE = "initial_state"
FIXTURE_INITIAL_PERCENTAGE = "initial_percentage"
FIXTURE_ENTITY_ID = "entity_id"
FIXTURE_EXPECTED_ACTIONS = "expected_actions"
FIXTURE_PERCENTAGE = "percentage"
FIXTURE_PERCENTAGE_STEP = "percentage_step"
FIXTURE_CREASE_TYPE = "crease_type"


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    fan_entity_id: str = None,
    fan_entity_state: str = None,
    fan_entity_state_attributes: Mapping[str, Any]= None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if fan_entity_id:
        result[ATTR_ENTITY_ID] = fan_entity_id
    if fan_entity_state != None:
        result[ATTR_ENTITY_STATE] = fan_entity_state
    if fan_entity_state_attributes != None:
        result[ATTR_ENTITY_STATE_ATTRIBUTES] = fan_entity_state_attributes


def get_mock_plugin(
    fan_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.fan_mock",
        ATTR_CONFIG: {} 
    }
    if fan_provider:
        result[ATTR_CONFIG][ATTR_FAN_PROVIDER] = fan_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_set_percentage_test"])
@pytest.mark.parametrize(FIXTURE_PERCENTAGE, [
    None,
    -1,
    101,
])
async def test_fan_plugin_api_set_percentage_invalid_percentage(test_context: TstContext, workflow_name: str, percentage: int):
    entity_id = "fan_initial_off_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    data = {
        ATTR_PERCENTAGE: percentage
    }
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_has_no_log_debug(f"1 - Setting percentage of fan '{entity_id}'")
    test_context.verify_has_log_error(f"1 - No valid percentage provided. Percentage should be a number between 0 and 100")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_PERCENTAGE_STEP},{FIXTURE_CREASE_TYPE}", [
    ("fan_increase_speed_test", -1,"Increasing"),
    ("fan_increase_speed_test", 101,"Increasing"),
    ("fan_decrease_speed_test", -1,"Decreasing"),
    ("fan_decrease_speed_test", 101,"Decreasing"),
])
async def test_fan_plugin_api_crease_invalid_percentage_step(test_context: TstContext, workflow_name: str, percentage_step: int, crease_type: str):
    entity_id = "fan_initial_on_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    data = {
        ATTR_PERCENTAGE_STEP: percentage_step
    }
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_has_no_log_debug(f"1 - {crease_type} speed of fan '{entity_id}'")
    test_context.verify_has_log_error(f"1 - Invalid percentage step provided. Percentage step should be a number between 0 and 100")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_FAN_NAME}", [
    ("fan_set_percentage_test", "initial_off"),
    ("fan_increase_speed_test", "initial_on"),
    ("fan_decrease_speed_test", "initial_on"),
])
async def test_fan_plugin_api_invalid_entity(test_context: TstContext, workflow_name: str, fan_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    data = {
        ATTR_PERCENTAGE: 50
    }
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - fan.fan_{fan_name}_test not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_ENTITY_ID}", [
    ("fan_set_percentage_test", "fan.fan_initial_off_test"),
    ("fan_increase_speed_test", "fan.fan_initial_on_test"),
    ("fan_decrease_speed_test", "fan.fan_initial_on_test"),
])
async def test_fan_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str, entity_id: str):
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        fan_entity_id=entity_id,
        fan_entity_state="test"
    )
    
    data = {
        ATTR_FAN_PROVIDER: invalid_provider,
        ATTR_PERCENTAGE: 50,
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Fan provider for '{invalid_provider}' not found")
    

@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_INITIAL_STATE},{FIXTURE_INITIAL_PERCENTAGE},{FIXTURE_PERCENTAGE}", [
    ("fan_set_percentage_test", STATE_OFF, None, 0),
    ("fan_set_percentage_test", STATE_ON, 50, 50),
])
async def test_fan_plugin_api_skip_set_percentage(test_context: TstContext, workflow_name: str, initial_state: str, initial_percentage: int, percentage: int):
    entity_id = f"fan.fan_initial_off_test"
    mock_plugin = get_mock_plugin(
        fan_provider=FAN_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=initial_state,
        fan_entity_state_attributes={
            ATTR_PERCENTAGE: initial_percentage
        }
    )
    data = {
        ATTR_PERCENTAGE: percentage
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_increase_speed_test"])
async def test_fan_plugin_api_skip_increase_speed(test_context: TstContext, workflow_name: str):
    entity_id = f"fan.fan_initial_on_test"
    mock_plugin = get_mock_plugin(
        fan_provider=FAN_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=STATE_ON,
        fan_entity_state_attributes={
            ATTR_PERCENTAGE: 100
        }
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_decrease_speed_test"])
async def test_fan_plugin_api_skip_decrease_speed(test_context: TstContext, workflow_name: str):
    entity_id = f"fan.fan_initial_on_test"
    mock_plugin = get_mock_plugin(
        fan_provider=FAN_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=STATE_OFF,
        fan_entity_state_attributes={
            ATTR_PERCENTAGE: 0
        }
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_set_percentage_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_AFTER}", [
    (STATE_OFF, 0, 50),
    (STATE_ON, 10, 50),
    (STATE_ON, 100, 50),
])
async def test_fan_plugin_api_set_percentage_config_provider(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_after: int):    
    entity_id = f"fan.fan_initial_off_test"
    mock_plugin = get_mock_plugin(
        fan_provider=FAN_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before},
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE: percentage_after
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_PERCENTAGE: percentage_after
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_set_percentage_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_AFTER}", [
    (STATE_OFF, 0, 50),
    (STATE_ON, 10, 50),
    (STATE_ON, 100, 50),
])
async def test_fan_plugin_api_set_percentage_event_provider(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_after: int):    
    entity_id = f"fan.fan_initial_off_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before},
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE: percentage_after,
        ATTR_FAN_PROVIDER: FAN_MOCK_PROVIDER,
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_PERCENTAGE: percentage_after
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_increase_speed_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_STEP}", [
    (STATE_OFF, 0, None),
    (STATE_ON, 10, None),
    (STATE_ON, 90, None),
    (STATE_OFF, 0, 20),
    (STATE_ON, 10, 20),
    (STATE_ON, 90, 20),
])
async def test_fan_plugin_api_increase_speed_config_provider(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_step: int):    
    entity_id = f"fan.fan_initial_on_test"
    mock_plugin = get_mock_plugin(
        fan_provider=FAN_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before},
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE_STEP: percentage_step
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_PERCENTAGE_STEP: percentage_step
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_increase_speed_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_STEP}", [
    (STATE_OFF, 0, None),
    (STATE_ON, 10, None),
    (STATE_ON, 90, None),
    (STATE_OFF, 0, 20),
    (STATE_ON, 10, 20),
    (STATE_ON, 90, 20),
])
async def test_fan_plugin_api_increase_speed_event_provider(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_step: int):    
    entity_id = f"fan.fan_initial_on_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before},
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE_STEP: percentage_step,
        ATTR_FAN_PROVIDER: FAN_MOCK_PROVIDER,
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_PERCENTAGE_STEP: percentage_step
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_decrease_speed_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_STEP}", [
    (STATE_ON, 100, None),
    (STATE_ON, 50, None),
    (STATE_ON, 10, None),
    (STATE_ON, 100, 20),
    (STATE_ON, 50, 20),
    (STATE_ON, 10, 20),
])
async def test_fan_plugin_api_decrease_speed_config_provider(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_step: int):    
    entity_id = f"fan.fan_initial_on_test"
    mock_plugin = get_mock_plugin(
        fan_provider=FAN_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before},
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE_STEP: percentage_step
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_PERCENTAGE_STEP: percentage_step
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_decrease_speed_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_STEP}", [
    (STATE_ON, 100, None),
    (STATE_ON, 50, None),
    (STATE_ON, 10, None),
])
async def test_fan_plugin_api_decrease_speed_event_provider(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_step: int):    
    entity_id = f"fan.fan_initial_on_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before},
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE_STEP: percentage_step,
        ATTR_FAN_PROVIDER: FAN_MOCK_PROVIDER,
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_PERCENTAGE_STEP: percentage_step
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_set_percentage_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_AFTER}", [
    (STATE_OFF, 0, 50),
    (STATE_ON, 10, 50),
    (STATE_ON, 100, 50),
])
async def test_fan_plugin_generic_provider_set_percentage(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_after: int):    
    entity_id = f"fan.fan_initial_off_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before}
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE: percentage_after
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_PERCENTAGE: percentage_after,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(FAN_DOMAIN, SERVICE_SET_PERCENTAGE, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_increase_speed_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_STEP}", [
    (STATE_OFF, 0, None),
    (STATE_ON, 10, None),
    (STATE_ON, 90, None),
    (STATE_OFF, 0, 20),
    (STATE_ON, 10, 20),
    (STATE_ON, 90, 20),
])
async def test_fan_plugin_generic_provider_increase_speed(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_step: int):    
    entity_id = f"fan.fan_initial_on_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before},
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE_STEP: percentage_step
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
    }
    if percentage_step:
        data_out[ATTR_PERCENTAGE_STEP] = percentage_step

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(FAN_DOMAIN, SERVICE_INCREASE_SPEED, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["fan_decrease_speed_test"])
@pytest.mark.parametrize(f"{FIXTURE_VALUE_BEFORE},{FIXTURE_PERCENTAGE_BEFORE},{FIXTURE_PERCENTAGE_STEP}", [
    (STATE_ON, 100, None),
    (STATE_ON, 50, None),
    (STATE_ON, 10, None),
    (STATE_ON, 100, 20),
    (STATE_ON, 50, 20),
    (STATE_ON, 10, 20),
])
async def test_fan_plugin_generic_provider_decrease_speed(test_context: TstContext, workflow_name: str, value_before: str, percentage_before: int, percentage_step: int):    
    entity_id = f"fan.fan_initial_on_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        fan_entity_id=entity_id,
        fan_entity_state=value_before,
        fan_entity_state_attributes={ATTR_PERCENTAGE: percentage_before},
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_PERCENTAGE_STEP: percentage_step
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
    }
    if percentage_step:
        data_out[ATTR_PERCENTAGE_STEP] = percentage_step

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(FAN_DOMAIN, SERVICE_DECREASE_SPEED, data_out)
    

@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_ENTITY_ID},{FIXTURE_PERCENTAGE},{FIXTURE_EXPECTED_ACTIONS}", [
    ("fan_state_percentage_test", "fan_state_percentage_test", 25, [ACTION_CHANGE,ACTION_DECREASE]),
    ("fan_state_percentage_test", "fan_state_percentage_test", 75, [ACTION_CHANGE,ACTION_INCREASE]),
    ("fan_state_test", "fan_state_test", 50, [ACTION_CHANGE,STATE_ON,ACTION_TOGGLE])
])
async def test_fan_plugin_input_block_state_change(test_context: TstContext, entity_id: str, percentage: int, expected_actions: list[str]):
    mock_plugin = get_mock_plugin()
    await test_context.async_start_virtual()
    f = await test_context.async_start_fan()
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await f.async_set_percentage(entity_id, percentage)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=len(expected_actions))
        for i,expected_action in enumerate(expected_actions):
            test_context.verify_action_event_data(
                expected_entity=entity_id,
                expected_type=FAN_DOMAIN,
                expected_action=expected_action,
                event_with_action_name=expected_action)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()
