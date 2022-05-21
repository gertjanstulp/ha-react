from __future__ import annotations
import asyncio
from contextlib import contextmanager, suppress
from copy import copy
from dataclasses import dataclass

from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Iterator, Tuple, Union
from homeassistant.core import Context, Event, callback
from homeassistant.helpers.condition import condition_trace_append
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers.template import Template, is_template_string
from homeassistant.helpers.trace import trace_get, trace_path, trace_set_result, trace_path_stack_cv
from homeassistant.util import ulid as ulid_util
from homeassistant.util.dt import utcnow

from .config import Actor, Reactor, Workflow, calculate_reaction_datetime
from ..base import ReactBase
from ..reactions.base import ReactReaction
from ..utils.updatable import Updatable
from ..utils.logger import format_data
from ..utils.template import TemplateJitter, TemplateTracker, ValueJitter
from ..utils.trace import ReactTrace, trace_node, trace_workflow

if TYPE_CHECKING:
    from .. import WorkflowEntity

from ..const import (
    ACTION_TOGGLE,
    ATTR_ACTION,
    ATTR_ACTOR,
    ATTR_ACTOR_ACTION,
    ATTR_ACTOR_ENTITY,
    ATTR_ACTOR_ID,
    ATTR_ACTOR_TYPE,
    ATTR_CONDITION,
    ATTR_CONTEXT,
    ATTR_DATA,
    ATTR_DELAY,
    ATTR_ENTITY,
    ATTR_RESET_WORKFLOW,
    ATTR_THIS,
    ATTR_TYPE,
    ATTR_VARIABLES,
    ATTR_WORKFLOW_ID,
    PROP_TYPE_DEFAULT,
    PROP_TYPE_TEMPLATE,
    PROP_TYPE_VALUE,
    EVENT_REACT_ACTION,
    PROP_ATTR_TYPE_POSTFIX,
    PROP_TYPE_BOOL,
    PROP_TYPE_INT,
    PROP_TYPE_SOURCE,
    PROP_TYPE_STR,
    SIGNAL_DISPATCH,
    SIGNAL_PROPERTY_COMPLETE,
    SIGNAL_REACT,
    TRACE_PATH_ACTOR,
    TRACE_PATH_CONDITION,
    TRACE_PATH_EVENT,
    TRACE_PATH_PARALLEL,
    TRACE_PATH_REACTOR,
    TRACE_PATH_TRIGGER
)

_JITTER_PROPERTY = "{}_jitter"

 
def extract_action_event_data(event: Event) -> Tuple[str, str, str]:
    entity = event.data.get(ATTR_ENTITY, None)
    type = event.data.get(ATTR_TYPE, None)
    action = event.data.get(ATTR_ACTION, None)
    return entity, type, action


class WorkflowState:
    def __init__(self, workflow_entity: WorkflowEntity) -> None:
        self.workflow_entity = workflow_entity


    @callback
    def async_set_context(self, context: Context) -> None:
        self.workflow_entity.async_set_context(context)


class VariableHandler(Updatable):
    def __init__(self, react: ReactBase, workflow: Workflow) -> None:
        super().__init__(react)
        self.variable_trackers: list[TemplateTracker] = []
        self.names = workflow.variables.names
        self.variable_container = type('object', (), {})()
        actor_container = {
            ATTR_ENTITY: None,
            ATTR_TYPE: None,
            ATTR_ACTION: None,
        }
        setattr(self.variable_container, ATTR_ACTOR, actor_container)

        def init_attr(attr: str, type_converter: Any, default: Any = None):
            type_prop = f"_{attr}{PROP_ATTR_TYPE_POSTFIX}"
            attr_value = getattr(workflow.variables, attr, None)

            def set_attr(attr: str, value: Any, prop_type):
                setattr(self.variable_container, attr, value)
                setattr(self.variable_container, type_prop, prop_type)

            if attr_value:
                if isinstance(attr_value, str) and is_template_string(attr_value):
                    set_attr(attr, None, PROP_TYPE_TEMPLATE)
                    self.variable_trackers.append(TemplateTracker(react, self, attr, Template(attr_value), type_converter))
                else:
                    set_attr(attr, attr_value, PROP_TYPE_VALUE)
            else:
                set_attr(attr, default, PROP_TYPE_DEFAULT)

        for name in self.names:
            init_attr(name, PROP_TYPE_STR)

        for tracker in self.variable_trackers:
            tracker.start()


    def to_dict(self, actor_data: dict = None) -> dict:
        result = vars(self.variable_container)
        if actor_data:
            result[ATTR_ACTOR][ATTR_ENTITY] = actor_data.get(ATTR_ENTITY, None)
            result[ATTR_ACTOR][ATTR_TYPE] = actor_data.get(ATTR_TYPE, None)
            result[ATTR_ACTOR][ATTR_ACTION] = actor_data.get(ATTR_ACTION, None)
        return result


    def as_dict(self) -> dict:
        return { name : getattr(self.variable_container, name, None) for name in self.names }

    
    def destroy(self):
        super().destroy()
        for tracker in self.variable_trackers:
            tracker.destroy()


class RuntimeHandler():
    def start(self):
        pass
    
    def stop(self):
        pass

    def destroy(self):
        pass


class ConditionHandler():
    def __init__(self, owner: Any, value_getter: Callable[[dict], bool]):
        self.owner = owner
        self.condition_type = getattr(owner, f"_{ATTR_CONDITION}{PROP_ATTR_TYPE_POSTFIX}", None)
        self.value_getter = value_getter
        
    def eval(self, variables: dict):
        result = self.value_getter(variables)
        if self.condition_type == PROP_TYPE_TEMPLATE:
            with trace_node(variables):
                trace_set_result(result=result)

        return result


@dataclass
class ActionContext():
    condition: Union[bool, None] = True
    condition_type: Union[str, None] = None
    index: Union[int, None] = None
    actor_id: Union[str, None] = None
     

class ActionHandler(RuntimeHandler):
    entity: Union[str, None] = None
    type: Union[str, None] = None
    action: Union[str, None] = None
    condition: Union[bool, None] = True
    
    def __init__(self, runtime: WorkflowRuntime, actor: Actor, index: int, variable_handler: VariableHandler):
        self.runtime = runtime
        self.actor = actor
        self.index = index
        self.complete = False
        self.enabled = False

        self.template_trackers: list[TemplateTracker] = []
        def init_attr(attr: str, type_converter: Any, default: Any = None):
            type_prop = f"_{attr}{PROP_ATTR_TYPE_POSTFIX}"
            attr_value = getattr(actor, attr, None)

            def set_attr(attr: str, value: Any, prop_type):
                self.set_property(attr, value)
                setattr(self, type_prop, prop_type)

            if attr_value:
                if isinstance(attr_value, str) and is_template_string(attr_value):
                    set_attr(attr, None, PROP_TYPE_TEMPLATE)
                    self.template_trackers.append(TemplateTracker(self.runtime.react, self, attr, Template(attr_value), type_converter, variable_handler.to_dict()))
                else:
                    set_attr(attr, attr_value, PROP_TYPE_VALUE)
            else:
                set_attr(attr, default, PROP_TYPE_DEFAULT)


        @callback
        def async_update_template_trackers():
            for tracker in self.template_trackers:
                tracker.async_refresh()

        init_attr(ATTR_ENTITY, PROP_TYPE_STR)
        init_attr(ATTR_TYPE, PROP_TYPE_STR)
        init_attr(ATTR_ACTION, PROP_TYPE_STR)
        init_attr(ATTR_CONDITION, PROP_TYPE_BOOL, True)

        variable_handler.on_update(async_update_template_trackers)

        self.disconnect_event_listener = self.runtime.react.hass.bus.async_listen(EVENT_REACT_ACTION, self.async_handle, self.async_filter)
        for tracker in self.template_trackers:
            tracker.start()


    def start(self):
        self.enabled = True

    
    def stop(self):
        self.enabled = False


    def destroy(self):
        self.enabled = False
        if self.disconnect_event_listener:
            self.disconnect_event_listener()
        for tracker in self.template_trackers:
            tracker.destroy()


    @callback
    def async_filter(self, event: Event) -> bool:
        entity, type, action = extract_action_event_data(event)

        if not self.enabled:
            self.runtime.react.log.info(f"ActionHandler: '{self.runtime.workflow_config.id}'.'{self.actor.id}' skipping (workflow is disabled)")
            return False

        result = False
        if (entity == self.entity and type == self.type):
            if self.action is None:
                result = True   
            else:
                result = action == self.action

        return result


    def check_condition(self) -> bool:
        return self.condition


    @callback
    async def async_handle(self, event: Event):
        run = self.runtime.create_run_from_action(self, event)
        await run.async_run()


    def set_property(self, name: str, value: Any):
        if hasattr(self, name) and getattr(self, name) == value: 
            return

        setattr(self, name, value)
        if (name == ATTR_ENTITY or name == ATTR_TYPE):
            entity = getattr(self, ATTR_ENTITY, None)
            type = getattr(self, ATTR_TYPE, None)
            if entity and type and not self.complete:
                self.complete = True
                async_dispatcher_send(self.runtime.react.hass, SIGNAL_PROPERTY_COMPLETE, entity, type)


    def get_run_context(self) -> ActionContext:
        return ActionContext(
            condition=self.condition,
            index=self.index,
            actor_id=self.actor.id,
            condition_type=getattr(self, f"_{ATTR_CONDITION}{PROP_ATTR_TYPE_POSTFIX}", None)
        )


class ReactionHandler(RuntimeHandler):
    def __init__(self, runtime: WorkflowRuntime, reactor: Reactor, index: int, variable_handler: VariableHandler):
        self.runtime = runtime
        self.reactor = reactor
        self.index = index
        self.variable_handler = variable_handler
        self.enabled = False
        
        self.add_jitter(ATTR_ENTITY, PROP_TYPE_STR)
        self.add_jitter(ATTR_TYPE, PROP_TYPE_STR)
        self.add_jitter(ATTR_ACTION, PROP_TYPE_STR)
        self.add_jitter(ATTR_RESET_WORKFLOW, PROP_TYPE_STR)
        self.add_jitter(ATTR_DELAY, PROP_TYPE_INT)
        self.add_jitter(ATTR_CONDITION, PROP_TYPE_BOOL, True)

        self.condition_handler = ConditionHandler(self, lambda variables: self.jit_render(ATTR_CONDITION, variables[ATTR_ACTOR][ATTR_DATA], True))

        self.disconnect_signal_listener = async_dispatcher_connect(self.runtime.react.hass, SIGNAL_REACT.format(self.runtime.workflow_config.id), self.async_handle)


    def start(self):
        self.enabled = True

    
    def stop(self):
        self.enabled = False


    def destroy(self):
        self.enabled = False
        if self.disconnect_signal_listener:
            self.disconnect_signal_listener()
        

    def add_jitter(self, property: str, type_converter: Any, default: Any = None):
        attr_value = getattr(self.reactor, property, None)
        if attr_value:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                self.set_jitter(property, TemplateJitter(self.runtime.react,  property, Template(attr_value), type_converter), PROP_TYPE_TEMPLATE)
            else:
                self.set_jitter(property, ValueJitter(attr_value, type_converter), PROP_TYPE_VALUE)
        else:
            self.set_jitter(property, ValueJitter(default, type_converter), PROP_TYPE_DEFAULT)


    def set_jitter(self, property: str, value: Any, prop_type: str):
        jitter_prop = _JITTER_PROPERTY.format(property)
        type_prop = f"_{property}{PROP_ATTR_TYPE_POSTFIX}"
        setattr(self, jitter_prop, value)
        setattr(self, type_prop, prop_type)


    def jit_render(self, attr: str, actor_data: dict, default: Any = None):
        jitter_property = _JITTER_PROPERTY.format(attr)
        attr_jitter: TemplateJitter = getattr(self, jitter_property, None)
        if attr_jitter:
            return attr_jitter.render(self.variable_handler.to_dict(actor_data))
        else:
            return default


    @callback
    async def async_handle(self, variables: dict):
        actor_data = variables[ATTR_ACTOR][ATTR_DATA]

        with trace_path(TRACE_PATH_CONDITION):
            if not self.condition_handler.eval(variables):
                self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{self.reactor.id}' skipping (condition false)")
                return

        with trace_path(TRACE_PATH_EVENT):
            with trace_node(variables):
                # Don't forward toggle actions as they are always accompanied by other actions which will be forwarded
                if actor_data.get(ATTR_ACTOR_ACTION) == ACTION_TOGGLE and self.reactor.forward_action:
                    self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{actor_data.get(ATTR_ACTOR_ID)}' skipping reactor (action 'toggle' with forward_action): '{self.reactor.id}'")
                    trace_set_result(message="Skipped, toggle with forward-action ")
                    return

                reaction = ReactReaction(self.runtime.react)
                reaction.data.workflow_id = self.runtime.workflow_config.id
                reaction.data.actor_id = actor_data.get(ATTR_ACTOR_ID)
                reaction.data.actor_entity = actor_data.get(ATTR_ACTOR_ENTITY)
                reaction.data.actor_type = actor_data.get(ATTR_ACTOR_TYPE)
                reaction.data.actor_action = actor_data.get(ATTR_ACTOR_ACTION)
                reaction.data.reactor_id = self.reactor.id
                reaction.data.reactor_entity = self.jit_render(ATTR_ENTITY, actor_data)
                reaction.data.reactor_type = self.jit_render(ATTR_TYPE, actor_data)
                reaction.data.reactor_action = actor_data.get(ATTR_ACTION) if self.reactor.forward_action else self.jit_render(ATTR_ACTION, actor_data)
                reaction.data.reset_workflow = self.jit_render(ATTR_RESET_WORKFLOW, actor_data)
                reaction.data.overwrite = self.reactor.overwrite
                reaction.data.datetime = calculate_reaction_datetime(self.reactor.timing, self.reactor.schedule, self.jit_render(ATTR_DELAY, actor_data))
                
                self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{self.reactor.id}' sending reaction: {format_data(entity=reaction.data.reactor_entity, type=reaction.data.reactor_type, action=reaction.data.reactor_action, overwrite=reaction.data.overwrite, reset_workflow=reaction.data.reset_workflow)}")
                self.runtime.react.reactions.add(reaction)
                async_dispatcher_send(self.runtime.react.hass, SIGNAL_DISPATCH, reaction.data.id)

                trace_set_result(reaction=reaction.data.to_json())


class WorkflowRun:
    trace: Union[ReactTrace, None] = None

    def __init__(self, 
        runtime: WorkflowRuntime, 
        action_context: ActionContext, 
        # event: Event,
        entity: str,
        type: str,
        action: str,
        context: Context
    ) -> None:
        self.id = ulid_util.ulid_hex()
        self.runtime = runtime
        self.action_context = action_context
        self.entity = entity
        self.type = type
        self.action = action
        self.trigger_context = context


    def set_trace(self, trace: ReactTrace):
        self.trace = trace
        trace.set_trace(trace_get())
        trace.set_actor_description(f"{self.type} {self.action} {self.entity}")

        # Init run variables
        this = None
        if state := self.runtime.react.hass.states.get(self.runtime.workflow_config.entity_id):
            this = state.as_dict()
        self.run_variables = {
            ATTR_THIS: this,
            ATTR_VARIABLES: self.runtime.variable_handler.as_dict(),
            ATTR_ACTOR: {
                ATTR_DATA: {
                    ATTR_WORKFLOW_ID: self.runtime.workflow_config.id, 
                    ATTR_ACTOR_ID: self.action_context.actor_id, 
                    ATTR_ACTOR_ENTITY: self.entity, 
                    ATTR_ACTOR_TYPE: self.type, 
                    ATTR_ACTOR_ACTION: self.action,
                },
                ATTR_CONTEXT: self.trigger_context
            }
        }


    async def async_run(self):
        # Create a new context referring to the old context.
        parent_id = None if self.trigger_context is None else self.trigger_context.id
        self.run_context = Context(parent_id=parent_id)

        with trace_workflow(self):
            # Process actor
            with trace_path(f"{TRACE_PATH_ACTOR}/{str(self.action_context.index)}"):
                actor_variables = dict(self.run_variables)
                # Trace the trigger part 
                with trace_path(TRACE_PATH_TRIGGER):
                    with trace_node(actor_variables):
                        pass
                with trace_path(TRACE_PATH_CONDITION):
                    result = self.action_context.condition
                    if self.action_context.condition_type == PROP_TYPE_TEMPLATE:
                        with trace_node(self.run_variables):
                            trace_set_result(result=result)
                    if not result:
                        self.runtime.react.log.info(f"ActionHandler: '{self.runtime.workflow_config.id}'.'{self.action_context.actor_id}' skipping (condition false)")
                        return

            # Update workflow entity context                              
            self.runtime.workflow_state.async_set_context(self.run_context)

            self.run_variables[ATTR_CONTEXT] = self.trigger_context
            
            # Add a parallel section if more than one reactor is triggered
            if len(self.runtime.reactor_handlers) > 1:
                with trace_path(TRACE_PATH_PARALLEL):
                    with trace_node(self.run_variables):
                        trace_set_result(parallel=True)

            with trace_path(TRACE_PATH_REACTOR):
                async def async_run_with_trace(idx: int, handler: ReactionHandler) -> None:
                    trace_path_stack_cv.set(copy(trace_path_stack_cv.get()))
                    with trace_path(str(idx)):
                        await asyncio.wait({self.runtime.react.hass.async_create_task(handler.async_handle(self.run_variables))})
                results = await asyncio.gather(
                    *(async_run_with_trace(index, handler) for index, handler in enumerate(self.runtime.reactor_handlers)),
                    return_exceptions=True,
                )
                for result in results:
                    if isinstance(result, Exception):
                        raise result


class WorkflowRuntime(Updatable):
    
    def __init__(self, react: ReactBase, workflow_state: WorkflowState, workflow_config: Workflow) -> None:
        super().__init__(react)
        
        self.react = react
        self.workflow_state = workflow_state
        self.workflow_config = workflow_config
        self.actor_handlers: list[ActionHandler] = []
        self.reactor_handlers: list[ReactionHandler] = []
        self.variable_handler = VariableHandler(react, workflow_config)
        self.last_triggered: Union[datetime, None] = None

        for ai,actor in enumerate(workflow_config.actors):
            self.actor_handlers.append(ActionHandler(self, actor, ai, self.variable_handler))
        for ri,reactor in enumerate(workflow_config.reactors):
            self.reactor_handlers.append(ReactionHandler(self, reactor, ri, self.variable_handler))

        self.all_handlers: list[RuntimeHandler] = self.actor_handlers + self.reactor_handlers


    def start(self) -> None:
        for handler in self.all_handlers: handler.start()


    def stop(self) -> None:
        for handler in self.all_handlers: handler.stop()


    def destroy(self) -> None:
        self.variable_handler.destroy()
        for handler in self.all_handlers: handler.destroy()
        del self.all_handlers


    @callback
    async def async_trigger(self, context: Context) -> None:
        run = self.create_run_from_service_call(context)
        await run.async_run()

    
    def create_run_from_action(self, trigger_action_handler: ActionHandler, event: Event) -> WorkflowRun:
        entity,type,action = extract_action_event_data(event)
        return self.create_run_core(
            trigger_action_handler, 
            entity,
            type, 
            action, 
            event.context)


    def create_run_from_service_call(self, context: Context) -> WorkflowRun:
        actor_handler = self.actor_handlers[0]
        return self.create_run_core(
            actor_handler,
            actor_handler.entity,
            actor_handler.type,
            actor_handler.action,
            context)

    def create_run_core(self, 
        actor_handler: ActionHandler, 
        entity: str,
        type: str,
        action: str,
        context: Context,
    ):
        action_context = actor_handler.get_run_context()
        run = WorkflowRun(self, action_context, entity, type, action, context)
        self.react.log.info(f"ActionHandler: '{self.workflow_config.id}'.'{action_context.actor_id}' receiving action: {format_data(entity=run.entity, type=run.type, action=run.action)}")
        self.last_triggered = utcnow()
        self.async_update()
        return run