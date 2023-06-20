from typing import Any, Mapping
import pytest

from homeassistant.components.climate import (
    DOMAIN as CLIMATE_DOMAIN,
    SERVICE_SET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    STATE_OFF,
)

from custom_components.react.const import (
    ATTR_EVENT_MESSAGE, 
    ATTR_PLUGIN_MODULE, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.climate.const import (
    ATTR_CLIMATE_PROVIDER, 
)
from tests._plugins.climate_mock.const import (
    ATTR_SETUP_MOCK_CLIMATE_PROVIDER,
    CLIMATE_PROVIDER_MOCK, 
)

from tests.common import (
    FIXTURE_WORKFLOW_NAME,
    VALUE_FIXTURE_COMBOS,
    VALUE_FIXTURES, 
)
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_ENTITY_STATE_ATTRIBUTES,
    TEST_CONFIG
)
from tests.tst_context import TstContext

FIXTURE_FAKE_CLIMATE_PROVIDER = "fake_climate_provider"


def set_test_config(test_context: TstContext,
    setup_mock_climate_provider: bool = False,
    climate_entity_id: str = None,
    climate_entity_state: str = None,
    climate_entity_state_attributes: Mapping[str, Any]= None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_CLIMATE_PROVIDER: setup_mock_climate_provider,
    }
    if climate_entity_id:
        result[ATTR_ENTITY_ID] = climate_entity_id
    if climate_entity_state != None:
        result[ATTR_ENTITY_STATE] = climate_entity_state
    if climate_entity_state_attributes != None:
        result[ATTR_ENTITY_STATE_ATTRIBUTES] = climate_entity_state_attributes


def get_mock_plugin(
    climate_provider: str = None,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.climate_mock", 
        ATTR_CONFIG : {}
    }
    if climate_provider:
        result[ATTR_CONFIG][ATTR_CLIMATE_PROVIDER] = climate_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [
    "climate_set_temperature_test",
    "climate_reset_temperature_test"
])
async def test_climate_plugin_api_entity_not_found(test_context: TstContext, workflow_name: str):
    entity_id = "climate.climate_initial_off_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    data_in = {
        ATTR_TEMPERATURE: 25,
    }
    
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - {entity_id} not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["climate_set_temperature_test"])
async def test_climate_plugin_api_no_climate_provider_set_up(test_context: TstContext, workflow_name: str):
    entity_id = "climate.climate_initial_off_test"
    mock_plugin = get_mock_plugin(
        climate_provider=CLIMATE_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_climate_provider=False,
        climate_entity_id=entity_id,
        climate_entity_state="off"
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Climate provider for {entity_id}/{CLIMATE_PROVIDER_MOCK} not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["climate_reset_temperature_test"])
async def test_climate_plugin_api_no_climate_provider_provided(test_context: TstContext, workflow_name: str):
    entity_id = "climate.climate_initial_off_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_climate_provider=True,
        climate_entity_id=entity_id,
        climate_entity_state="off"
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Climate provider for {entity_id} not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [
    "climate_set_temperature_test",
    "climate_reset_temperature_test"
])
async def test_climate_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str):
    entity_id = "climate.climate_initial_off_test"
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        climate_entity_id=entity_id,
        climate_entity_state=STATE_OFF
    )
    
    data = {
        ATTR_CLIMATE_PROVIDER: invalid_provider
    }
    
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Climate provider for {entity_id}/{invalid_provider} not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["climate_set_temperature_test"])
@pytest.mark.parametrize(VALUE_FIXTURES, VALUE_FIXTURE_COMBOS)
async def test_climate_plugin_api_set_temperature(test_context: TstContext, workflow_name: str, config_value: bool, event_value: bool):
    entity_id = "climate.climate_initial_off_test"
    mock_plugin = get_mock_plugin(
        climate_provider=CLIMATE_PROVIDER_MOCK if config_value else None
    )
    set_test_config(test_context,
        setup_mock_climate_provider=True,
        climate_entity_id=entity_id,
        climate_entity_state="off",
    )
   
    await test_context.async_start_react([mock_plugin])
    
    temperature = 25
    data_in = {
        ATTR_CLIMATE_PROVIDER: CLIMATE_PROVIDER_MOCK if event_value else None,
        ATTR_TEMPERATURE: temperature
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_TEMPERATURE: temperature
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["climate_reset_temperature_test"])
@pytest.mark.parametrize(VALUE_FIXTURES, VALUE_FIXTURE_COMBOS)
async def test_climate_plugin_api_reset_temperature(test_context: TstContext, workflow_name: str, config_value: bool, event_value: bool):
    entity_id = "climate.climate_initial_off_test"
    mock_plugin = get_mock_plugin(
        climate_provider=CLIMATE_PROVIDER_MOCK if config_value else None
    )
    set_test_config(test_context,
        setup_mock_climate_provider=True,
        climate_entity_id=entity_id,
        climate_entity_state="off",
    )
   
    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_CLIMATE_PROVIDER: CLIMATE_PROVIDER_MOCK if event_value else None,
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["climate_set_temperature_test"])
@pytest.mark.parametrize(VALUE_FIXTURES, VALUE_FIXTURE_COMBOS)
async def test_climate_plugin_api_skip(test_context: TstContext, workflow_name: str, config_value: bool, event_value: bool):
    entity_id = "climate.climate_initial_off_test"
    temperature = 25
    mock_plugin = get_mock_plugin(
        climate_provider=CLIMATE_PROVIDER_MOCK if config_value else None
    )
    set_test_config(test_context,
        setup_mock_climate_provider=True,
        climate_entity_id=entity_id,
        climate_entity_state="off",
        climate_entity_state_attributes={
            ATTR_TEMPERATURE: temperature
        }
    )

    data_in = {
        ATTR_CLIMATE_PROVIDER: CLIMATE_PROVIDER_MOCK if event_value else None,
        ATTR_TEMPERATURE: temperature
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["climate_set_temperature_test"])
async def test_climate_plugin_provider_set_temperature(test_context: TstContext, workflow_name: str):
    entity_id = "climate.climate_initial_off_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        climate_entity_id = entity_id,
        climate_entity_state = STATE_OFF,
    )

    await test_context.async_start_react([mock_plugin])
        
    temperature = 25
    data_in = {
        ATTR_TEMPERATURE: temperature
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_TEMPERATURE: temperature,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(CLIMATE_DOMAIN, SERVICE_SET_TEMPERATURE, data_out)


# @pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["climate_state_test"])
# async def test_climate_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
#     entity_id = "climate_state_test"
#     mock_plugin = get_mock_plugin()
#     set_test_config(test_context)
#     mp = await test_context.async_start_climate()
#     await test_context.async_start_react([mock_plugin])

#     async with test_context.async_listen_action_event():
#         await mp.async_play_media(entity_id, "content_id", "content_type")
#         await test_context.hass.async_block_till_done()
#         await test_context.async_verify_action_event_received(expected_count=2)
#         test_context.verify_action_event_data(
#             expected_entity=entity_id,
#             expected_type=CLIMATE_DOMAIN,
#             expected_action=ACTION_CHANGE,
#             event_index=0)
#         test_context.verify_action_event_data(
#             expected_entity=entity_id,
#             expected_type=CLIMATE_DOMAIN,
#             expected_action=str(MediaPlayerState.PLAYING),
#             event_index=1)
#         test_context.verify_has_no_log_issues()
#     await test_context.hass.async_block_till_done()
