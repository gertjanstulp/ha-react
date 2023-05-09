import pytest

from homeassistant.core import HomeAssistant
from custom_components.react.base import ReactBase
from custom_components.react.const import DOMAIN

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled_restart_abort"])
async def test_runtime_restart_mode_abort(test_context: TstContext, workflow_name: str):
    await test_context.async_start_react()

    async with test_context.async_listen_reaction_event():
        await test_context.async_send_action_event()
        test_context.verify_run_found()
        await test_context.async_verify_reaction_event_not_received()
        await test_context.react.runtime.async_shutdown(is_hass_shutdown=True)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_run_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled_restart_force"])
async def test_runtime_restart_mode_force(test_context: TstContext, workflow_name: str):
    await test_context.async_start_react()

    async with test_context.async_listen_reaction_event():
        await test_context.async_send_action_event()
        test_context.verify_run_found()
        await test_context.async_verify_reaction_event_not_received()
        await test_context.react.runtime.async_shutdown(is_hass_shutdown=True)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_run_not_found()
