from typing import Any
import pytest

from homeassistant.components.input_text import (
    DOMAIN,
    SERVICE_SET_VALUE,
    ATTR_VALUE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
)

from custom_components.react.const import (
    ACTION_CHANGE,
    ATTR_PLUGIN_MODULE,
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.input_text.const import ATTR_INPUT_TEXT_PROVIDER

from tests._plugins.input_text_mock.setup import INPUT_TEXT_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    entity_id: str = None,
    entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if entity_id:
        result[ATTR_ENTITY_ID] = entity_id
    if entity_state != None:
        result[ATTR_ENTITY_STATE] = entity_state


def get_mock_plugin(
    input_text_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.input_text_mock",
        ATTR_CONFIG: {} 
    }
    if input_text_provider:
        result[ATTR_CONFIG][ATTR_INPUT_TEXT_PROVIDER] = input_text_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_text_plugin_api_set_invalid_entity(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    data_in = {
        ATTR_VALUE: "test_value"
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - input_text.input_text_value_test not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_text_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str):
    entity_id = "input_text.input_text_value_test"
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        entity_id=entity_id,
        entity_state="Test"
    )
    
    data = {
        ATTR_INPUT_TEXT_PROVIDER: invalid_provider,
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Input_text provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_text_plugin_api_set_config_provider(test_context: TstContext, workflow_name: str):
    entity_id = "input_text.input_text_value_test"
    mock_plugin = get_mock_plugin(
        input_text_provider=INPUT_TEXT_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        entity_id=entity_id,
        entity_state=50
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_VALUE: "test_value"
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_VALUE: "test_value",
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_text_plugin_api_set_event_provider(test_context: TstContext, workflow_name: str):
    entity_id = "input_text.input_text_value_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        entity_id=entity_id,
        entity_state=50
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_VALUE: "test_value",
        ATTR_INPUT_TEXT_PROVIDER: INPUT_TEXT_MOCK_PROVIDER
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_VALUE: "test_value",
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_state_test"])
async def test_input_text_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "input_text_state_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    inc = await test_context.async_start_input_text()
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await inc.async_set_value(entity_id, "test_value")
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=1)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=DOMAIN,
            expected_action=ACTION_CHANGE,
            event_index=0)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_text_plugin_generic_provider_set(test_context: TstContext, workflow_name: str):
    entity_id = "input_text.input_text_value_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        entity_id=entity_id,
        entity_state=""
    )

    await test_context.async_start_react([mock_plugin])

    data_in = {
        ATTR_VALUE: "test_value"
    }  
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_VALUE: "test_value",
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(DOMAIN, SERVICE_SET_VALUE, data_out)
