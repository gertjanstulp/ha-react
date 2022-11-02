import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait"])
async def test_react_wait_immediate_initial_false(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with wait reactor:
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await input_boolean_component.async_turn_on("test_wait")
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
        tc.verify_reaction_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait_delayed"])
async def test_react_wait_delayed_initial_false(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with delayed wait reactor:
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await input_boolean_component.async_turn_on("test_wait")
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await tc.async_verify_reaction_event_received(delay=6)
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
        tc.verify_reaction_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait_delayed"])
async def test_react_wait_delayed_initial_true(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with delayed wait reactor
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        await input_boolean_component.async_turn_on("test_wait")
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await tc.async_verify_reaction_event_received(delay=6)
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
        tc.verify_reaction_not_found()
