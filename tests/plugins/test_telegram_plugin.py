import pytest

from homeassistant.components.notify.const import DOMAIN as NOTIFY_DOMAIN
from homeassistant.components.telegram import DOMAIN as TELEGRAM_DOMAIN
from homeassistant.components.telegram.notify import (
    ATTR_INLINE_KEYBOARD
)
from homeassistant.components.telegram_bot.const import (
    ATTR_CHAT_ID, 
    ATTR_MESSAGE, 
    ATTR_MESSAGEID, 
    ATTR_TEXT,
    DOMAIN as TELEGRAM_BOT_DOMAIN,
    EVENT_TELEGRAM_CALLBACK,
    SERVICE_EDIT_MESSAGE,
)
from homeassistant.const import (
    ATTR_COMMAND
)

from custom_components.react.const import (
    ATTR_DATA,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT,
    ATTR_EVENT_MESSAGE,
    ATTR_EVENT_NOTIFY_PROVIDER,
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD,
    ATTR_PLUGIN_MODULE,
    CONF_ENTITY_MAPS,
    EVENTPAYLOAD_COMMAND_REACT,
    REACT_ACTION_FEEDBACK_RETRIEVED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER
from custom_components.react.plugin.telegram.const import (
    ATTR_ENTITY_SOURCE,
    NOTIFY_PROVIDER_TELEGRAM, 
)
from tests._mocks import mock_data

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
                ATTR_NOTIFY_PROVIDER: NOTIFY_PROVIDER_TELEGRAM
            }
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.telegram_mock", 
            ATTR_CONFIG: {}
        }
    ]
    if entity_map:
        result[1][ATTR_CONFIG][CONF_ENTITY_MAPS] = entity_map
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_telegram_plugin_provider_notify_send_message(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_notify_provider=True,
        notify_entity_id=entity_id
    )

    await test_context.async_start_react(mock_plugins)
    
    data_out = {
        ATTR_MESSAGE: 'Approve something', 
        ATTR_DATA: {
            ATTR_INLINE_KEYBOARD: 'Approve:/react approve approved, Deny:/react deny denied'
        }
    }

    await test_context.async_send_reaction_event(data=mock_data.TEST_NOTIFY_SEND_MESSAGE_DATA_IN)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(NOTIFY_DOMAIN, entity_id, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_telegram_plugin_provider_confirm_feedback(test_context: TstContext, workflow_name: str):
    message_id = "message_id"
    conversation_id = "conversation_id"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_notify_provider=True,
    )

    await test_context.async_start_react(mock_plugins)
    
    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: conversation_id,
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: message_id,
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }
    feedback_data = {
        ATTR_MESSAGEID: 'message_id', 
        ATTR_CHAT_ID: 'conversation_id', 
        ATTR_EVENT_MESSAGE: 'text - acknowledgement', 
        ATTR_INLINE_KEYBOARD: None
    }

    await test_context.async_send_reaction_event(reactor_index=1, data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(TELEGRAM_BOT_DOMAIN, SERVICE_EDIT_MESSAGE, feedback_data)
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_telegram_plugin_task_callback_action(test_context: TstContext):
    entity_source = "entity_source"
    mapped_entity_source = "mapped_entity_source"
    feedback = "feedback"
    acknowledgement = "acknowledgement"
    chat_id = "chat_id"
    messageid = "messageid"
    text = "text"
    mock_plugins = get_mock_plugins(
        entity_map={
            ATTR_ENTITY_SOURCE: mapped_entity_source
        }
    )
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugins)

    data_in = {
        ATTR_COMMAND: EVENTPAYLOAD_COMMAND_REACT,
        ATTR_ENTITY_SOURCE: entity_source,
        ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: feedback,
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: acknowledgement,
        ATTR_CHAT_ID: chat_id,
        ATTR_MESSAGE: {
            ATTR_MESSAGEID: messageid,
            ATTR_TEXT: text
        }
    }

    expected_data = {
        ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: feedback,
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: acknowledgement,
        ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_TELEGRAM,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: chat_id,
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: messageid,
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: text,
        }
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_TELEGRAM_CALLBACK, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=mapped_entity_source, 
            expected_type=REACT_TYPE_NOTIFY,
            expected_action=REACT_ACTION_FEEDBACK_RETRIEVED, 
            expected_data=expected_data
        )
