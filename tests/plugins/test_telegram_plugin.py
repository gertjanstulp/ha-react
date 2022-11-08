import pytest

from homeassistant.core import HomeAssistant

from homeassistant.components.telegram_bot import (
    ATTR_CHAT_ID, 
    ATTR_KEYBOARD_INLINE,
    ATTR_MESSAGE, 
    ATTR_MESSAGEID, 
    ATTR_TEXT,
    EVENT_TELEGRAM_CALLBACK
)
from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_MESSAGE,
    ATTR_EVENT_PLUGIN,
    ATTR_EVENT_PLUGIN_PAYLOAD,
    ATTR_PLUGIN_MODULE,
    ATTR_TYPE,
    DOMAIN,
    EVENTPAYLOAD_COMMAND_REACT,
    REACT_ACTION_FEEDBACK_RETRIEVED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.lib.config import Plugin
from custom_components.react.plugin.telegram.const import ATTR_COMMAND, ATTR_ENTITY_SOURCE, ATTR_MESSAGE_DATA, ATTR_SERVICE_DATA_INLINE_KEYBOARD, PLUGIN_NAME

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actionable_notification"])
async def test_telegram_notify_send_message(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for actionable notifications
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.telegram_plugin_notify_send_message_mock"}
    await react_component.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    message_data = {
        ATTR_ENTITY: "mobile_group",
        ATTR_MESSAGE_DATA: {
            ATTR_EVENT_MESSAGE: "Approve something",
            ATTR_DATA: {
                ATTR_SERVICE_DATA_INLINE_KEYBOARD: "Approve:/react approve approved, Deny:/react deny denied"
            }
        } 
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data["test_context"] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_notify_send_message_sent()
        tc.verify_notify_send_message_data(message_data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actionable_notification_feedback"])
async def test_telegram_notify_confirm_feedback(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for actionable notifications
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.telegram_plugin_notify_confirm_feedback_mock"}
    await react_component.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    data_in = {
        ATTR_EVENT_PLUGIN: PLUGIN_NAME,
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "",
        ATTR_EVENT_PLUGIN_PAYLOAD: {
            ATTR_MESSAGEID: "",
            ATTR_CHAT_ID: "",
            ATTR_TEXT: ""
        }
    }
    expected_data = {'feedback': ''}
    feedback_data = {
        ATTR_MESSAGEID: "",
        ATTR_CHAT_ID: "",
        ATTR_MESSAGE: " - ",
        ATTR_KEYBOARD_INLINE: None
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data["test_context"] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(data=data_in)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_trace_record(expected_runtime_actor_data=data_in, expected_runtime_reactor_data=[expected_data, data_in])
        
        tc.verify_notify_confirm_feedback_sent()
        tc.verify_notify_confirm_feedback_data(feedback_data)


async def test_telegram_callback_transform_in(hass: HomeAssistant, react_component):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.telegram_plugin_callback_transform_in_mock"}
    await react_component.async_setup(None, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, None)
    react.hass.data["test_context"] = tc

    data_in = {
        ATTR_COMMAND: EVENTPAYLOAD_COMMAND_REACT,
        ATTR_ENTITY_SOURCE: "entity_source",
        ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: "feedback",
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_CHAT_ID: "chat_id",
        ATTR_MESSAGE: {
            ATTR_MESSAGEID: "messageid",
            ATTR_TEXT: "text"
        }
    }

    data_out = {
        ATTR_ENTITY: None,
        ATTR_TYPE: REACT_TYPE_NOTIFY,
        ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
        ATTR_DATA: {
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: "feedback",
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
            ATTR_EVENT_PLUGIN: PLUGIN_NAME,
            ATTR_EVENT_PLUGIN_PAYLOAD: {
                ATTR_CHAT_ID: "chat_id",
                ATTR_MESSAGEID: "messageid",
                ATTR_TEXT: "text",
            }
        }
    }

    async with tc.async_listen_action_event():
        await tc.async_send_event(EVENT_TELEGRAM_CALLBACK, data_in)
        await tc.async_verify_action_event_received()
        tc.verify_action_event_data(expected_data=data_out)
        test = 1