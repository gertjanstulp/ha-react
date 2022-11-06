import pytest

from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_MESSAGE,
    DOMAIN
)
from custom_components.react.plugin.telegram.telegram_plugin import ATTR_SERVICE_DATA_INLINE_KEYBOARD

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actionable_notification"])
async def test_telegram_notify_send_message(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for actionable notifications
    """

    await react_component.async_setup(workflow_name, plugins=["tests._plugins.telegram_plugin_notify_send_message_mock"])
    react: ReactBase = hass.data[DOMAIN]
    
    message_data = {
        ATTR_ENTITY: "mobile_group",
        "message_data":{
            ATTR_EVENT_MESSAGE: "Approve something",
            ATTR_DATA: {
                ATTR_SERVICE_DATA_INLINE_KEYBOARD: "Approve:/react approve approved, Deny:/react deny denied"
            }
        } 
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data["test_context"] = tc
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_notify_send_message_sent()
        tc.verify_notify_send_message_data(message_data)


# @pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actionable_notification_feedback"])
# async def test_react_actionable_notification_feedback(hass: HomeAssistant, workflow_name, react_component):
#     """
#     Test for actionable notifications feedback
#     """

#     await react_component.async_setup(workflow_name, init_notify_plugin=True, additional_workflows=["actionable_notification"])
#     react: ReactBase = hass.data[DOMAIN]
#     notify_plugin = react.plugin_factory.get_notify_plugin()

#     tc = TstContext(hass, workflow_name)
#     tc_actionable_notification = TstContext(hass, "actionable_notification")
#     send_workflow = tc_actionable_notification.workflow_config
#     notify_plugin.hook_test(tc)
#     data_out = {
#         "feedback": "approve"
#     }
#     async with tc.async_listen_react_event():
#         tc.verify_reaction_not_found()
#         await tc.async_send_notify_feedback_event(send_workflow)
#         tc.verify_acknowledgement_sent()
#         tc.verify_acknowledgement_data(send_workflow)
#         await tc.async_verify_reaction_event_received()
#         tc.verify_reaction_event_data(expected_data=data_out)
#         tc.verify_trace_record(expected_runtime_reactor_data=data_out)