import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_call_service_delete_reaction(hass: HomeAssistant, workflow_name, react_component):
    
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_found()
        reaction_id = tc.retrieve_reaction_id()
        await comp.async_call_service_delete_reaction(reaction_id)
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_call_service_react_now(hass: HomeAssistant, workflow_name, react_component):
    
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_found()
        reaction_id = tc.retrieve_reaction_id()
        await comp.async_call_service_react_now(reaction_id)
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
