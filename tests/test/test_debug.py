# from asyncio import sleep
# import pytest

# from homeassistant.core import HomeAssistant

# from tests.tst_context import TstContext
# from tests.common import FIXTURE_WORKFLOW_NAME

# FIXTURE_ADDITIONAL_TESTS = "additional_tests"


# @pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["debug"])
# async def test_react_immediate(hass: HomeAssistant, workflow_name, react_component):
#     await react_component.async_setup(workflow_name)

#     # tc = TstContext(hass, workflow_name)
#     # async with tc.async_listen_reaction_event():
#     #     tc.verify_reaction_not_found()
#     #     await tc.async_send_action_event()
#     #     tc.verify_reaction_not_found()
#     #     await tc.async_verify_reaction_event_received()
#     #     tc.verify_reaction_event_data()
#     #     tc.verify_trace_record()