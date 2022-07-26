from __future__ import annotations
import asyncio
from copy import copy
from dataclasses import dataclass

from datetime import datetime
from typing import Any, Tuple, Union
from homeassistant.core import Context, Event, EventOrigin, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers.template import Template, is_template_string
from homeassistant.helpers.trace import trace_get, trace_path, trace_set_result, trace_path_stack_cv
from homeassistant.util import ulid as ulid_util
from homeassistant.util.dt import utcnow

from .config import Actor, DynamicData, Reactor, Workflow, calculate_reaction_datetime, get_property
from ..base import ReactBase
from ..reactions.base import ReactReaction
from ..utils.context import ActorTemplateContextDataProvider, TemplateContext, TemplateContextDataProvider, VariableContextDataProvider
from ..utils.events import ActionEventDataReader
from ..utils.signals import ReactSignalDataReader
from ..utils.logger import format_data
from ..utils.template import BaseJitter, TemplateJitter, TemplateTracker, ValueJitter
from ..utils.trace import ReactTrace, trace_node, trace_workflow
from ..utils.updatable import Updatable

from ..const import (
    ACTION_AVAILABLE,
    ACTION_TOGGLE,
    ACTION_UNAVAILABLE,
    ATTR_ACTION,
    ATTR_ACTOR,
    ATTR_ACTOR_ACTION,
    ATTR_ACTOR_DATA,
    ATTR_ACTOR_ENTITY,
    ATTR_ACTOR_ID,
    ATTR_ACTOR_TYPE,
    ATTR_CONDITION,
    ATTR_CONTEXT,
    ATTR_DATA,
    ATTR_DELAY,
    ATTR_ENTITY,
    ATTR_REACTOR,
    ATTR_RESET_WORKFLOW,
    ATTR_THIS,
    ATTR_TYPE,
    ATTR_VARIABLES,
    ATTR_WORKFLOW_ID,
    PROP_TYPE_DEFAULT,
    PROP_TYPE_SOURCE,
    PROP_TYPE_TEMPLATE,
    PROP_TYPE_VALUE,
    EVENT_REACT_ACTION,
    PROP_ATTR_TYPE_POSTFIX,
    PROP_TYPE_BOOL,
    PROP_TYPE_INT,
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


class RuntimeHandler(Updatable):
    def __init__(self, runtime: WorkflowRuntime, config_source: Any, template_context: TemplateContext) -> None:
        super().__init__(runtime.react)
        self.runtime = runtime
        self.config_source = config_source
        self.template_context = template_context

        self.template_trackers: list[TemplateTracker] = []
        self.value_container = type('object', (), {})()
        self.jit_attrs = []


    def start(self):
        pass
    

    def stop(self):
        pass

    def destroy(self):
        super().destroy()
        if self.template_context:
            self.template_context.destroy()
    

    def start_trackers(self):
        if self.template_context:
            @callback
            def async_update_template_trackers():
                for tracker in self.template_trackers:
                    tracker.async_refresh()
            self.template_context.on_update(async_update_template_trackers)
        
        for tracker in self.template_trackers:
            tracker.start()


    def init_attr(self, is_jit: bool, attr: str, type_converter: Any, default: Any = None):
        attr_value = getattr(self.config_source, attr, None)

        if is_jit:
            self.add_jitter(attr, attr_value, type_converter, default)
        else:
            self.add_tracker(attr, attr_value, type_converter, default)
    

    def add_tracker(self, attr: str, attr_value: Any, type_converter: Any, default: Any = None):
        
        def set_attr(attr: str, value: Any, prop_type: str):
            self.set_property(attr, value)
            self.set_property_type(attr, prop_type)

        if attr_value:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                set_attr(attr, None, PROP_TYPE_TEMPLATE)
                self.template_trackers.append(TemplateTracker(
                    react=self.runtime.react,
                    owner=self, 
                    property=attr, 
                    template=Template(attr_value),
                    type_converter=type_converter,
                    template_context=self.template_context,
                    update_callback=self.async_update))
            else:
                set_attr(attr, attr_value, PROP_TYPE_VALUE)
        else:
            set_attr(attr, default, PROP_TYPE_DEFAULT)


    def add_jitter(self, attr: str, attr_value: Any, type_converter: Any, default: Any = None):
        if attr_value:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                self.set_jitter(attr, TemplateJitter(self.runtime.react, attr, Template(attr_value), type_converter, self.template_context), PROP_TYPE_TEMPLATE)
            else:
                self.set_jitter(attr, ValueJitter(attr_value, type_converter), PROP_TYPE_VALUE)
        else:
            self.set_jitter(attr, ValueJitter(default, type_converter), PROP_TYPE_DEFAULT)
            
        self.jit_attrs.append(attr)


    def set_jitter(self, attr: str, value: BaseJitter, prop_type: str):
        self.set_jitter_prop(attr, value)
        self.set_property_type(attr, prop_type)


    def jit_render(self, attr: str, template_context_data_provider: TemplateContextDataProvider = None, default: Any = None):
        attr_jitter = self.get_jitter_prop(attr)
        if attr_jitter:
            return attr_jitter.render(template_context_data_provider)
        else:
            return default


    def jit_render_all(self, template_context_data_provider: TemplateContextDataProvider = None):
        result = {}
        for attr in self.jit_attrs:
            result[attr] = self.jit_render(attr, template_context_data_provider)
        return result


    def set_property(self, name: str, value: Any):
        if hasattr(self.value_container, name) and getattr(self.value_container, name) == value: 
            return
        setattr(self.value_container, name, value)


    def get_property(self, name: str, default: Any = None) -> Any:
        return getattr(self.value_container, name, default)


    def set_property_type(self, attr: str, prop_type: str):
        type_prop = f"_{attr}{PROP_ATTR_TYPE_POSTFIX}"
        setattr(self, type_prop, prop_type)


    def get_property_type(self, attr: str) -> str:
        type_prop = f"_{attr}{PROP_ATTR_TYPE_POSTFIX}"
        return getattr(self, type_prop, PROP_TYPE_DEFAULT)

    
    def set_jitter_prop(self, attr: str, value: BaseJitter):
        jitter_prop = _JITTER_PROPERTY.format(attr)
        setattr(self, jitter_prop, value)
        

    def get_jitter_prop(self, attr: str) -> BaseJitter:
        jitter_prop = _JITTER_PROPERTY.format(attr)
        return getattr(self, jitter_prop, None)


class DynamicDataHandler(RuntimeHandler):
    def __init__(self, is_jit: bool, runtime: WorkflowRuntime, dynamicData: DynamicData, template_context: TemplateContext) -> None:
        super().__init__(runtime, dynamicData, template_context)

        self.names = dynamicData.names

        for name in self.names:
            self.init_attr(is_jit, name, PROP_TYPE_SOURCE)

        self.start_trackers()


    def to_dict(self) -> dict:
        return vars(self.value_container)
        

    def as_trace_dict(self) -> dict:
        return { name : self.get_property(name) for name in self.names }

    
    def destroy(self):
        super().destroy()
        for tracker in self.template_trackers:
            tracker.destroy()


@dataclass
class ActionContext():
    condition: Union[bool, None] = True
    condition_type: Union[str, None] = None
    index: Union[int, None] = None
    actor_id: Union[str, None] = None
     

class TraceContext():
    variables: dict = {}


class ActionHandler(RuntimeHandler):
    
    def __init__(self, runtime: WorkflowRuntime, actor: Actor, index: int, template_context: TemplateContext):
        super().__init__(runtime, actor, template_context)

        self.actor = actor
        self.index = index
        self.complete = False
        self.enabled = False
        self.data_handler = DynamicDataHandler(False, runtime, actor.data, template_context)
        
        self.init_attr(False, ATTR_ENTITY, PROP_TYPE_STR)
        self.init_attr(False, ATTR_TYPE, PROP_TYPE_STR)
        self.init_attr(False, ATTR_ACTION, PROP_TYPE_STR)
        self.init_attr(False, ATTR_CONDITION, PROP_TYPE_BOOL, True)

        self.start_trackers()

        self.disconnect_event_listener = self.runtime.react.hass.bus.async_listen(EVENT_REACT_ACTION, self.async_handle, self.async_filter)


    def set_property(self, name: str, value: Any):
        super().set_property(name, value)

        if (name == ATTR_ENTITY or name == ATTR_TYPE):
            entity = self.get_property(ATTR_ENTITY)
            type = self.get_property(ATTR_TYPE)
            if entity and type and not self.complete:
                self.complete = True
                async_dispatcher_send(self.runtime.react.hass, SIGNAL_PROPERTY_COMPLETE, entity, type)


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
        action_event_reader = ActionEventDataReader(self.runtime.react, event)
        config_data = self.data_handler.to_dict()

        result = False
        if (action_event_reader.entity == self.get_property(ATTR_ENTITY) and action_event_reader.type == self.get_property(ATTR_TYPE)):
            config_action = self.get_property(ATTR_ACTION)
            if config_action is None:
                result = True   
            else:
                result = action_event_reader.action == config_action
            
            if result and config_data and not action_event_reader.data:
                result = False

            if result and action_event_reader.data and config_data:
                for name in config_data:
                    if not name in action_event_reader.data or action_event_reader.data[name] != config_data[name]:
                        result = False
                        break

        if result and not self.enabled:
            self.runtime.react.log.info(f"ActionHandler: '{self.runtime.workflow_config.id}'.'{self.actor.id}' skipping (workflow is disabled)")
            return False

        return result


    @callback
    async def async_handle(self, event: Event):
        run = self.runtime.create_run_from_action(self, event)
        await run.async_run()


    def get_run_context(self) -> ActionContext:
        return ActionContext(
            condition=self.get_property(ATTR_CONDITION, True),
            index=self.index,
            actor_id=self.actor.id,
            condition_type=self.get_property_type(ATTR_CONDITION)
        )

    
    def create_event(self, context: Context) -> Event:
        data = {
            ATTR_ENTITY: self.get_property(ATTR_ENTITY),
            ATTR_TYPE: self.get_property(ATTR_TYPE),
            ATTR_ACTION: self.get_property(ATTR_ACTION),
            ATTR_DATA: self.get_property(ATTR_DATA),
        }
        return Event(EVENT_REACT_ACTION, data, context=context)


class ReactionHandler(RuntimeHandler):
    def __init__(self, runtime: WorkflowRuntime, reactor: Reactor, index: int, template_context: TemplateContext):
        super().__init__(runtime, reactor, template_context)
        
        self.reactor = reactor
        self.index = index
        self.enabled = False
        self.data_handler = DynamicDataHandler(True, runtime, reactor.data, template_context)
        
        self.init_attr(True, ATTR_ENTITY, PROP_TYPE_STR)
        self.init_attr(True, ATTR_TYPE, PROP_TYPE_STR)
        self.init_attr(True, ATTR_ACTION, PROP_TYPE_STR)
        self.init_attr(True, ATTR_RESET_WORKFLOW, PROP_TYPE_STR)
        self.init_attr(True, ATTR_DELAY, PROP_TYPE_INT)
        self.init_attr(True, ATTR_CONDITION, PROP_TYPE_BOOL, True)

        self.disconnect_signal_listener = async_dispatcher_connect(runtime.react.hass, SIGNAL_REACT.format(self.runtime.workflow_config.id), self.async_handle)


    def start(self):
        self.enabled = True

    
    def stop(self):
        self.enabled = False


    def destroy(self):
        super().destroy()
        self.enabled = False
        if self.disconnect_signal_listener:
            self.disconnect_signal_listener()


    @callback
    async def async_handle(self, action_context: ActionContext, action_event_reader: ActionEventDataReader, trace_variables: dict):
        template_context_data_provider = ActorTemplateContextDataProvider(self._react, action_event_reader)
        
        reactor_data = self.data_handler.jit_render_all(template_context_data_provider)

        trace_variables[ATTR_REACTOR] = {
            ATTR_DATA: reactor_data
        }
        
        with trace_path(TRACE_PATH_CONDITION):
            condition_result = self.jit_render(ATTR_CONDITION, template_context_data_provider, True)
            if self.get_property_type(ATTR_CONDITION) == PROP_TYPE_TEMPLATE:
                with trace_node(trace_variables):
                    trace_set_result(result=condition_result)
            if not condition_result:
                self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{self.reactor.id}' skipping (condition false)")
                return

        with trace_path(TRACE_PATH_EVENT):
            with trace_node(trace_variables):
                if self.reactor.forward_action:
                    # Don't forward toggle actions as they are always accompanied by other actions which will be forwarded
                    if action_event_reader.action == ACTION_TOGGLE:
                        self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{action_context.actor_id}' skipping reactor (action 'toggle' with forward_action): '{self.reactor.id}'")
                        trace_set_result(message="Skipped, toggle with forward-action")
                        return
                    # Don't forward availabililty actions as reactors don't support them
                    if action_event_reader.action == ACTION_AVAILABLE or action_event_reader.action == ACTION_UNAVAILABLE:
                        self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{action_context.actor_id}' skipping reactor (availability action with forward_action): '{self.reactor.id}'")
                        trace_set_result(message="Skipped, availability action with forward_action")
                        return
                    

                reaction = ReactReaction(self.runtime.react)
                reaction.data.workflow_id = self.runtime.workflow_config.id
                reaction.data.actor_id = action_context.actor_id
                reaction.data.actor_entity = action_event_reader.entity
                reaction.data.actor_type = action_event_reader.type
                reaction.data.actor_action = action_event_reader.action
                reaction.data.reactor_id = self.reactor.id
                reaction.data.reactor_entity = self.jit_render(ATTR_ENTITY, template_context_data_provider)
                reaction.data.reactor_type = self.jit_render(ATTR_TYPE, template_context_data_provider)
                reaction.data.reactor_action = action_event_reader.action if self.reactor.forward_action else self.jit_render(ATTR_ACTION, template_context_data_provider)
                reaction.data.reset_workflow = self.jit_render(ATTR_RESET_WORKFLOW, template_context_data_provider)
                reaction.data.overwrite = self.reactor.overwrite
                reaction.data.datetime = calculate_reaction_datetime(self.reactor.timing, self.reactor.schedule, self.jit_render(ATTR_DELAY, template_context_data_provider))
                reaction.data.data = reactor_data

                self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{self.reactor.id}' sending reaction: {format_data(entity=reaction.data.reactor_entity, type=reaction.data.reactor_type, action=reaction.data.reactor_action, overwrite=reaction.data.overwrite, reset_workflow=reaction.data.reset_workflow)}")
                self.runtime.react.reactions.add(reaction)
                async_dispatcher_send(self.runtime.react.hass, SIGNAL_DISPATCH, reaction.data.id)

                trace_set_result(reaction=reaction.data.to_json())


class WorkflowRun:
    trace: Union[ReactTrace, None] = None

    def __init__(self, 
        runtime: WorkflowRuntime, 
        actor_id: str,
        action_context: ActionContext, 
        action_event_reader: ActionEventDataReader,
    ) -> None:
        self.id = ulid_util.ulid_hex()
        self.runtime = runtime
        self.actor_id = actor_id
        self.action_context = action_context
        self.action_event_reader = action_event_reader


    def set_trace(self, trace: ReactTrace):
        self.trace = trace
        trace.set_trace(trace_get())
        trace.set_actor_description(f"{self.action_event_reader.type} {self.action_event_reader.action} {self.action_event_reader.entity}")

        # Init run variables
        this = None
        if state := self.runtime.react.hass.states.get(self.runtime.workflow_config.entity_id):
            this = state.as_dict()
        self.trace_variables = {
            ATTR_THIS: this,
            ATTR_VARIABLES: self.runtime.variable_handler.as_trace_dict(),
            ATTR_ACTOR: {
                ATTR_DATA: {
                    ATTR_WORKFLOW_ID: self.runtime.workflow_config.id, 
                    ATTR_ACTOR_ID: self.action_context.actor_id, 
                    ATTR_ACTOR_ENTITY: self.action_event_reader.entity, 
                    ATTR_ACTOR_TYPE: self.action_event_reader.type, 
                    ATTR_ACTOR_ACTION: self.action_event_reader.action,
                    ATTR_ACTOR_DATA:  self.action_event_reader.data,
                },
                ATTR_CONTEXT: self.action_event_reader.context
            }
        }


    async def async_run(self):
        # Create a new context referring to the old context.
        parent_id = None if self.action_event_reader.context is None else self.action_event_reader.context.id
        self.run_context = Context(parent_id=parent_id)
use trace_context
        with trace_workflow(self):
            # Process actor
            with trace_path(f"{TRACE_PATH_ACTOR}/{str(self.action_context.index)}"):
                actor_variables = dict(self.trace_variables)
                # Trace the trigger part 
                with trace_path(TRACE_PATH_TRIGGER):
                    with trace_node(actor_variables):
                        pass
                with trace_path(TRACE_PATH_CONDITION):
                    result = self.action_context.condition
                    if self.action_context.condition_type == PROP_TYPE_TEMPLATE:
                        with trace_node(self.trace_variables):
                            trace_set_result(result=result)
                    if not result:
                        self.runtime.react.log.info(f"ActionHandler: '{self.runtime.workflow_config.id}'.'{self.action_context.actor_id}' skipping (condition false)")
                        return

            self.trace_variables[ATTR_CONTEXT] = self.action_event_reader.context
            
            # Add a parallel section if more than one reactor is triggered
            if len(self.runtime.reactor_handlers) > 1:
                with trace_path(TRACE_PATH_PARALLEL):
                    with trace_node(self.trace_variables):
                        trace_set_result(parallel=True)

            with trace_path(TRACE_PATH_REACTOR):
                async def async_run_with_trace(idx: int, handler: ReactionHandler) -> None:
                    trace_path_stack_cv.set(copy(trace_path_stack_cv.get()))
                    with trace_path(str(idx)):
                        await asyncio.wait({self.runtime.react.hass.async_create_task(handler.async_handle(self.action_context, self.action_event_reader, self.trace_variables))})
                results = await asyncio.gather(
                    *(async_run_with_trace(index, handler) for index, handler in enumerate(self.runtime.reactor_handlers)),
                    return_exceptions=True,
                )
                for result in results:
                    if isinstance(result, Exception):
                        raise result


class WorkflowRuntime(Updatable):
    
    def __init__(self, react: ReactBase, workflow_config: Workflow) -> None:
        super().__init__(react)
        
        self.react = react
        self.workflow_config = workflow_config
        self.actor_handlers: list[ActionHandler] = []
        self.reactor_handlers: list[ReactionHandler] = []
        self.variable_handler = DynamicDataHandler(False, self,  workflow_config.variables, TemplateContext(react))
        self.last_triggered: Union[datetime, None] = None

        for ai,actor in enumerate(workflow_config.actors):
            self.actor_handlers.append(ActionHandler(self, actor, ai, TemplateContext(react, VariableContextDataProvider(react, self.variable_handler))))
        for ri,reactor in enumerate(workflow_config.reactors):
            self.reactor_handlers.append(ReactionHandler(self, reactor, ri, TemplateContext(react, VariableContextDataProvider(react, self.variable_handler))))

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
        action_event_reader = ActionEventDataReader(self.react, event)
        return self.create_run_core(trigger_action_handler, action_event_reader)


    def create_run_from_service_call(self, context: Context) -> WorkflowRun:
        actor_handler = self.actor_handlers[0]
        action_event_reader = ActionEventDataReader(self.react, actor_handler.create_event(context))
        return self.create_run_core(actor_handler, action_event_reader)


    def create_run_core(self, 
        actor_handler: ActionHandler, 
        action_event_reader: ActionEventDataReader,
    ):
        action_context = actor_handler.get_run_context()
        run = WorkflowRun(self, actor_handler.actor.id, action_context, action_event_reader)
        self.react.log.info(f"ActionHandler: '{self.workflow_config.id}'.'{action_context.actor_id}' receiving action: {format_data(entity=run.action_event_reader.entity, type=run.action_event_reader.type, action=run.action_event_reader.action)}")
        self.last_triggered = utcnow()
        self.async_update()
        return run
