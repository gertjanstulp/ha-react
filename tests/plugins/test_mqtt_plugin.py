import pytest

from homeassistant.components.mqtt import ATTR_PAYLOAD
from homeassistant.const import (
    ATTR_ENTITY_ID,
)

from custom_components.react.const import ATTR_PLUGIN_MODULE
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.mqtt.const import ATTR_MQTT_PROVIDER

from tests._plugins.mqtt_mock.setup import MQTT_MOCK_PROVIDER
from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
    VALUE_FIXTURE_COMBOS, 
    VALUE_FIXTURES,
)
from tests.const import (
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }


def get_mock_plugin(
    mqtt_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.mqtt_mock",
        ATTR_CONFIG: {} 
    }
    if mqtt_provider:
        result[ATTR_CONFIG][ATTR_MQTT_PROVIDER] = mqtt_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["mqtt_publish_test"])
async def test_mqtt_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str):
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    
    data = {
        ATTR_MQTT_PROVIDER: invalid_provider,
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Mqtt provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["mqtt_publish_test"])
@pytest.mark.parametrize(VALUE_FIXTURES, VALUE_FIXTURE_COMBOS)
async def test_mqtt_plugin_api_publish(test_context: TstContext, workflow_name: str, config_value: bool, event_value: bool):    
    mock_plugin = get_mock_plugin(
        mqtt_provider=MQTT_MOCK_PROVIDER if config_value else None,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
    )

    await test_context.async_start_react([mock_plugin])
    
    entity_id = "some/test/topic"
    payload = "some payload"
    data_in = {
        ATTR_MQTT_PROVIDER: MQTT_MOCK_PROVIDER if event_value else None,
        ATTR_PAYLOAD: payload
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_PAYLOAD: payload
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)