import pytest

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN 
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    STATE_ON,
    STATE_OFF,
)

from custom_components.react.const import (
    ACTION_CHANGE,
    ACTION_TOGGLE,
    ATTR_PLUGIN_MODULE,
    ATTR_STATE, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.switch.const import ATTR_SWITCH_PROVIDER

from tests._plugins.switch_mock.setup import SWITCH_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

FIXTURE_SWITCH_NAME = "switch_name"
FIXTURE_VALUE_BEFORE = "value_before"
FIXTURE_VALUE_AFTER = "value_after"
FIXTURE_NAME_INITIAL = "name_initial"
FIXTURE_EXPECTED_SERVICE = "expected_service"
FIXTURE_INITIAL_STATE = "initial_state"
FIXTURE_ENTITY_ID = "entity_id"


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    switch_entity_id: str = None,
    switch_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if switch_entity_id:
        result[ATTR_ENTITY_ID] = switch_entity_id
    if switch_entity_state != None:
        result[ATTR_ENTITY_STATE] = switch_entity_state


def get_mock_plugin(
    switch_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.switch_mock",
        ATTR_CONFIG: {} 
    }
    if switch_provider:
        result[ATTR_CONFIG][ATTR_SWITCH_PROVIDER] = switch_provider
    return result


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_SWITCH_NAME}", [
    ("switch_turn_on_test", "initial_off"),
    ("switch_turn_off_test", "initial_on"),
    ("switch_toggle_test", "initial_off"),
])
async def test_switch_plugin_api_set_invalid_entity(test_context: TstContext, workflow_name: str, switch_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - switch.switch_{switch_name}_test not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_ENTITY_ID}", [
    ("switch_turn_on_test", "switch.switch_initial_off_test"),
    ("switch_turn_off_test", "switch.switch_initial_on_test"),
    ("switch_toggle_test", "switch.switch_initial_off_test"),
])
async def test_switch_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str, entity_id: str):
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        switch_entity_id=entity_id,
        switch_entity_state="test"
    )
    
    data = {
        ATTR_SWITCH_PROVIDER: invalid_provider
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Switch provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_VALUE_BEFORE},{FIXTURE_VALUE_AFTER},{FIXTURE_NAME_INITIAL}", [
    ("switch_turn_on_test", STATE_OFF, STATE_ON, STATE_OFF),
    ("switch_turn_off_test", STATE_ON, STATE_OFF, STATE_ON),
    ("switch_toggle_test", STATE_OFF, STATE_ON, STATE_OFF),
    ("switch_toggle_test", STATE_ON, STATE_OFF, STATE_OFF),
])
async def test_switch_plugin_api_set_config_provider(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, name_initial: str):    
    entity_id = f"switch.switch_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin(
        switch_provider=SWITCH_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        switch_entity_id=entity_id,
        switch_entity_state=value_before
    )

    await test_context.async_start_react([mock_plugin])
        
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_STATE: value_after,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data)


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_VALUE_BEFORE},{FIXTURE_VALUE_AFTER},{FIXTURE_NAME_INITIAL}", [
    ("switch_turn_on_test", STATE_OFF, STATE_ON, STATE_OFF),
    ("switch_turn_off_test", STATE_ON, STATE_OFF, STATE_ON),
    ("switch_toggle_test", STATE_OFF, STATE_ON, STATE_OFF),
    ("switch_toggle_test", STATE_ON, STATE_OFF, STATE_OFF),
])
async def test_switch_plugin_api_set_event_provider(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, name_initial: str):    
    entity_id = f"switch.switch_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        switch_entity_id=entity_id,
        switch_entity_state=value_before
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_SWITCH_PROVIDER: SWITCH_MOCK_PROVIDER 
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_STATE: value_after,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(F"{FIXTURE_WORKFLOW_NAME},{FIXTURE_VALUE_BEFORE},{FIXTURE_EXPECTED_SERVICE},{FIXTURE_NAME_INITIAL}", [
    ("switch_turn_on_test", STATE_OFF, SERVICE_TURN_ON, STATE_OFF),
    ("switch_turn_off_test", STATE_ON, SERVICE_TURN_OFF, STATE_ON),
])
async def test_switch_plugin_generic_provider_set(test_context: TstContext, workflow_name: str, value_before: str, expected_service: str, name_initial: str):    
    entity_id = f"switch.switch_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        switch_entity_id=entity_id,
        switch_entity_state=value_before
    )

    await test_context.async_start_react([mock_plugin])
        
    data = {
        ATTR_ENTITY_ID: entity_id,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(SWITCH_DOMAIN, expected_service, data)
    

@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_INITIAL_STATE}", [
    ("switch_turn_on_skip_test",STATE_ON),
    ("switch_turn_off_skip_test", STATE_OFF),
])
async def test_switch_plugin_api_skip(test_context: TstContext, workflow_name: str, initial_state: str):
    entity_id = f"switch.switch_initial_{initial_state}_test"
    mock_plugin = get_mock_plugin(
        switch_provider=SWITCH_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        switch_entity_id=entity_id,
        switch_entity_state=initial_state
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_state_test"])
async def test_switch_plugin_input_block_state_change(test_context: TstContext):
    entity_id = "switch_state_test"
    mock_plugin = get_mock_plugin()
    await test_context.async_start_virtual()
    sc = await test_context.async_start_switch()
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await sc.async_turn_on(entity_id)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=SWITCH_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=SWITCH_DOMAIN,
            expected_action=STATE_ON,
            event_with_action_name=STATE_ON)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=SWITCH_DOMAIN,
            expected_action=ACTION_TOGGLE,
            event_with_action_name=ACTION_TOGGLE)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()
