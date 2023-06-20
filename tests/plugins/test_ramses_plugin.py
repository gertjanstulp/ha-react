import pytest

from homeassistant.components.climate import SERVICE_SET_TEMPERATURE
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    Platform,
    STATE_OFF,
)

from custom_components.react.const import ATTR_MODE, ATTR_PLUGIN_MODULE
from custom_components.react.plugin.climate.const import ATTR_CLIMATE_PROVIDER
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.ramses.const import ATTR_SETPOINT, CLIMATE_RAMSES_PROVIDER, DOMAIN, MODE_ADVANCED_OVERRIDE, SVC_SET_ZONE_MODE

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE,
    TEST_CONFIG, 
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    climate_entity_id: str = None,
    climate_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if climate_entity_id:
        result[ATTR_ENTITY_ID] = climate_entity_id
    if climate_entity_state != None:
        result[ATTR_ENTITY_STATE] = climate_entity_state
    

def get_mock_plugins():
    result = [
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.ramses_mock", 
            ATTR_CONFIG: {}
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.climate_mock", 
            ATTR_CONFIG: { 
                ATTR_CLIMATE_PROVIDER: CLIMATE_RAMSES_PROVIDER,
            }
        },
    ]
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["climate_set_temperature_test"])
async def test_ramses_plugin_provider_set_temperature(test_context: TstContext, workflow_name: str):
    entity_id = "climate.climate_initial_off_test"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        climate_entity_id = entity_id,
        climate_entity_state = STATE_OFF,
    )

    await test_context.async_start_react(mock_plugins)
        
    temperature = 25
    data_in = {
        ATTR_TEMPERATURE: temperature
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_SETPOINT: temperature,
        ATTR_MODE: MODE_ADVANCED_OVERRIDE,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(DOMAIN, SVC_SET_ZONE_MODE, data_out)
