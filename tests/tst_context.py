from __future__ import annotations

from asyncio import sleep
from contextlib import asynccontextmanager
from types import DynamicClassAttribute
from deepdiff import DeepDiff
from typing import Any, Union
from custom_components.react.lib.config import Reactor, Workflow
from custom_components.react.utils.struct import DynamicData, MultiItem

from homeassistant.components.trace.const import DATA_TRACE
from homeassistant.const import ATTR_ENTITY_ID, ATTR_STATE, STATE_ON
from homeassistant.core import Event, HomeAssistant, State, Context

from unittest.mock import Mock

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    _EMPTY_,
    ATTR_ACTION,
    ATTR_ACTOR,
    ATTR_ACTOR_ACTION,
    ATTR_ACTOR_ENTITY,
    ATTR_ACTOR_ID,
    ATTR_ACTOR_TYPE,
    ATTR_CONDITION,
    ATTR_CONTEXT,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE,
    ATTR_FORWARD_ACTION,
    ATTR_ID,
    ATTR_INDEX,
    ATTR_OVERWRITE,
    ATTR_REACTION_DATETIME,
    ATTR_REACTOR,
    ATTR_REACTOR_ACTION,
    ATTR_REACTOR_ENTITY,
    ATTR_REACTOR_ID,
    ATTR_REACTOR_TYPE,
    ATTR_RESET_WORKFLOW,
    ATTR_TEMPLATE,
    ATTR_THIS,
    ATTR_TIMING,
    ATTR_TRIGGER,
    ATTR_TYPE,
    ATTR_VARIABLES,
    ATTR_WORKFLOW_ID, 
    DOMAIN, 
    EVENT_REACT_ACTION,
    EVENT_REACT_REACTION,
    REACTOR_TIMING_IMMEDIATE,
)
from custom_components.react.utils.trace import ReactTrace

from tests.common import (
    DOMAIN_SENSOR, 
    EVENT_TEST_CALLBACK,
)

ACTOR_ID_PREFIX = "actor_"
ACTOR_ENTITY_PREFIX = "actor_entity_"
ACTOR_TYPE_PREFIX = "actor_type_"
ACTOR_ACTION_PREFIX = "actor_action_"

REACTOR_ID_PREFIX = "reactor_"
REACTOR_ENTITY_PREFIX = "reactor_entity_"
REACTOR_TYPE_PREFIX = "reactor_type_"
REACTOR_ACTION_PREFIX = "reactor_action_"

TRACE_CHANGED_VARIABLES = "changed_variables"
TRACE_CONTEXT = "context"
TRACE_RESULT = "result"
TRACE_PARALLEL = "parallel"
TRACE_PATH = "path"
TRACE_REACTION = "reaction"
TRACE_TRACE = "trace"
TRACE_CONFIG = "config"
TRACE_DOMAIN = "domain"
TRACE_ITEM_ID = "item_id"
TRACE_MESSAGE = "message"

class TstContext():
    
    def __init__(self, hass: HomeAssistant, workflow_name: str) -> None:
        self.hass = hass
        self.react: ReactBase = self.hass.data[DOMAIN]
        self.event_mock = Mock()

        self.workflow_id = f"workflow_{workflow_name}"
        self.workflow_config = self.react.configuration.workflow_config.workflows.get(self.workflow_id)

        self.notifications = list[dict]()
        self.acknowledgements = list[dict]()

    
    async def async_send_action_event(self, 
        entity: str = None, 
        type: str = None, 
        action: str = None, 
        data: dict = None, 
        actor_index: int = 0,
        entity_index: int = 0,
        type_index: int = 0,
        action_index: int = 0,
    ):
        workflow_config_actor = self.workflow_config.actors[actor_index]
        event_data = {
            ATTR_ENTITY: entity or workflow_config_actor.entity[entity_index],
            ATTR_TYPE: type or workflow_config_actor.type[type_index],
            ATTR_ACTION: action or workflow_config_actor.action[action_index],
            ATTR_DATA: data
        }
        self.hass.bus.async_fire(EVENT_REACT_ACTION, event_data)
        await self.hass.async_block_till_done()


    @asynccontextmanager
    async def async_listen_reaction_event(self):
        try:
            self.cancel_listen = self.hass.bus.async_listen(EVENT_REACT_REACTION, self.event_mock)
            yield
        finally:
            if self.cancel_listen:
                self.cancel_listen()


    def retrieve_reaction_entities(self):
        states = [ state for state in self.hass.states.async_all(DOMAIN_SENSOR) if state.entity_id.startswith(f"{DOMAIN_SENSOR}.reaction_") ]
        return states


    def verify_reaction_entity_count(self, expected_count: int = 1):
        reactions = self.retrieve_reaction_entities()
        got_count = len(reactions)
        assert got_count == expected_count, f"Expected reaction entity count {expected_count}, got {got_count}, {reactions[0]}"


    def verify_reaction_entity_not_found(self) -> None:
        self.verify_reaction_entity_count(0)


    def verify_reaction_entity_found(self, expected_count: int = 1) -> None:
        self.verify_reaction_entity_count(expected_count)


    def verify_reaction_entity_data(self, 
        expected_entity: str = None, 
        expected_type: str = None, 
        expected_action: str = None, 
        reactor_index: int = 0,
        entity_index: int = 0,
        type_index: int = 0,
        action_index: int = 0,
    ):
        reaction_entity: State = self.retrieve_reaction_entities()[0]

        workflow_config_reactor = self.workflow_config.reactors[reactor_index]

        self.verify_reaction_entity_data_item(ATTR_ENTITY, reaction_entity, workflow_config_reactor.entity, expected_entity, entity_index)
        self.verify_reaction_entity_data_item(ATTR_TYPE, reaction_entity, workflow_config_reactor.type, expected_type, type_index)
        self.verify_reaction_entity_data_item(ATTR_ACTION, reaction_entity, workflow_config_reactor.action, expected_action, action_index)

    
    def verify_reaction_entity_data_item(self, attr: str, reaction_entity: State, multi_item: MultiItem, expected_value: Any = None, item_index: int = 0):
        got_value = reaction_entity.attributes.get(attr, None)
        expected_value = expected_value or multi_item[item_index]
        assert got_value == expected_value, f"Expected reaction {attr} '{expected_value}', got '{got_value}'"


    def retrieve_reaction_entity_id(self):
        reaction_entity: State = self.retrieve_reaction_entities()[0]
        return reaction_entity.entity_id


    def verify_reaction_internal_data(self, expected_data: dict = None):
        react: ReactBase = self.hass.data[DOMAIN]
        reaction_entity = self.retrieve_reaction_entities()[0]
        reaction_internal = react.reactions.get_by_id(reaction_entity.attributes.get(ATTR_ID))

        data_got = reaction_internal.data.data
        data_expected = expected_data 
        assert data_got == data_expected, f"Expected reaction data '{data_expected}', got '{data_got}'"


    def verify_reaction_event_count(self, expected_count: int = 1):
        got_count = self.event_mock.call_count
        assert got_count == expected_count, f"Expected event count {expected_count}, got {got_count}"


    def verify_reaction_event_not_received(self) -> None:
        self.verify_reaction_event_count(0)


    async def async_verify_reaction_event_received(self, expected_count: int = 1, delay: int = 0) -> None:
        if delay > 0:
            await sleep(delay)
        self.verify_reaction_event_count(expected_count)
        for i,call in enumerate(self.event_mock.mock_calls):
            assert len(call.args) > 0, f"Expected args for call {i}, got none"


    def verify_reaction_event_data(self,
        expected_entity: str = None, 
        expected_type: str = None, 
        expected_action: str = None, 
        expected_data: dict = None, 
        event_index: int = 0,
        reactor_index: int = 0,
        entity_index: int = 0,
        type_index: int = 0,
        action_index: int = 0,
    ):
        event: Event = self.event_mock.mock_calls[event_index].args[0]
        event_type_got = event.event_type
        event_type_expected = EVENT_REACT_REACTION
        assert event_type_got == event_type_expected, f"Expected eventtype '{event_type_expected}', got '{event_type_got}'"

        workflow_config_reactor = self.workflow_config.reactors[reactor_index]

        self.verify_reaction_event_data_item(ATTR_ENTITY, event, workflow_config_reactor.entity, expected_entity, entity_index)
        self.verify_reaction_event_data_item(ATTR_TYPE, event, workflow_config_reactor.type, expected_type, type_index)
        self.verify_reaction_event_data_item(ATTR_ACTION, event, workflow_config_reactor.action, expected_action, action_index)
        self.verify_reaction_event_data_item(ATTR_DATA, event, workflow_config_reactor.data, expected_data, -1)


    def verify_reaction_event_data_item(self, attr: str, event: Event, multi_item_or_list: Union[MultiItem, list], expected_value: Any = None, item_index: int = 0):
        got_value = event.data.get(attr, None)
        expected_value = expected_value or (multi_item_or_list[item_index] if multi_item_or_list else None)
        assert DeepDiff(got_value, expected_value) == {}, f"Expected event entity '{expected_value}', got '{got_value}'"


    def verify_trace_record(self, 
        actor_index: int = 0, 
        actor_entity_index = 0,
        actor_type_index = 0,
        actor_action_index = 0,
        actor_data_index = 0,
        expected_runtime_actor_entity: str = None, 
        expected_runtime_actor_type: str = None, 
        expected_runtime_actor_action: str = None, 
        expected_runtime_actor_data: dict = None,
        expected_runtime_reactor_entity: list[str] = None, 
        expected_runtime_reactor_type: list[str] = None, 
        expected_runtime_reactor_action: list[str] = None, 
        expected_runtime_reactor_data: dict = None,
        expected_result_message: str = None,
        expected_actor_condition_result: bool = True,
        expected_reactor_condition_results: list[bool] = None
    ):

        # Initialize expectation lists
        if not expected_reactor_condition_results:
            expected_reactor_condition_results = [True] * len(self.workflow_config.reactors)
        if not expected_runtime_reactor_entity:
            expected_runtime_reactor_entity = [None] * len(self.workflow_config.reactors)
        if not expected_runtime_reactor_type:
            expected_runtime_reactor_type = [None] * len(self.workflow_config.reactors)
        if not expected_runtime_reactor_action:
            expected_runtime_reactor_action = [None] * len(self.workflow_config.reactors)

        trace_data: dict = self.hass.data[DATA_TRACE]
        key = f"{DOMAIN}.{self.workflow_id}"
        test_traces: dict = assert_dict_property_value_not_none(trace_data, key)
        test_trace: ReactTrace = list(test_traces.values())[0]

        trace = TracePath(test_trace.as_extended_dict(), TRACE_TRACE)

        trace.assert_property_match(TRACE_DOMAIN, DOMAIN)
        trace.assert_property_match(TRACE_ITEM_ID, self.workflow_id)
        
        ########## Trace config ##########

        trace_config = trace.assert_property_not_none(TRACE_CONFIG)
        trace_config.assert_property_match(ATTR_ID, self.workflow_id)
        
        # Test for actor configuration in trace data
        for i in range(0, len(self.workflow_config.actors)):
            workflow_config_actor = self.workflow_config.actors[i]
            trace_config_actor = trace_config.assert_property_list_item(ATTR_ACTOR, i)
            trace_config_actor.assert_property_match(ATTR_INDEX, i)
            trace_config_trigger = trace_config_actor.assert_property_not_none(ATTR_TRIGGER)
            trace_config_trigger.assert_property_match(ATTR_ID, workflow_config_actor.id)
            if workflow_config_actor.entity:
                trace_config_trigger.assert_property_match(ATTR_ENTITY, workflow_config_actor.entity)
            if workflow_config_actor.type:
                trace_config_trigger.assert_property_match(ATTR_TYPE, workflow_config_actor.type)
            if workflow_config_actor.action:
                trace_config_trigger.assert_property_match(ATTR_ACTION, workflow_config_actor.action)
            if workflow_config_actor.data:
                trace_config_trigger.assert_property_match(ATTR_DATA, workflow_config_actor.data)
            if workflow_config_actor.condition:
                trace_config_actor_condition = trace_config_actor.assert_property_not_none(ATTR_CONDITION)
                trace_config_actor_condition.assert_property_match(ATTR_TEMPLATE, workflow_config_actor.condition)

        # Test for reactor configuration in trace data
        for i in range(0, len(self.workflow_config.reactors)):
            workflow_config_reactor = self.workflow_config.reactors[i]
            trace_config_reactor = trace_config.assert_property_list_item(ATTR_REACTOR, i)
            trace_config_reactor.assert_property_match(ATTR_INDEX, i)
            trace_config_event = trace_config_reactor.assert_property_not_none(ATTR_EVENT)
            trace_config_event.assert_property_match(ATTR_ID, workflow_config_reactor.id)
            trace_config_event.assert_property_match(ATTR_TIMING, workflow_config_reactor.timing)
            trace_config_event.assert_property_match(ATTR_DATA, workflow_config_reactor.data)
            if workflow_config_reactor.reset_workflow:
                trace_config_event.assert_property_match(ATTR_RESET_WORKFLOW, workflow_config_reactor.reset_workflow)
            else:
                trace_config_event.assert_property_match(ATTR_ENTITY, workflow_config_reactor.entity[0])
                trace_config_event.assert_property_match(ATTR_TYPE, workflow_config_reactor.type[0])
                if not workflow_config_reactor.forward_action:
                    trace_config_event.assert_property_match(ATTR_ACTION, workflow_config_reactor.action[0])

        ########## Trace data ##########

        # Test for actor data and vars in trace data
        trace_trace = trace.assert_property_not_none(TRACE_TRACE)
        workflow_config_actor = self.workflow_config.actors[actor_index]

        trace_trace_actor_path = f"{ATTR_ACTOR}/{actor_index}/{ATTR_TRIGGER}"
        trace_trace_actor = trace_trace.assert_property_list_item(trace_trace_actor_path)
        trace_trace_actor.assert_property_match(TRACE_PATH, trace_trace_actor_path)

        trace_trace_actor_vars = trace_trace_actor.assert_property_not_none(TRACE_CHANGED_VARIABLES)
        
        trace_trace_actor_vars_this = trace_trace_actor_vars.assert_property_not_none(ATTR_THIS)
        trace_trace_actor_vars_this.assert_property_match(ATTR_ENTITY_ID, key)
        trace_trace_actor_vars_this.assert_property_match(ATTR_STATE, STATE_ON)

        # Test for actor variables in trace data
        trace_trace_actor_vars_variables = trace_trace_actor_vars.assert_property_not_none(ATTR_VARIABLES)
        trace_trace_actor_vars_variables_actor = trace_trace_actor_vars_variables.assert_property_not_none(ATTR_ACTOR)
        trace_trace_actor_vars_variables_actor.assert_property_match(ATTR_ID, workflow_config_actor.id)
        trace_trace_actor_vars_variables_event = trace_trace_actor_vars_variables.assert_property_not_none(ATTR_EVENT)
        if workflow_config_actor.entity:
            trace_trace_actor_vars_variables_event.assert_property_match(ATTR_ENTITY, expected_runtime_actor_entity or workflow_config_actor.entity[actor_entity_index])
        if workflow_config_actor.type:
            trace_trace_actor_vars_variables_event.assert_property_match(ATTR_TYPE, expected_runtime_actor_type or workflow_config_actor.type[actor_type_index])
        if workflow_config_actor.action:
            trace_trace_actor_vars_variables_event.assert_property_match(ATTR_ACTION, expected_runtime_actor_action or workflow_config_actor.action[actor_action_index])
        if workflow_config_actor.data:
            trace_trace_actor_vars_variables_event.assert_property_match(ATTR_DATA, expected_runtime_actor_data or workflow_config_actor.data[actor_data_index])
        

        trace_trace_actor_vars_actor = trace_trace_actor_vars.assert_property_not_none(ATTR_ACTOR)
        trace_trace_actor_vars_actor.assert_property_match(ATTR_ID, workflow_config_actor.id)

        # Test for actor condition in trace data
        if workflow_config_actor.condition:
            trace_trace_actor_condition_path = f"{ATTR_ACTOR}/{actor_index}/{ATTR_CONDITION}"
            trace_trace_actor_condition = trace_trace.assert_property_list_item(trace_trace_actor_condition_path)
            trace_trace_actor_condition.assert_property_match(TRACE_PATH, trace_trace_actor_condition_path)
            trace_trace_actor_condition_result = trace_trace_actor_condition.assert_property_not_none(TRACE_RESULT)
            trace_trace_actor_condition_result.assert_property_match(TRACE_RESULT, expected_actor_condition_result)
        
        # Skip reaction traces if actor condition was false
        if not expected_actor_condition_result: return

        # Test for parallel in trace data if multiple reactors configured
        multiple_reactors = len(self.workflow_config.reactors) > 1

        if multiple_reactors:
            trace_trace_parallel_path = TRACE_PARALLEL
            trace_trace_parallel = trace_trace.assert_property_list_item(trace_trace_parallel_path)
            trace_trace_parallel.assert_property_match(TRACE_PATH, trace_trace_parallel_path)
            trace_trace_parallel_variables = trace_trace_parallel.assert_property_not_none(TRACE_CHANGED_VARIABLES)
            trace_trace_parallel_variables.assert_property_not_none(TRACE_CONTEXT)

        # Test for reactor data in trace data
        for i in range(0, len(self.workflow_config.reactors)):
            workflow_config_reactor = self.workflow_config.reactors[i]

            if workflow_config_reactor.condition:
                # Test for reactor condition in trace data
                trace_trace_reactor_condition_path = f"{ATTR_REACTOR}/{i}/{ATTR_CONDITION}"
                trace_trace_reactor_condition = trace_trace.assert_property_list_item(trace_trace_reactor_condition_path)
                trace_trace_reactor_condition.assert_property_match(TRACE_PATH, trace_trace_reactor_condition_path)
                trace_trace_reactor_condition_result = trace_trace_reactor_condition.assert_property_not_none(TRACE_RESULT)
                trace_trace_reactor_condition_result.assert_property_match(TRACE_RESULT, expected_reactor_condition_results[i])
                
                # if there's one reactor with a condition the condition contains changed variables, test it
                if not multiple_reactors:
                    trace_trace_reactor_condition_variables = trace_trace_reactor_condition.assert_property_not_none(TRACE_CHANGED_VARIABLES)
                    trace_trace_reactor_condition_variables.assert_property_not_none(TRACE_CONTEXT)
            
            # If the reactor condition is false skip remaining reactor trace tests for this reactor as there is no trace data for it
            if not expected_reactor_condition_results[i]: continue

            trace_trace_reactor_path = f"{ATTR_REACTOR}/{i}/{ATTR_EVENT}"
            trace_trace_reactor = trace_trace.assert_property_list_item(trace_trace_reactor_path)
            trace_trace_reactor.assert_property_match(TRACE_PATH, trace_trace_reactor_path)

            trace_trace_reactor_result = trace_trace_reactor.assert_property_not_none(TRACE_RESULT)
            
            if expected_result_message:
                # Test for message result in trace data
                trace_trace_reactor_result.assert_property_match(TRACE_MESSAGE, expected_result_message)
            else:
                # test for reaction result in trace data
                trace_trace_reactor_result_reaction = trace_trace_reactor_result.assert_property_not_none(TRACE_REACTION)
                trace_trace_reactor_result_reaction.assert_property_not_none(ATTR_ID)
                if workflow_config_reactor.timing != REACTOR_TIMING_IMMEDIATE:
                    trace_trace_reactor_result_reaction.assert_property_not_none(ATTR_REACTION_DATETIME)
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_WORKFLOW_ID, self.workflow_id)
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_ACTOR_ID, workflow_config_actor.id)
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_ACTOR_ENTITY, expected_runtime_actor_entity or workflow_config_actor.entity[actor_entity_index])
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_ACTOR_TYPE, expected_runtime_actor_type or workflow_config_actor.type[actor_type_index])
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_ACTOR_ACTION, expected_runtime_actor_action or workflow_config_actor.action[actor_action_index])
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_REACTOR_ID, workflow_config_reactor.id)
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_REACTOR_ENTITY, expected_runtime_reactor_entity[i] or (_EMPTY_ if workflow_config_reactor.reset_workflow else workflow_config_reactor.entity[0]))
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_REACTOR_TYPE, expected_runtime_reactor_type[i] or (_EMPTY_ if workflow_config_reactor.reset_workflow else workflow_config_reactor.type[0]))
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_REACTOR_ACTION, expected_runtime_reactor_action[i] or (_EMPTY_ if workflow_config_reactor.reset_workflow else expected_runtime_actor_action if workflow_config_reactor.forward_action else workflow_config_reactor.action[0]))
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_DATA, expected_runtime_reactor_data or (None if workflow_config_reactor.reset_workflow else workflow_config_reactor.data[0] if workflow_config_reactor.data else None))
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_RESET_WORKFLOW, workflow_config_reactor.reset_workflow)
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_OVERWRITE, workflow_config_reactor.overwrite)
                trace_trace_reactor_result_reaction.assert_property_match(ATTR_FORWARD_ACTION, workflow_config_reactor.forward_action)

            # Test for variables in event section of trace data if only 1 reactor configured without condition
            if len(self.workflow_config.reactors) == 1 and not workflow_config_reactor.condition:
                trace_trace_reactor_variables = trace_trace_reactor.assert_property_not_none(TRACE_CHANGED_VARIABLES)
                trace_trace_reactor_variables.assert_property_not_none(TRACE_CONTEXT)
            

    async def async_send_notify_feedback_event(self, send_workflow: Workflow, send_reactor_index: int = 0, send_reactor_data_index: int = 0, send_feedback_item_index: int = 0):
        send_workflow_config_reactor = send_workflow.reactors[send_reactor_index]

        send_workflow_config_reactor_data = send_workflow_config_reactor.data[send_reactor_data_index].as_dict()
        send_feedback_items: list[dict] = send_workflow_config_reactor_data.get(ATTR_EVENT_FEEDBACK_ITEMS)
        send_feedback_item = send_feedback_items[send_feedback_item_index]

        event_data = {
            ATTR_ENTITY: send_workflow_config_reactor.entity[0],
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: send_feedback_item.get(ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK),
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: send_feedback_item.get(ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,)
        }
        self.hass.bus.async_fire(EVENT_TEST_CALLBACK, event_data)
        await self.hass.async_block_till_done()


    def send_notification(self, entity: str, notification_data: dict, context: Context):
        self.notifications.append({
            ATTR_ENTITY: entity,
            ATTR_DATA: notification_data,
            ATTR_CONTEXT: context
        })


    def acknowledge_feedback(self, feedback_data: dict):
        self.acknowledgements.append({
            ATTR_ENTITY: feedback_data.get(ATTR_ENTITY, None),
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: feedback_data.get(ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, None),
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: feedback_data.get(ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, None),
        })


    def verify_notification_sent(self, expected_count: int = 1):
        got_count = len(self.notifications)
        assert got_count == expected_count, f"Expected notification count {expected_count}, got {got_count}"


    def verify_acknowledgement_sent(self, expected_count: int = 1):
        got_count = len(self.acknowledgements)
        assert got_count == expected_count, f"Expected acknowledgement count {expected_count}, got {got_count}"


    def verify_notification_data(self, notification_index: int = 0, reactor_index: int = 0, reactor_data_index: int = 0):
        notification = self.notifications[0]
        notification_data = notification.get(ATTR_DATA, None)

        workflow_config_reactor = self.workflow_config.reactors[reactor_index]
        workflow_config_reactor_data = workflow_config_reactor.data[reactor_data_index].as_dict()

        self.assert_attribute(ATTR_ENTITY, workflow_config_reactor, notification)
        self.assert_attribute(ATTR_EVENT_MESSAGE, workflow_config_reactor_data, notification_data)
        self.assert_attribute(ATTR_EVENT_FEEDBACK_ITEMS, workflow_config_reactor_data, notification_data)


    def verify_acknowledgement_data(self, send_workflow: Workflow, send_reactor_index: int = 0, send_reactor_data_index: int = 0, send_feedback_item_index: int = 0, acknowledgement_index: int = 0):
        acknowledgement = self.acknowledgements[acknowledgement_index]

        send_workflow_config_reactor = send_workflow.reactors[send_reactor_index]
        send_workflow_config_reactor_data = send_workflow_config_reactor.data[send_reactor_data_index].as_dict()
        send_feedback_items: list[dict] = send_workflow_config_reactor_data.get(ATTR_EVENT_FEEDBACK_ITEMS)
        send_feedback_item = send_feedback_items[send_feedback_item_index]

        self.assert_attribute(ATTR_ENTITY, send_workflow_config_reactor, acknowledgement)
        self.assert_attribute(ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, send_feedback_item, acknowledgement)
        self.assert_attribute(ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, send_feedback_item, acknowledgement)


    def assert_attribute(self, attr: str, expected: dict, got: dict):    
        value_expected = expected.get(attr, None)
        if isinstance(value_expected, MultiItem) and len(value_expected) == 1:
            value_expected = value_expected.first
        value_got = got.get(attr, None)
        assert value_got == value_expected, f"Expected notification value '{value_expected}', got '{value_got}'"


class TracePath():
    def __init__(self, owner: dict, path: str, parent: str = None) -> None:
        self.owner = owner
        self.path = path
        self.parent = parent
    
    
    def assert_property_match(self, key: str, value_expected: Any, name: str = None):
        value_got = self.owner.get(key, None)
        if isinstance(value_got, DynamicData):
            value_got = value_got.as_dict()
        match = False
        used_value_expected = value_expected
        if isinstance(value_expected, str) and isinstance(value_got, MultiItem):
            match = used_value_expected == value_got.first and len(value_got) == 1
        elif isinstance(value_expected, MultiItem) and isinstance(value_got, str):
            used_value_expected = value_expected.first
            match = used_value_expected == value_got and len(value_expected) == 1
        elif isinstance(value_expected, list) and isinstance(value_got, dict):
            used_value_expected = value_expected[0]
            if isinstance(used_value_expected, DynamicData):
                used_value_expected = used_value_expected.as_dict()
            match = DeepDiff(used_value_expected, value_got) == {} and len(value_expected) == 1
        elif isinstance(value_expected, list) and isinstance(value_got, list):
            used_value_expected = [ x.as_dict() if isinstance(x, DynamicData) else x for x in value_expected ]
            match = DeepDiff(used_value_expected, value_got) == {}
        else:
            if isinstance(used_value_expected, DynamicData):
                used_value_expected = used_value_expected.as_dict()
            match = DeepDiff(used_value_expected, value_got) == {}
        assert match, self.assert_message_match(key, name, used_value_expected, value_got)

    
    def assert_property_not_none(self, key: str, name: str = None) -> TracePath:
        value_got = self._assert_property_not_none_bare(key, name)
        return self.child_path(value_got, key)


    def _assert_property_not_none_bare(self, key: str, name: str = None) -> Any:
        value_got = self.owner.get(key, None)
        assert value_got, self.assert_message_not_none(key, name)
        return value_got


    def assert_property_list_item(self, key: str, index: int = 0, name: str = None) -> TracePath:
        item_list: list = self._assert_property_not_none_bare(key, name)
        assert len(item_list) > index, self.assert_message_list_item(key, name, index+1, item_list)
        return self.child_path(item_list[index], f"{key}[{index}]")


    def child_path(self, owner: dict, child_path: str) -> TracePath:
        return TracePath(owner, child_path, self.path)
    

    @property
    def full_path(self):
        if self.parent:
            return f"{self.parent}.{self.path}"
        return self.path


    def full_property(self, key: str, name: str):
        return f"{self.full_path}.{name if name else key}"


    def assert_message_match(self, key: str, name: str, value_expected: Any, value_got: Any):
        return f"Expected {self.full_property(key, name)} '{value_expected}', got '{value_got}'"


    def assert_message_not_none(self, key: str, name: str):
        return f"Expected a value for {self.full_property(key, name)}, got none"

    
    def assert_message_list_item(self, key: str, name: str, count: int, item_list: list):
        f"Expected {count} items in list {self.full_property(key, name)}, got {len(item_list)}"


def assert_dict_property_value_not_none(owner: dict, key: str, name: str = None) -> Any:
    value_got = owner.get(key, None)
    assert value_got, f"Expected a value for {name if name else key}, got none"
    return value_got