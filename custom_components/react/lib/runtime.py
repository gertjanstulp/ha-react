from __future__ import annotations

import asyncio
from copy import copy
from dataclasses import dataclass

from datetime import datetime
from itertools import product
from typing import Union
from homeassistant.const import ATTR_ID
from homeassistant.core import Context, Event, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers.trace import trace_get, trace_path, trace_set_result, trace_path_stack_cv
from homeassistant.util import ulid as ulid_util
from homeassistant.util.dt import utcnow

from .config import Actor, Reactor, Workflow, calculate_reaction_datetime
from ..base import ReactBase
from ..reactions.base import ReactReaction
from ..utils.context import ActorTemplateContextDataProvider, TemplateContext, VariableContextDataProvider
from ..utils.events import ActionEventDataReader
from ..utils.logger import format_data
from ..utils.struct import ActorRuntime, ReactorConfig, ReactorRuntime
from ..utils.jit import JitHandler
from ..utils.trace import ReactTrace, trace_node, trace_workflow
from ..utils.track import TrackHandler
from ..utils.updatable import Updatable

from ..const import (
    _EMPTY_,
    ATTR_ACTION,
    ATTR_ACTOR,
    ATTR_CONDITION,
    ATTR_CONTEXT,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_THIS,
    ATTR_TYPE,
    ATTR_VARIABLES,
    EVENT_REACT_ACTION,
    SIGNAL_DISPATCH,
    SIGNAL_PROPERTY_COMPLETE,
    SIGNAL_TRACK_UPDATE,
    TRACE_PATH_ACTOR,
    TRACE_PATH_CONDITION,
    TRACE_PATH_EVENT,
    TRACE_PATH_PARALLEL,
    TRACE_PATH_REACTOR,
    TRACE_PATH_TRIGGER
)



@dataclass
class ActionContext():
    
    condition: Union[bool, None] = True
    condition_is_template: Union[bool, None] = None
    index: Union[int, None] = None
    actor_id: Union[str, None] = None


class BaseHandler():

    def __init__(self, runtime: WorkflowRuntime, index: int, tctx: TemplateContext) -> None:
        self.enabled: bool = False
        self.runtime = runtime
        self.index = index
        self.tctx = tctx


    def start(self) -> None:
        pass
    

    def stop(self) -> None:
        pass


    def destroy(self) -> None:
        if self.tctx:
            self.tctx.destroy()
     

class ActionHandler(BaseHandler):

    def __init__(self, runtime: WorkflowRuntime, actor_config: Actor, index: int, tctx: TemplateContext):
        super().__init__(runtime, index, tctx)
        
        self.complete: bool = False
        self.enabled: bool = False
        self.actor_config = actor_config

        def async_track_update(owner: ActorRuntime, attr: str):
            if (attr == ATTR_ENTITY or attr == ATTR_TYPE):
                if owner.entity and owner.type and not self.complete:
                    self.complete = True
                    async_dispatcher_send(self.runtime.react.hass, SIGNAL_PROPERTY_COMPLETE, owner.entity, owner.type)

        self.disconnect_track_update = async_dispatcher_connect(runtime.react.hass, SIGNAL_TRACK_UPDATE, async_track_update)
        self.track_handler = TrackHandler[ActorRuntime](runtime.react, actor_config, tctx, ActorRuntime)
        self.actor_runtime = self.track_handler.value_container

        self.disconnect_event_listener = runtime.react.hass.bus.async_listen(EVENT_REACT_ACTION, self.async_handle, self.async_filter)


    def start(self):
        self.enabled = True

    
    def stop(self):
        self.enabled = False


    def destroy(self):
        super().destroy()
        self.enabled = False
        if self.disconnect_event_listener:
            self.disconnect_event_listener()
        if self.disconnect_track_update:
            self.disconnect_track_update()
        if self.track_handler:
            self.track_handler.destroy()


    @callback
    def async_filter(self, event: Event) -> bool:
        event_reader = ActionEventDataReader(self.runtime.react, event)

        result = False
        if (event_reader.entity in self.actor_runtime.entity and event_reader.type in self.actor_runtime.type):
            config_action = self.actor_runtime.action
            if config_action is None:
                result = True   
            else:
                result = event_reader.action in config_action
            
            if result and self.actor_runtime.data and len(self.actor_runtime.data) > 0 and not event_reader.data:
                result = False

            if result and event_reader.data and self.actor_runtime.data:
                match: bool
                for data_item in self.actor_runtime.data:
                    match = True
                    for name in data_item.names:
                        if not name in event_reader.data or event_reader.data[name] != data_item.get(name):
                            match = False
                            break
                    if match:
                        break

                if not match:
                    result = False

        if result and not self.enabled:
            self.runtime.react.log.info(f"ActionHandler: '{self.runtime.workflow_config.id}'.'{self.actor_config.id}' skipping (workflow is disabled)")
            return False

        return result


    @callback
    async def async_handle(self, event: Event):
        run = self.runtime.create_run_from_action(self, event)
        await run.async_run()


    def get_action_context(self) -> ActionContext:
        return ActionContext(self.actor_runtime.condition, self.track_handler.is_template(ATTR_CONDITION), self.index, self.actor_config.id,
    )

    
    def create_event(self, context: Context) -> Event:
        data = {
            ATTR_ENTITY: self.actor_runtime.entity.first,
            ATTR_TYPE: self.actor_runtime.type.first,
            ATTR_ACTION: self.actor_runtime.action.first,
            ATTR_DATA: self.actor_runtime.data[0].as_dict() if self.actor_runtime.data and len(self.actor_runtime.data) > 0 else None,
        }
        return Event(EVENT_REACT_ACTION, data, context=context)


class ReactionHandler(BaseHandler):

    def __init__(self, runtime: WorkflowRuntime, reactor_config: Reactor, index: int, tctx: TemplateContext):
        super().__init__(runtime, index, tctx)
        
        self.runtime = runtime
        self.reactor_config = reactor_config
        self.index = index
        
        self.jit_handler = JitHandler[ReactorRuntime](runtime.react, reactor_config, tctx, ReactorRuntime)


    def start(self):
        self.enabled = True

    
    def stop(self):
        self.enabled = False


    def destroy(self):
        super().destroy()
        self.enabled = False


    @callback
    async def async_handle(self, wctx: WorkflowRunContext):
        template_context_data_provider = ActorTemplateContextDataProvider(self.runtime.react, wctx.event_reader)
        reactor_runtime = self.jit_handler.render(template_context_data_provider)
        
        with trace_path(TRACE_PATH_CONDITION):
            condition_result = reactor_runtime.condition
            if self.jit_handler.is_template(ATTR_CONDITION):
                with trace_node(wctx.trace_variables):
                    trace_set_result(result=condition_result)
            if not condition_result:
                self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{self.reactor_config.id}' skipping (condition false)")
                return

        with trace_path(TRACE_PATH_EVENT):
            for reaction in create_reactions(self.runtime.react, wctx, self.reactor_config, reactor_runtime):
                with trace_node(wctx.trace_variables):
                    if reaction.is_forward_toggle:
                        # Don't forward toggle actions as they are always accompanied by other actions which will be forwarded
                        self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{wctx.actx.actor_id}' skipping reactor (action 'toggle' with forward_action): '{self.reactor_config.id}'")
                        trace_set_result(message="Skipped, toggle with forward-action")
                        return

                    if reaction.is_forward_availability:
                        # Don't forward availabililty actions as reactors don't support them
                        self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{wctx.actx.actor_id}' skipping reactor (availability action with forward_action): '{self.reactor_config.id}'")
                        trace_set_result(message="Skipped, availability action with forward_action")
                        return

                    self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{self.reactor_config.id}' sending reaction: {format_data(entity=reaction.data.reactor_entity, type=reaction.data.reactor_type, action=reaction.data.reactor_action, overwrite=reaction.data.overwrite, reset_workflow=reaction.data.reset_workflow)}")
                    self.runtime.react.reactions.add(reaction)
                    async_dispatcher_send(self.runtime.react.hass, SIGNAL_DISPATCH, reaction.data.id)

                    trace_set_result(reaction=reaction.data.to_json())


def create_reactions(react: ReactBase, wctx: WorkflowRunContext, reactor_config: ReactorConfig, reactor_runtime: ReactorRuntime):
    result: list[ReactReaction] = []
    reactor_action = [wctx.event_reader.action] if reactor_runtime.forward_action else reactor_runtime.action

    for entity, type, action, data_item in product(reactor_runtime.entity or [_EMPTY_], reactor_runtime.type or [_EMPTY_], reactor_action or [_EMPTY_], reactor_runtime.data or [_EMPTY_]):
        reaction = ReactReaction(react)

        reaction.data.workflow_id = wctx.workflow_id
        reaction.data.actor_id = wctx.actx.actor_id
        reaction.data.reactor_id = reactor_config.id

        reaction.data.actor_entity = wctx.event_reader.entity
        reaction.data.actor_type = wctx.event_reader.type
        reaction.data.actor_action = wctx.event_reader.action
        
        reaction.data.reactor_entity = entity
        reaction.data.reactor_type = type
        reaction.data.reactor_action = action
        reaction.data.reset_workflow = reactor_runtime.reset_workflow
        reaction.data.overwrite = reactor_runtime.overwrite
        reaction.data.forward_action = reactor_runtime.forward_action
        reaction.data.datetime = calculate_reaction_datetime(reactor_runtime.timing, reactor_runtime.schedule, reactor_runtime.delay)
        reaction.data.data = data_item.as_dict() if data_item != _EMPTY_ else None

        result.append(reaction)

    return result


class WorkflowRunContext:

    def __init__(self, react: ReactBase, workflow_config: Workflow, variable_handler: TrackHandler, actx: ActionContext, event_reader: ActionEventDataReader) -> None:
        self.react = react
        self.workflow_config = workflow_config
        self.variable_handler = variable_handler
        self.actx = actx
        self.event_reader = event_reader
        
        self.trace_variables = {}
        self.workflow_id = workflow_config.id


    def trace_variables_init(self):
        # Init run variables
        this = None
        if state := self.react.hass.states.get(self.workflow_config.entity_id):
            this = state.as_dict()
        self.trace_variables = {
            ATTR_THIS: this,
            ATTR_VARIABLES: self.variable_handler.as_trace_dict() | { ATTR_ACTOR: self.event_reader.to_dict() },
            ATTR_ACTOR: {
                ATTR_ID: self.actx.actor_id, 
                ATTR_CONTEXT: self.event_reader.hass_context
            }
        }

    def trace_variables_set_hass_context(self):
        self.trace_variables[ATTR_CONTEXT] = self.event_reader.hass_context
        

    def create_hass_run_context(self):
        parent_id = None if self.event_reader.hass_context is None else self.event_reader.hass_context.id
        self.hass_run_context = Context(parent_id=parent_id)


    def create_trace_actor_path(self):
        return f"{TRACE_PATH_ACTOR}/{str(self.actx.index)}"


class WorkflowRun:

    def __init__(self, wctx: WorkflowRunContext, reactor_handlers: list[ReactionHandler]) -> None:
        self.id = ulid_util.ulid_hex()
        self.wctx = wctx
        self.reactor_handlers = reactor_handlers
        self.trace: Union[ReactTrace, None] = None


    def set_trace(self, trace: ReactTrace):
        self.trace = trace
        trace.set_trace(trace_get())
        trace.set_actor_description(f"{self.wctx.event_reader.type} {self.wctx.event_reader.action} {self.wctx.event_reader.entity}")

        self.wctx.trace_variables_init()


    async def async_run(self):
        # Create a new context referring to the old context.
        wctx = self.wctx
        wctx.create_hass_run_context()

        with trace_workflow(self):
            # Process actor
            with trace_path(wctx.create_trace_actor_path()):
                # Trace the data part 
                with trace_path(TRACE_PATH_TRIGGER):
                    with trace_node(wctx.trace_variables):
                        pass
                with trace_path(TRACE_PATH_CONDITION):
                    result = wctx.actx.condition
                    if wctx.actx.condition_is_template:
                        with trace_node(wctx.trace_variables):
                            trace_set_result(result=result)
                    if not result:
                        self.wctx.react.log.info(f"ActionHandler: '{self.wctx.workflow_config.id}'.'{wctx.actx.actor_id}' skipping (condition false)")
                        return

            wctx.trace_variables_set_hass_context()

            # Add a parallel section if more than one reactor is triggered
            if len(self.reactor_handlers) > 1:
                with trace_path(TRACE_PATH_PARALLEL):
                    with trace_node(wctx.trace_variables):
                        trace_set_result(parallel=True)

            with trace_path(TRACE_PATH_REACTOR):
                async def async_run_with_trace(idx: int, handler: ReactionHandler) -> None:
                    trace_path_stack_cv.set(copy(trace_path_stack_cv.get()))
                    with trace_path(str(idx)):
                        await asyncio.wait({self.wctx.react.hass.async_create_task(handler.async_handle(wctx))})
                results = await asyncio.gather(
                    *(async_run_with_trace(index, handler) for index, handler in enumerate(self.reactor_handlers)),
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
        self.variable_handler = TrackHandler(self.react,  workflow_config.variables, TemplateContext(react))
        self.last_triggered: Union[datetime, None] = None

        for ai,actor in enumerate(workflow_config.actors):
            self.actor_handlers.append(ActionHandler(self, actor, ai, TemplateContext(react, VariableContextDataProvider(react, self.variable_handler))))
        for ri,reactor in enumerate(workflow_config.reactors):
            self.reactor_handlers.append(ReactionHandler(self, reactor, ri, TemplateContext(react, VariableContextDataProvider(react, self.variable_handler))))

        self.all_handlers: list[BaseHandler] = self.actor_handlers + self.reactor_handlers


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
        event_reader = ActionEventDataReader(self.react, event)
        return self.create_run_core(trigger_action_handler, event_reader)


    def create_run_from_service_call(self, context: Context) -> WorkflowRun:
        actor_handler = self.actor_handlers[0]
        event_reader = ActionEventDataReader(self.react, actor_handler.create_event(context))
        return self.create_run_core(actor_handler, event_reader)


    def create_run_core(self, 
        actor_handler: ActionHandler, 
        event_reader: ActionEventDataReader,
    ):
        wctx = WorkflowRunContext(self.react, self.workflow_config, self.variable_handler, actor_handler.get_action_context(), event_reader)
        run = WorkflowRun(wctx, self.reactor_handlers)
        self.react.log.info(f"ActionHandler: '{self.workflow_config.id}'.'{actor_handler.actor_config.id}' receiving action: {format_data(entity=wctx.event_reader.entity, type=wctx.event_reader.type, action=wctx.event_reader.action)}")
        self.last_triggered = utcnow()
        self.async_update()
        return run
