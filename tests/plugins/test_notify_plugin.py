import pytest

from homeassistant.const import (
    ATTR_ENTITY_ID
)
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_DATA,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE,
    ATTR_EVENT_PLUGIN,
    ATTR_EVENT_PLUGIN_PAYLOAD, 
    ATTR_PLUGIN_MODULE, 
    DOMAIN
)
from custom_components.react.plugin.notify.const import (
    ATTR_MESSAGE_DATA,
    PLUGIN_NAME
)

from tests.common import (
    FIXTURE_WORKFLOW_NAME,
    TEST_CONTEXT
)
from tests.tst_context import TstContext

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_send_message(hass: HomeAssistant, workflow_name, react_component, notify_component):
    """
    Test for notify plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.notify_plugin_mock"}
    await notify_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "mobile_group",
        ATTR_EVENT_MESSAGE: "Approve something",
        ATTR_EVENT_FEEDBACK_ITEMS: "Approve|approve|approved,Deny|deny|denied"
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(plugin_data)
        

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_confirm_feedback(hass: HomeAssistant, workflow_name, react_component, notify_component):
    """
    Test for telegram plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.notify_plugin_mock"}
    await notify_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    data_in = {
        ATTR_EVENT_PLUGIN: PLUGIN_NAME,
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_PLUGIN_PAYLOAD: {
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

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(data=data_in)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_trace_record(expected_runtime_actor_data=data_in, expected_runtime_reactor_data=[expected_data, data_in])
        
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(feedback_data)
