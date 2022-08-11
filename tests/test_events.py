import pytest

from homeassistant.core import HomeAssistant

from custom_components.react.const import DOMAIN
from custom_components.react.base import ReactBase

from tests.tst_context import TstContext

FIXTURE_TEST_NAME = "test_name"
FIXTURE_ADDITIONAL_TESTS = "additional_tests"

@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["immediate"])
async def test_react_immediate(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with immediate reactor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["delayed"])
async def test_react_delayed(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with delayed reactor:
    - An event should not be sent immediately
    - A reaction entity should be created
    - Reaction entity data should match configuration
    - An event should be sent after a configured delay
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_event_not_received()
        tc.verify_reaction_entity_found()
        tc.verify_reaction_entity_data()
        await tc.async_verify_reaction_event_received(delay=6)
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["scheduled"])
async def test_react_scheduled(hass: HomeAssistant, test_name, react_component):
    """ 
    Test for workflow with scheduled reactor:
    - An event should not be sent immediately
    - A reaction entity should be created
    - Reaction entity data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_event_not_received()
        tc.verify_reaction_entity_found()
        tc.verify_reaction_entity_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["reset"])
async def test_react_reset(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with reset reactor:
    - Reactions should be found before sending reset event
    - No reactions should be found after sending reset event
    - Trace data should match configuration
    """
    
    await react_component.async_setup(test_name, ["delayed", "scheduled"])

    tc = TstContext(hass, test_name)
    tc_delayed = TstContext(hass, "delayed")
    tc_scheduled = TstContext(hass, "scheduled")

    async with tc_delayed.async_listen_reaction_event():
        await tc_delayed.async_send_action_event()
    async with tc_scheduled.async_listen_reaction_event():
        await tc_scheduled.async_send_action_event()

    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_found(2)
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["forward_action"])
async def test_react_forward_action_no_toggle(hass: HomeAssistant, test_name, react_component):
    """ 
    Test for workflow with reactor with forwardaction and not event action 'toggle':
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration and forwarded action
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(action="test")
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_action="test")
        tc.verify_trace_record(expected_runtime_actor_action="test")


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["forward_action"])
async def test_react_forward_action_toggle(hass: HomeAssistant, test_name, react_component):
    """ 
    Test for workflow with reactor with forwardaction and event action 'toggle':
    - No reaction entity should be created
    - No event should be sent
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(action="toggle")
        tc.verify_reaction_entity_not_found()
        tc.verify_reaction_event_not_received()
        tc.verify_trace_record(expected_result_message="Skipped, toggle with forward-action")


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["multiple_actor"])
async def test_react_multiple_actor_1(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with multiple actors using first actor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["multiple_actor"])
async def test_react_multiple_actor_2(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with multiple actors using second actor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(actor_index=1)
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record(actor_index=1)


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["data"])
async def test_react_data_no_event_1(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with actor data where action has no data:
    - No reaction entity should be found
    - No Event should be received
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        tc.verify_reaction_event_not_received()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["data"])
async def test_react_data_no_event_2(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with actor data where action data does not match actor data:
    - No reaction entity should be found
    - No Event should be received
    """

    await react_component.async_setup(test_name)
    
    tc = TstContext(hass, test_name)
    data_in: dict = {"actor_data_data" : 4}
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(data=data_in)
        tc.verify_reaction_entity_not_found()
        tc.verify_reaction_event_not_received()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["data"])
async def test_react_data_event(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with actor data where action data does match actor data:
    - No reaction entity should be found
    - An event should be received
    - Event data should match configuration and contain configured reactor data
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)
    
    tc = TstContext(hass, test_name)
    data_in: dict = {"actor_data_data" : 3}
    data_out: dict = {
        "data1": 1,
        "data2": tc.workflow_config.actors[0].action.first,
        "data3": 3,
        "data4": ["asdf", "qwer"]
    }
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(data=data_in)
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_data=data_out)
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["data_delayed"])
async def test_react_data_delayed_event(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with delayed reactor with data:
    - No event should be sent
    - A reaction entity should be found
    - Reaction entity data should match configuration
    - Internal reaction data should match configured reactor data
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)
    
    tc = TstContext(hass, test_name)
    data_out: dict = {
        "data1": 1,
        "data2": True,
    }
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_event_not_received
        tc.verify_reaction_entity_found()
        tc.verify_reaction_entity_data()
        tc.verify_reaction_internal_data(expected_data=data_out)
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["multiple_reactor"])
async def test_react_multiple_reactor(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with multiple reactors:
    - No reaction entities should be created
    - An event should be sent for each reactor (2)
    - Event data should match configuration for each reactor (2)
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_reaction_event_data(event_index=0, reactor_index=0)
        tc.verify_reaction_event_data(event_index=1, reactor_index=1)
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["full_stencil"])
async def test_react_full_stencil(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with full stencil:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    data_out: dict = {
        "test": 37
    }
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_data=data_out)
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["partial_stencil"])
async def test_react_partial_stencil(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with partial stencil:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["templated"])
async def test_react_templated(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with templates:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(entity="actor_entity_templated", type="actor_type_templated", action="actor_action_templated")
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_entity="reactor_entity_templated", expected_type="reactor_type_templated", expected_action="reactor_action_templated")
        tc.verify_trace_record(
            expected_runtime_actor_entity="actor_entity_templated",
            expected_runtime_actor_type="actor_type_templated",
            expected_runtime_actor_action="actor_action_templated",
            expected_runtime_reactor_entity=["reactor_entity_templated"],
            expected_runtime_reactor_type=["reactor_type_templated"],
            expected_runtime_reactor_action=["reactor_action_templated"],
        )


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["templated_state"])
async def test_react_templated_state(hass: HomeAssistant, test_name, template_component, react_component, input_text_component):
    """
    Test for workflow with templates containing state references
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(test_name)
    await input_text_component.async_set_value("test_text", "templated_state")
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(entity="actor_entity_templated_state", type="actor_type_templated_state", action="actor_action_templated_state")
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_entity="reactor_entity_templated_state", expected_type="reactor_type_templated_state", expected_action="reactor_action_templated_state")
        tc.verify_trace_record(
            expected_runtime_actor_entity="actor_entity_templated_state",
            expected_runtime_actor_type="actor_type_templated_state",
            expected_runtime_actor_action="actor_action_templated_state",
            expected_runtime_reactor_entity=["reactor_entity_templated_state"],
            expected_runtime_reactor_type=["reactor_type_templated_state"],
            expected_runtime_reactor_action=["reactor_action_templated_state"],
        )


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["multiple_entities"])
async def test_react_multiple_entities_1(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with an actor containing multiple entities
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["multiple_entities"])
async def test_react_multiple_entities_2(hass: HomeAssistant, test_name, react_component):
    """
    Test for workflow with an actor containing multiple entities
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(entity_index=1)
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record(actor_entity_index=1)


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["actor_condition"])
async def test_react_actor_condition_true(hass: HomeAssistant, test_name, react_component, template_component, input_boolean_component):
    """
    Test for workflow with an actor with a condition that evaluates to 'true'
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(test_name)
    await input_boolean_component.async_turn_on("test_boolean")
    await hass.async_block_till_done()

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["actor_condition"])
async def test_react_actor_condition_false(hass: HomeAssistant, test_name, react_component, template_component, input_boolean_component):
    """
    Test for workflow with an actor with a condition that evaluates to 'false'
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(test_name)
    await input_boolean_component.async_turn_off("test_boolean")
    await hass.async_block_till_done()

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        tc.verify_reaction_event_not_received()
        tc.verify_trace_record(expected_actor_condition_result=False)


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["trace"])
async def test_react_trace_switched_off_actor_1(hass: HomeAssistant, test_name, react_component, input_boolean_component):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_boolean is turned off:
    - No reaction entity should be created
    - One event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)
    await input_boolean_component.async_turn_off("test_boolean")
    await hass.async_block_till_done()
    
    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(reactor_index=1)
        tc.verify_trace_record(
            expected_reactor_condition_results=[False, True]
        )


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["trace"])
async def test_react_trace_switched_on_actor_1(hass: HomeAssistant, test_name, react_component, input_boolean_component):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_boolean is turned off:
    - No reaction entity should be created
    - No events should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)
    await input_boolean_component.async_turn_on("test_boolean")
    await hass.async_block_till_done()

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        tc.verify_reaction_event_not_received()
        tc.verify_trace_record(
            expected_actor_condition_result=False
        )



@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["trace"])
async def test_react_trace_switched_off_actor_2(hass: HomeAssistant, test_name, react_component, input_boolean_component):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_boolean is turned off:
    - No reaction entity should be created
    - One event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)
    await input_boolean_component.async_turn_off("test_boolean")
    await hass.async_block_till_done()
    
    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(actor_index=1)
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(reactor_index=1)
        tc.verify_trace_record(
            actor_index=1,
            expected_reactor_condition_results=[False, True]
        )


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["trace"])
async def test_react_trace_switched_on_actor_2(hass: HomeAssistant, test_name, react_component, input_boolean_component):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_boolean is turned off:
    - No reaction entity should be created
    - No events should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)
    await input_boolean_component.async_turn_on("test_boolean")
    await hass.async_block_till_done()

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event(actor_index=1)
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_reaction_event_data(event_index=0, reactor_index=0)
        tc.verify_reaction_event_data(event_index=1, reactor_index=1)
        tc.verify_trace_record(
            actor_index=1,
            expected_reactor_condition_results=[True, True]
        )


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["reactor_condition"])
async def test_react_reactor_condition_false(hass: HomeAssistant, test_name, react_component, input_boolean_component):
    """
    Test for workflow with a reactor with a condition that is false:
    - No reaction entity should be created
    - No event should be sent
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)
    await input_boolean_component.async_turn_off("test_boolean")
    await hass.async_block_till_done()

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        tc.verify_reaction_event_not_received()
        tc.verify_trace_record(
            expected_reactor_condition_results=[False]
        )


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["reactor_condition"])
async def test_react_reactor_condition_true(hass: HomeAssistant, test_name, react_component, input_boolean_component):
    """
    Test for workflow with a reactor with a condition that is false:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(test_name)
    await input_boolean_component.async_turn_on("test_boolean")
    await hass.async_block_till_done()

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["binary_sensor"])
async def test_react_binary_sensor(hass: HomeAssistant, test_name, react_component, input_boolean_component, template_component):
    """
    Test for workflow for a binary_sensor:
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await input_boolean_component.async_turn_on("test_boolean")
        await hass.async_block_till_done()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["group"])
async def test_react_group(hass: HomeAssistant, test_name, react_component, template_component, group_component, input_boolean_component):
    """
    Test for workflow for a group:
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await input_boolean_component.async_turn_on("test_boolean")
        await hass.async_block_till_done()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["device_tracker"])
async def test_react_device_tracker(hass: HomeAssistant, test_name, react_component, device_tracker_component):
    """
    Test for workflow for a device_tracker:
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await device_tracker_component.async_see("test_device_tracker", "not_home")
        await device_tracker_component.async_see("test_device_tracker", "home")
        await hass.async_block_till_done()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

    await hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["person"])
async def test_react_person(hass: HomeAssistant, test_name, react_component, device_tracker_component, person_component):
    """
    Test for workflow for a person:
    """

    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await device_tracker_component.async_see("test_device_tracker", "home")
        await device_tracker_component.async_see("test_device_tracker", "not_home")
        await hass.async_block_till_done()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

    await hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["actionable_notification"])
async def test_react_actionable_notification(hass: HomeAssistant, test_name, react_component):
    """
    Test for actionable notifications
    """

    await react_component.async_setup(test_name, init_notify_plugin=True)
    react: ReactBase = hass.data[DOMAIN]
    notify_plugin = react.plugin_factory.get_notify_plugin()
    
    tc = TstContext(hass, test_name)
    notify_plugin.hook_test(tc)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await tc.async_send_action_event()
        tc.verify_notification_send()