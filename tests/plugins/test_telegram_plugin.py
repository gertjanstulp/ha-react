import pytest

from homeassistant.const import (
    ATTR_COMMAND
)
from homeassistant.core import HomeAssistant

from homeassistant.components.telegram_bot import (
    ATTR_CHAT_ID, 
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
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT,
    ATTR_EVENT_PLUGIN,
    ATTR_EVENT_PLUGIN_PAYLOAD,
    ATTR_PLUGIN_MODULE,
    ATTR_TYPE,
    DOMAIN,
    EVENTPAYLOAD_COMMAND_REACT,
    REACT_ACTION_FEEDBACK_RETRIEVED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.plugin.notify.const import PLUGIN_NAME
from custom_components.react.plugin.telegram.const import (
    ATTR_ENTITY_SOURCE, 
)

from tests.tst_context import TstContext
from tests.common import TEST_CONTEXT


@pytest.mark.asyncio
async def test_telegram_callback_transform_in(hass: HomeAssistant, react_component):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.telegram_plugin_mock"}
    comp = await react_component
    await comp.async_setup(None, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, None)
    react.hass.data[TEST_CONTEXT] = tc

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
        ATTR_ENTITY: "entity_source",
        ATTR_TYPE: REACT_TYPE_NOTIFY,
        ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
        ATTR_DATA: {
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: "feedback",
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
            ATTR_EVENT_PLUGIN: PLUGIN_NAME,
            ATTR_EVENT_PLUGIN_PAYLOAD: {
                ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "chat_id",
                ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
                ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text",
            }
        }
    }

    async with tc.async_listen_action_event():
        await tc.async_send_event(EVENT_TELEGRAM_CALLBACK, data_in)
        await tc.async_verify_action_event_received()
        tc.verify_action_event_data(expected_data=data_out)
