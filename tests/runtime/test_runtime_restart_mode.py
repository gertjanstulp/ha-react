import pytest

from homeassistant.core import HomeAssistant
from custom_components.react.base import ReactBase
from custom_components.react.const import DOMAIN

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled_restart_abort"])
async def test_runtime_restart_mode_abort(hass: HomeAssistant, workflow_name, react_component):
    
    comp = await react_component
    await comp.async_setup(workflow_name)

    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        tc.verify_run_found()
        await tc.async_verify_reaction_event_not_received()
        await react.runtime.async_shutdown(is_hass_shutdown=True)
        await react.hass.async_block_till_done()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_run_not_found()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled_restart_force"])
async def test_runtime_restart_mode_force(hass: HomeAssistant, workflow_name, react_component):
    
    comp = await react_component
    await comp.async_setup(workflow_name)

    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        tc.verify_run_found()
        await tc.async_verify_reaction_event_not_received()
        await react.runtime.async_shutdown(is_hass_shutdown=True)
        await react.hass.async_block_till_done()
        await tc.async_verify_reaction_event_received()
        tc.verify_run_not_found()
