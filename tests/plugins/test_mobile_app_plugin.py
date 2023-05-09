import pytest

from homeassistant.components.mobile_app import DOMAIN as MOBILE_APP_DOMAIN
from homeassistant.components.notify.const import (
    ATTR_TITLE,
    DOMAIN as NOTIFY_DOMAIN
)
from homeassistant.const import (
    ATTR_DEVICE_ID
)

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT,
    ATTR_EVENT_MESSAGE,
    ATTR_EVENT_NOTIFY_PROVIDER,
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD,
    ATTR_PLUGIN_MODULE,
    ATTR_TYPE,
    CONF_ENTITY_MAPS,
    REACT_ACTION_FEEDBACK_RETRIEVED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.mobile_app.const import (
    ATTR_ACTIONS, 
    ATTR_MESSAGE, 
    ATTR_PERSISTENT, 
    ATTR_STICKY, 
    ATTR_TAG, 
    EVENT_MOBILE_APP_CALLBACK, 
    MESSAGE_CLEAR_NOTIFICATION,
    NOTIFY_PROVIDER_MOBILE_APP
)

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import ATTR_SERVICE_NAME, TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    notify_entity_id: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if notify_entity_id:
        result[ATTR_SERVICE_NAME] = notify_entity_id


def get_mock_plugin(
    entity_map: dict = None,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.mobile_app_mock", 
        ATTR_CONFIG: {}
    }
    if entity_map:
        result[ATTR_CONFIG][CONF_ENTITY_MAPS] = entity_map
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_mobile_app_plugin_provider_notify_send_message(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
    )
    set_test_config(test_context,
        notify_entity_id=entity_id
    )

    await test_context.async_start_react(mock_plugin)
    
    data = {
        ATTR_EVENT_MESSAGE: "Approve something",
        ATTR_DATA: {
            ATTR_ACTIONS:  [ {
                ATTR_ACTION : "approve",
                ATTR_TITLE : "Approve"
            }, {
                ATTR_ACTION : "deny",
                ATTR_TITLE : "Deny"        
            } 
            ],
            ATTR_PERSISTENT: "true",
            ATTR_TAG: "0123456789",
            ATTR_STICKY: "true"
        }
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(NOTIFY_DOMAIN, entity_id, data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_mobile_app_plugin_provider_confirm_feedback(test_context: TstContext, workflow_name: str):
    message_id = "message_id"
    conversation_id = "conversation_id"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugin)
    
    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER: MOBILE_APP_DOMAIN,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: conversation_id,
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: message_id,
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }
    expected_data = {'feedback': ''}
    feedback_data = {
        ATTR_EVENT_MESSAGE: MESSAGE_CLEAR_NOTIFICATION,
        ATTR_DATA: {
            ATTR_TAG: conversation_id
        }
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(data=data_in)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=2)
        test_context.verify_trace_record(expected_runtime_actor_data=data_in, expected_runtime_reactor_data=[expected_data, data_in], expected_runtime_reactor_entity=["reactor_entity_notify_confirm_feedback_test", "telegram_user"])
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(NOTIFY_DOMAIN, message_id, feedback_data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_mobile_app_task_callback_transform_in(test_context: TstContext):
    DEVICE_ID = "device_id"
    MAPPED_DEVICE_ID = f"mapped_{DEVICE_ID}"
    FEEDBACK = "feedback"
    TAG = "tag"
    MESSAGE = "message"
    
    mock_plugin = mock_plugin = get_mock_plugin(
        entity_map={
            DEVICE_ID: MAPPED_DEVICE_ID
        }
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugin)

    data_in = {
        ATTR_ACTION: FEEDBACK,
        ATTR_DEVICE_ID: DEVICE_ID,
        ATTR_TAG: TAG,
        ATTR_MESSAGE: MESSAGE
    }

    data_out = {
        ATTR_ENTITY: MAPPED_DEVICE_ID,
        ATTR_TYPE: REACT_TYPE_NOTIFY,
        ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
        ATTR_DATA: {
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: FEEDBACK,
            ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOBILE_APP,
            ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
                ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: TAG,
                ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: MAPPED_DEVICE_ID,
                ATTR_EVENT_FEEDBACK_ITEM_TEXT: MESSAGE,
            }
        }
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_MOBILE_APP_CALLBACK, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(expected_data=data_out)
