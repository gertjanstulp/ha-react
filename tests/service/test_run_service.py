import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_react_call_service_delete_run(hass: HomeAssistant, workflow_name, react_component):
    
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_run_not_found()
        await tc.async_send_action_event()
        tc.verify_run_found()
        run_id = tc.retrieve_run_id()
        await comp.async_call_service_delete_run(run_id)
        await hass.async_block_till_done()
        tc.verify_run_not_found()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace2"])
async def test_react_call_service_delete_run_multiple_reactions(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    
    comp = await react_component
    await comp.async_setup(workflow_name)
    await hass.async_block_till_done()
    ibc = await input_boolean_component

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_run_not_found()
        await ibc.async_turn_on("test_trace2")
        await tc.async_send_action_event(entity="actor_entity_trace2_2", type="actor_type_trace2_2", action="actor_action_trace2_2")
        tc.verify_run_found()
        tc.verify_reaction_found(expected_count=2)
        run_id = tc.retrieve_run_id()
        await comp.async_call_service_delete_run(run_id)
        await hass.async_block_till_done()
        tc.verify_run_not_found()
        tc.verify_reaction_not_found()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_react_call_service_run_now(hass: HomeAssistant, workflow_name, react_component):
    
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_run_not_found()
        await tc.async_send_action_event()
        tc.verify_run_found()
        run_id = tc.retrieve_run_id()
        await comp.async_call_service_run_now(run_id)
        await hass.async_block_till_done()
        tc.verify_run_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()