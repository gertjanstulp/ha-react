import pytest

from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN 
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
from custom_components.react.plugin.light.const import ATTR_LIGHT_PROVIDER

from tests._plugins.light_mock.setup import LIGHT_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

FIXTURE_LIGHT_NAME = "light_name"
FIXTURE_VALUE_BEFORE = "value_before"
FIXTURE_VALUE_AFTER = "value_after"
FIXTURE_NAME_INITIAL = "name_initial"
FIXTURE_EXPECTED_SERVICE = "expected_service"
FIXTURE_INITIAL_STATE = "initial_state"
FIXTURE_ENTITY_ID = "entity_id"


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    light_entity_id: str = None,
    light_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if light_entity_id:
        result[ATTR_ENTITY_ID] = light_entity_id
    if light_entity_state != None:
        result[ATTR_ENTITY_STATE] = light_entity_state


def get_mock_plugin(
    light_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.light_mock",
        ATTR_CONFIG: {} 
    }
    if light_provider:
        result[ATTR_CONFIG][ATTR_LIGHT_PROVIDER] = light_provider
    return result


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_LIGHT_NAME}", [
    ("light_turn_on_test", "initial_off"),
    ("light_turn_off_test", "initial_on"),
    ("light_toggle_test", "initial_off"),
])
async def test_light_plugin_api_set_invalid_entity(test_context: TstContext, workflow_name: str, light_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_record("WARNING", f"Light plugin: Api - light.light_{light_name}_test not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_ENTITY_ID}", [
    ("light_turn_on_test", "light.light_initial_off_test"),
    ("light_turn_off_test", "light.light_initial_on_test"),
    ("light_toggle_test", "light.light_initial_off_test"),
])
async def test_light_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str, entity_id: str):
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        light_entity_id=entity_id,
        light_entity_state="test"
    )
    
    data = {
        ATTR_LIGHT_PROVIDER: invalid_provider
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"Light plugin: Api - Light provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_VALUE_BEFORE},{FIXTURE_VALUE_AFTER},{FIXTURE_NAME_INITIAL}", [
    ("light_turn_on_test", STATE_OFF, STATE_ON, STATE_OFF),
    ("light_turn_off_test", STATE_ON, STATE_OFF, STATE_ON),
    ("light_toggle_test", STATE_OFF, STATE_ON, STATE_OFF),
    ("light_toggle_test", STATE_ON, STATE_OFF, STATE_OFF),
])
async def test_light_plugin_api_set_config_provider(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, name_initial: str):    
    entity_id = f"light.light_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin(
        light_provider=LIGHT_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        light_entity_id=entity_id,
        light_entity_state=value_before
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
    ("light_turn_on_test", STATE_OFF, STATE_ON, STATE_OFF),
    ("light_turn_off_test", STATE_ON, STATE_OFF, STATE_ON),
    ("light_toggle_test", STATE_OFF, STATE_ON, STATE_OFF),
    ("light_toggle_test", STATE_ON, STATE_OFF, STATE_OFF),
])
async def test_light_plugin_api_set_event_provider(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, name_initial: str):    
    entity_id = f"light.light_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        light_entity_id=entity_id,
        light_entity_state=value_before
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_LIGHT_PROVIDER: LIGHT_MOCK_PROVIDER 
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
    ("light_turn_on_test", STATE_OFF, SERVICE_TURN_ON, STATE_OFF),
    ("light_turn_off_test", STATE_ON, SERVICE_TURN_OFF, STATE_ON),
])
async def test_light_plugin_generic_provider_set(test_context: TstContext, workflow_name: str, value_before: str, expected_service: str, name_initial: str):    
    entity_id = f"light.light_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        light_entity_id=entity_id,
        light_entity_state=value_before
    )

    await test_context.async_start_react([mock_plugin])
        
    data = {
        ATTR_ENTITY_ID: entity_id,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(LIGHT_DOMAIN, expected_service, data)
    

@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_INITIAL_STATE}", [
    ("light_turn_on_skip_test",STATE_ON),
    ("light_turn_off_skip_test", STATE_OFF),
])
async def test_light_plugin_api_skip(test_context: TstContext, workflow_name: str, initial_state: str):
    entity_id = f"light.light_initial_{initial_state}_test"
    mock_plugin = get_mock_plugin(
        light_provider=LIGHT_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        light_entity_id=entity_id,
        light_entity_state=initial_state
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["light_state_test"])
async def test_light_plugin_input_block_state_change(test_context: TstContext):
    entity_id = "light_state_test"
    mock_plugin = get_mock_plugin()
    await test_context.async_start_virtual()
    lc = await test_context.async_start_light()
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await lc.async_turn_on(entity_id)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=LIGHT_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_index=0)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=LIGHT_DOMAIN,
            expected_action=f"{STATE_ON}",
            event_index=1)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=LIGHT_DOMAIN,
            expected_action=f"{ACTION_TOGGLE}",
            event_index=2)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()
