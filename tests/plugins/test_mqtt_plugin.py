import pytest

from homeassistant.components.mqtt import ATTR_PAYLOAD
from homeassistant.const import (
    ATTR_ENTITY_ID,
    EVENT_STATE_CHANGED,
)

from custom_components.react.const import (
    ATTR_NEW_STATE, 
    ATTR_OLD_STATE, 
    ATTR_PLUGIN_MODULE, 
    ATTR_STATE,
    CONF_ENTITY_MAPS,
    REACT_ACTION_DOUBLE_PRESS,
    REACT_ACTION_LONG_PRESS,
    REACT_ACTION_SHORT_PRESS,
    REACT_TYPE_BUTTON,
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.mqtt.const import (
    ATTR_MQTT_PROVIDER,
    CONF_DOUBLE_PRESS_ACTION,
    CONF_LONG_PRESS_ACTION,
    CONF_MAPPED_ENTITY_ID,
    CONF_SHORT_PRESS_ACTION,
)

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
    entity_maps: list = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.mqtt_mock",
        ATTR_CONFIG: {} 
    }
    if mqtt_provider:
        result[ATTR_CONFIG][ATTR_MQTT_PROVIDER] = mqtt_provider
    if entity_maps:
        result[ATTR_CONFIG][CONF_ENTITY_MAPS] = entity_maps
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


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_mqtt_task_short_press_input_block(test_context: TstContext):
    TEST_ENTITY_ID = "test_entity_id"
    TEST_MAPPED_DEVICE_ID = "test_mapped_device_id"
    TEST_SHORT_PRESS_ACTION = "test_short_press_action"
    
    mock_plugins = get_mock_plugin(
        entity_maps=[{
            ATTR_ENTITY_ID: TEST_ENTITY_ID,
            CONF_MAPPED_ENTITY_ID: TEST_MAPPED_DEVICE_ID,
            CONF_SHORT_PRESS_ACTION: TEST_SHORT_PRESS_ACTION
        }]
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugins)

    data_in = {
        ATTR_ENTITY_ID: TEST_ENTITY_ID, 
        ATTR_OLD_STATE: {
            ATTR_STATE: TEST_SHORT_PRESS_ACTION
        },
        ATTR_NEW_STATE: {
            ATTR_STATE: ""
        }
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_STATE_CHANGED, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=TEST_MAPPED_DEVICE_ID, 
            expected_type=REACT_TYPE_BUTTON,
            expected_action=REACT_ACTION_SHORT_PRESS)
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_mqtt_task_long_press_input_block(test_context: TstContext):
    TEST_ENTITY_ID = "test_entity_id"
    TEST_MAPPED_DEVICE_ID = "test_mapped_device_id"
    TEST_LONG_PRESS_ACTION = "test_long_press_action"
    
    mock_plugins = get_mock_plugin(
        entity_maps=[{
            ATTR_ENTITY_ID: TEST_ENTITY_ID,
            CONF_MAPPED_ENTITY_ID: TEST_MAPPED_DEVICE_ID,
            CONF_LONG_PRESS_ACTION: TEST_LONG_PRESS_ACTION
        }]
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugins)

    data_in = {
        ATTR_ENTITY_ID: TEST_ENTITY_ID, 
        ATTR_OLD_STATE: {
            ATTR_STATE: TEST_LONG_PRESS_ACTION
        },
        ATTR_NEW_STATE: {
            ATTR_STATE: ""
        }
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_STATE_CHANGED, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=TEST_MAPPED_DEVICE_ID, 
            expected_type=REACT_TYPE_BUTTON,
            expected_action=REACT_ACTION_LONG_PRESS)
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_mqtt_task_double_press_input_block(test_context: TstContext):
    TEST_ENTITY_ID = "test_entity_id"
    TEST_MAPPED_DEVICE_ID = "test_mapped_device_id"
    TEST_DOUBLE_PRESS_ACTION = "test_double_press_action"
    
    mock_plugins = get_mock_plugin(
        entity_maps=[{
            ATTR_ENTITY_ID: TEST_ENTITY_ID,
            CONF_MAPPED_ENTITY_ID: TEST_MAPPED_DEVICE_ID,
            CONF_DOUBLE_PRESS_ACTION: TEST_DOUBLE_PRESS_ACTION
        }]
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugins)

    data_in = {
        ATTR_ENTITY_ID: TEST_ENTITY_ID, 
        ATTR_OLD_STATE: {
            ATTR_STATE: TEST_DOUBLE_PRESS_ACTION
        },
        ATTR_NEW_STATE: {
            ATTR_STATE: ""
        }
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_STATE_CHANGED, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=TEST_MAPPED_DEVICE_ID, 
            expected_type=REACT_TYPE_BUTTON,
            expected_action=REACT_ACTION_DOUBLE_PRESS)
        test_context.verify_has_no_log_issues()

