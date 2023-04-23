import pytest

from homeassistant.components.mobile_app import DOMAIN as MOBILE_APP_DOMAIN
from homeassistant.components.notify.const import (
    ATTR_TITLE,
    DOMAIN as NOTIFY_DOMAIN
)
from homeassistant.const import (
    ATTR_DEVICE_ID
)
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
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
    DOMAIN,
    REACT_ACTION_FEEDBACK_RETRIEVED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.mobile_app.const import ATTR_ACTIONS, ATTR_MESSAGE, ATTR_PERSISTENT, ATTR_STICKY, ATTR_TAG, EVENT_MOBILE_APP_CALLBACK, MESSAGE_CLEAR_NOTIFICATION
from tests.const import ATTR_ENTITY_STATE, ATTR_SERVICE_NAME

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT


def get_mock_plugin(
    notify_entity_id: str = None,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.mobile_app_plugin_mock", 
        ATTR_CONFIG: {}
    }
    if notify_entity_id:
        result[ATTR_CONFIG][ATTR_SERVICE_NAME] = notify_entity_id
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_mobile_app_plugin_provider_notify_send_message(hass: HomeAssistant, react_component, workflow_name):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_entity_id=entity_id
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

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

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_service_call_sent()
        tc.verify_service_call_content(NOTIFY_DOMAIN, entity_id, data)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_mobile_app_plugin_provider_confirm_feedback(hass: HomeAssistant, workflow_name, react_component):
    message_id = "message_id"
    conversation_id = "conversation_id"
    mock_plugin = get_mock_plugin(
        # notify_entity_id=entity_id
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

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

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(data=data_in)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_trace_record(expected_runtime_actor_data=data_in, expected_runtime_reactor_data=[expected_data, data_in])
        tc.verify_has_no_log_issues()
        tc.verify_service_call_sent()
        tc.verify_service_call_content(NOTIFY_DOMAIN, message_id, feedback_data)


@pytest.mark.asyncio
async def test_mobile_app_task_callback_transform_in(hass: HomeAssistant, react_component):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.mobile_app_plugin_mock"}
    comp = await react_component
    await comp.async_setup(None, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, None)
    react.hass.data[TEST_CONTEXT] = tc

    DEVICE_ID = "device_id"
    FEEDBACK = "feedback"
    TAG = "tag"
    MESSAGE = "message"

    data_in = {
        ATTR_ACTION: FEEDBACK,
        ATTR_DEVICE_ID: DEVICE_ID,
        ATTR_TAG: TAG,
        ATTR_MESSAGE: MESSAGE
    }

    data_out = {
        ATTR_ENTITY: DEVICE_ID,
        ATTR_TYPE: REACT_TYPE_NOTIFY,
        ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
        ATTR_DATA: {
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: FEEDBACK,
            ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
                ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: TAG,
                ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: DEVICE_ID,
                ATTR_EVENT_FEEDBACK_ITEM_TEXT: MESSAGE,
            }
        }
    }

    async with tc.async_listen_action_event():
        await tc.async_send_event(EVENT_MOBILE_APP_CALLBACK, data_in)
        await tc.async_verify_action_event_received()
        tc.verify_action_event_data(expected_data=data_out)
