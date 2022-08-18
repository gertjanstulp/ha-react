import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["immediate"])
async def test_react_call_service_trigger_workflow(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for calling trigger service
    """
    
    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await react_component.async_call_service_trigger_workflow("react.workflow_immediate")
        await hass.async_block_till_done()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_react_call_service_trigger_reaction(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for calling trigger service
    """
    
    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_found()
        reaction_id = tc.retrieve_reaction_entity_id()
        await react_component.async_call_service_trigger_reaction(reaction_id)
        await hass.async_block_till_done()
        tc.verify_reaction_entity_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_react_call_service_delete_reaction(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for calling trigger service
    """
    
    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_found()
        reaction_id = tc.retrieve_reaction_entity_id()
        await react_component.async_call_service_delete_reaction(reaction_id)
        await hass.async_block_till_done()
        tc.verify_reaction_entity_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_react_call_service_react_now(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for calling trigger service
    """
    
    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_found()
        reaction_id = tc.retrieve_reaction_entity_id()
        await react_component.async_call_service_react_now(reaction_id)
        await hass.async_block_till_done()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
