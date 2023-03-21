import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait_for_state_test"])
async def test_wait_for_state_initial_false(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with wait reactor:
    """

    comp = await react_component
    await comp.async_setup(workflow_name)
    ibc = await input_boolean_component

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await ibc.async_turn_on("wait_for_state_test")
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
        tc.verify_reaction_not_found()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait_for_state_delayed_test"])
async def test_wait_for_state_delayed_initial_false(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with delayed wait reactor:
    """

    comp = await react_component
    await comp.async_setup(workflow_name)
    ibc = await input_boolean_component

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await ibc.async_turn_on("wait_for_state_delayed_test")
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await tc.async_verify_reaction_event_received(delay=6)
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
        tc.verify_reaction_not_found()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait_for_state_delayed_test"])
async def test_wait_for_state_delayed_initial_true(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with delayed wait reactor
    """

    comp = await react_component
    await comp.async_setup(workflow_name)
    ibc = await input_boolean_component

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        await ibc.async_turn_on("wait_for_state_delayed_test")
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await tc.async_verify_reaction_event_received(delay=6)
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
        tc.verify_reaction_not_found()
