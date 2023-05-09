import pytest

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID
)

from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE,
    ATTR_EVENT_NOTIFY_PROVIDER,
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD, 
    ATTR_PLUGIN_MODULE, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER

from tests._plugins.notify_mock.plugin import NOTIFY_PROVIDER_MOCK
from tests.common import (
    FIXTURE_WORKFLOW_NAME,
)
from tests.const import (
    ATTR_SERVICE_NAME,
    TEST_CONFIG
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    notify_service: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if notify_service:
        result[ATTR_SERVICE_NAME] = notify_service


def get_mock_plugin(
    notify_provider: str = None,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.notify_mock", 
        ATTR_CONFIG : {
        }
    }
    if notify_provider:
        result[ATTR_CONFIG][ATTR_NOTIFY_PROVIDER] = notify_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_no_service(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK,
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugin)
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_log_warning(f"Notify plugin: Api - {NOTIFY_DOMAIN}.{entity_id} not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_no_notify_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        notify_service=entity_id,
    )

    await test_context.async_start_react(mock_plugin)
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_log_error(f"Notify plugin: Api - Notify provider for '{entity_id}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        notify_service=entity_id,
    )

    await test_context.async_start_react(mock_plugin)
        
    plugin_data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_EVENT_MESSAGE: "Approve something",
        ATTR_EVENT_FEEDBACK_ITEMS: "Approve|approve|approved,Deny|deny|denied"
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(plugin_data)
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_plugin_api_confirm_feedback_no_notify_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        notify_service=entity_id,
    )

    await test_context.async_start_react(mock_plugin)
    

    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOCK,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(data=data_in)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=2)
        test_context.verify_has_log_error(f"Notify plugin: Api - Notify provider not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_plugin_api_confirm_feedback(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        notify_service=entity_id,
    )

    await test_context.async_start_react(mock_plugin)
    
    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOCK,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }
    expected_data = {'feedback': ''}
    feedback_data = {
        ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
        ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
        ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text",
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement"
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(data=data_in)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=2)
        test_context.verify_trace_record(expected_runtime_actor_data=data_in, expected_runtime_reactor_data=[expected_data, data_in], expected_runtime_reactor_entity=["reactor_entity_notify_confirm_feedback_test", "telegram_user"])
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(feedback_data)
