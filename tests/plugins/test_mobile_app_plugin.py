import pytest

from homeassistant.components.mobile_app import DOMAIN as MOBILE_APP_DOMAIN
from homeassistant.components.notify.const import (
    ATTR_TITLE,
    DOMAIN as NOTIFY_DOMAIN
)
from homeassistant.const import ATTR_DEVICE_ID

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE,
    ATTR_EVENT_NOTIFY_PROVIDER,
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD,
    ATTR_PLUGIN_MODULE,
    CONF_ENTITY_MAPS,
    REACT_ACTION_FEEDBACK_RETRIEVED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.plugin.const import ATTR_ACTIONS, ATTR_CONFIG
from custom_components.react.plugin.mobile_app.const import (
    ATTR_MESSAGE, 
    ATTR_PERSISTENT, 
    ATTR_STICKY, 
    ATTR_TAG, 
    EVENT_MOBILE_APP_CALLBACK, 
    MESSAGE_CLEAR_NOTIFICATION,
    NOTIFY_PROVIDER_MOBILE_APP
)
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import ATTR_SERVICE_NAME, ATTR_SETUP_MOCK_PROVIDER, TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_notify_provider: bool = False,
    notify_entity_id: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_notify_provider
    }
    if notify_entity_id:
        result[ATTR_SERVICE_NAME] = notify_entity_id


def get_mock_plugins(
    entity_map: dict = None,
):
    result = [
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.notify_mock",
            ATTR_CONFIG: {
                ATTR_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOBILE_APP
            }
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.mobile_app_mock", 
            ATTR_CONFIG: {}
        }
    ]
    if entity_map:
        result[1][ATTR_CONFIG][CONF_ENTITY_MAPS] = entity_map
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_mobile_app_plugin_provider_notify_send_message(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_notify_provider=True,
        notify_entity_id=entity_id
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
        ATTR_EVENT_MESSAGE: event_message,
        ATTR_DATA: {
            ATTR_ACTIONS:  [ {
                ATTR_ACTION : feedback1,
                ATTR_TITLE : title1
            }, {
                ATTR_ACTION : feedback2,
                ATTR_TITLE : title2     
            } 
            ],
            ATTR_PERSISTENT: "true",
            ATTR_TAG: "0123456789",
            ATTR_STICKY: "true"
        }
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(NOTIFY_DOMAIN, entity_id, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_mobile_app_plugin_provider_confirm_feedback(test_context: TstContext, workflow_name: str):
    message_id = "message_id"
    conversation_id = "conversation_id"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_notify_provider=True,
    )

    await test_context.async_start_react(mock_plugins)
    
    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER: MOBILE_APP_DOMAIN,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: conversation_id,
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: message_id,
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }
    data_out = {
        ATTR_EVENT_MESSAGE: MESSAGE_CLEAR_NOTIFICATION,
        ATTR_DATA: {
            ATTR_TAG: conversation_id
        }
    }

    await test_context.async_send_reaction_event(reactor_index=1, data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(NOTIFY_DOMAIN, message_id, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_mobile_app_task_callback_input_block(test_context: TstContext):
    DEVICE_ID = "device_id"
    MAPPED_DEVICE_ID = f"mapped_{DEVICE_ID}"
    FEEDBACK = "feedback"
    TAG = "tag"
    MESSAGE = "message"
    
    mock_plugins = get_mock_plugins(
        entity_map={
            DEVICE_ID: MAPPED_DEVICE_ID
        }
    )
    set_test_config(test_context,
        setup_mock_notify_provider=True,
    )

    await test_context.async_start_react(mock_plugins)

    data_in = {
        ATTR_ACTION: FEEDBACK,
        ATTR_DEVICE_ID: DEVICE_ID,
        ATTR_TAG: TAG,
        ATTR_MESSAGE: MESSAGE
    }

    expected_data = {
        ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: FEEDBACK,
        ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOBILE_APP,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: TAG,
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: MAPPED_DEVICE_ID,
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: MESSAGE,
    }
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_MOBILE_APP_CALLBACK, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=MAPPED_DEVICE_ID, 
            expected_type=REACT_TYPE_NOTIFY,
            expected_action=REACT_ACTION_FEEDBACK_RETRIEVED, 
            expected_data=expected_data)
        test_context.verify_has_no_log_issues()
