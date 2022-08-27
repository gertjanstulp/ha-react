import pytest

from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, 
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, 
    ATTR_EVENT_FEEDBACK_ITEM_TITLE, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE, 
    DOMAIN
)

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actionable_notification"])
async def test_react_actionable_notification(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for actionable notifications
    """

    await react_component.async_setup(workflow_name, init_notify_plugin=True)
    react: ReactBase = hass.data[DOMAIN]
    notify_plugin = react.plugin_factory.get_notify_plugin()
    data_out = {
        ATTR_EVENT_MESSAGE: "Approve something",
        ATTR_EVENT_FEEDBACK_ITEMS: [
            { ATTR_EVENT_FEEDBACK_ITEM_TITLE: "Approve", ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: "approve", ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "approved" },
            { ATTR_EVENT_FEEDBACK_ITEM_TITLE: "Deny", ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: "deny", ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "denied" }
        ]
    }

    tc = TstContext(hass, workflow_name)
    notify_plugin.hook_test(tc)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_data=data_out)
        tc.verify_trace_record()
        
        tc.verify_notification_sent()
        tc.verify_notification_data()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actionable_notification_feedback"])
async def test_react_actionable_notification_feedback(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for actionable notifications feedback
    """

    await react_component.async_setup(workflow_name, init_notify_plugin=True, additional_workflows=["actionable_notification"])
    react: ReactBase = hass.data[DOMAIN]
    notify_plugin = react.plugin_factory.get_notify_plugin()

    tc = TstContext(hass, workflow_name)
    tc_actionable_notification = TstContext(hass, "actionable_notification")
    send_workflow = tc_actionable_notification.workflow_config
    notify_plugin.hook_test(tc)
    data_out = {
        "feedback": "approve"
    }
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_notify_feedback_event(send_workflow)
        tc.verify_acknowledgement_sent()
        tc.verify_acknowledgement_data(send_workflow)
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_data=data_out)
        tc.verify_trace_record(expected_runtime_reactor_data=data_out)
