import pytest

from homeassistant.components.notify.const import ATTR_TITLE
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.group import DOMAIN as GROUP_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_HOME,
    STATE_ON,
)

from custom_components.react.const import (
    ACTION_CHANGE,
    ACTION_TOGGLE,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE, 
    ATTR_PLUGIN_MODULE, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.group.const import NOTIFY_PROVIDER_GROUP
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER

from tests._plugins.group_mock.setup import (
    ATTR_CHILD_SERVICE, 
    ATTR_KILL_CHILD_PROVIDER,
    ATTR_KILL_RESOLVER
)
from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
)
from tests.const import (
    ATTR_SERVICE_NAME,
    ATTR_SETUP_MOCK_PROVIDER,
    TEST_CONFIG
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_notify_provider: bool = False,
    notify_entity_id: str = None,
    child_service: str = None,
    kill_resolver: bool = False,
    kill_child_provider: bool = False,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_notify_provider
    }
    if notify_entity_id:
        result[ATTR_SERVICE_NAME] = notify_entity_id
    if child_service:
        result[ATTR_CHILD_SERVICE] = child_service
    if kill_resolver:
        result[ATTR_KILL_RESOLVER] = True
    if kill_child_provider:
        result[ATTR_KILL_CHILD_PROVIDER] = True
    

def get_mock_plugins():
    result = [
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.notify_mock",
            ATTR_CONFIG: {
                ATTR_NOTIFY_PROVIDER: NOTIFY_PROVIDER_GROUP
            }
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.group_mock", 
            ATTR_CONFIG: {}
        },
    ]
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_resolver(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        notify_entity_id=entity_id,
        kill_resolver=True,
    )

    await test_context.async_start_react(mock_plugins)
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error("1 - Notify resolver not found, notify plugin is not configured")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_notify_platform(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        notify_entity_id=entity_id,
    )

    await test_context.async_start_react(mock_plugins)
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Could not find notify platform for entity '{entity_id}'")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_child_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    child_entity_id = "mobile_item"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        notify_entity_id=entity_id,
        child_service=child_entity_id,
        kill_child_provider=True,
    )

    await test_context.async_start_react(mock_plugins)
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - Could not find notify provider for child entity '{child_entity_id}'")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_send_message(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    child_entity_id = "mobile_item"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_notify_provider=True,
        notify_entity_id=entity_id,
        child_service=child_entity_id
    )

    await test_context.async_start_react(mock_plugins)
    
    event_message = "Approve something"
    title1 = "Approve"
    feedback1 = "approve"
    acknowledgement1 = "approved"
    title2 = "Deny"
    feedback2 = "deny"
    acknowledgement2 = "denied"

    data_in = {
        ATTR_EVENT_MESSAGE: event_message,
        ATTR_EVENT_FEEDBACK_ITEMS: [{
            ATTR_TITLE: title1,
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: feedback1,
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: acknowledgement1
        },{
            ATTR_TITLE: title2,
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: feedback2,
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: acknowledgement2
        }]
    }
    data_out = {
        ATTR_ENTITY_ID: child_entity_id,
        ATTR_EVENT_MESSAGE: event_message,
        ATTR_EVENT_FEEDBACK_ITEMS: f"{title1}|{feedback1}|{acknowledgement1},{title2}|{feedback2}|{acknowledgement2}"
    }

    await test_context.async_start_react(mock_plugins)
    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person_group_state_test"])
async def test_person_group_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "person_group_state_test"
    mock_plugins = get_mock_plugins()
    await test_context.async_start_virtual()
    await test_context.async_start_group()
    await test_context.async_start_person()
    dtc = await test_context.async_start_device_tracker()
    await test_context.async_start_react(mock_plugins)

    async with test_context.async_listen_action_event():
        await dtc.async_see(entity_id, STATE_HOME)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=GROUP_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=GROUP_DOMAIN,
            expected_action=STATE_HOME,
            event_with_action_name=STATE_HOME)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=GROUP_DOMAIN,
            expected_action=ACTION_TOGGLE,
            event_with_action_name=ACTION_TOGGLE)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["group_state_test"])
async def test_group_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "group_state_test"
    mock_plugins = get_mock_plugins()
    await test_context.async_start_binary_sensor()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_group()
    await test_context.async_start_react(mock_plugins)
    
    async with test_context.async_listen_action_event():
        await vc.async_turn_on(BINARY_SENSOR_DOMAIN, entity_id)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=GROUP_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=GROUP_DOMAIN,
            expected_action=STATE_ON,
            event_with_action_name=STATE_ON)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=GROUP_DOMAIN,
            expected_action=ACTION_TOGGLE,
            event_with_action_name=ACTION_TOGGLE)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()
