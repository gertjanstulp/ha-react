from __future__ import annotations
import asyncio
from copy import copy
from dataclasses import dataclass

from datetime import datetime
from itertools import product
import types
from typing import Any, Tuple, Union
from homeassistant.const import ATTR_ID
from homeassistant.core import Context, Event, EventOrigin, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers.template import Template, is_template_string
from homeassistant.helpers.trace import trace_get, trace_path, trace_set_result, trace_path_stack_cv
from homeassistant.util import ulid as ulid_util
from homeassistant.util.dt import utcnow

from .config import Actor, DynamicData, MultiItem, Reactor, Workflow, calculate_reaction_datetime
from ..base import ReactBase
from ..reactions.base import ReactReaction
from ..utils.context import ActorTemplateContextDataProvider, TemplateContext, TemplateContextDataProvider, VariableContextDataProvider
from ..utils.events import ActionEventDataReader
from ..utils.logger import format_data
from ..utils.signals import ReactSignalDataReader
from ..utils.struct import DynamicData, MultiItem
from ..utils.template import BasePropertyJitter, MultiItemJitter, ObjectJitter, TemplatePropertyJitter, MultiItemTracker, ObjectTracker, TemplatePropertyTracker, ValuePropertyJitter
from ..utils.trace import ReactTrace, trace_node, trace_workflow
from ..utils.updatable import Updatable

from ..const import (
    ACTION_AVAILABLE,
    ACTION_TOGGLE,
    ACTION_UNAVAILABLE,
    ATTR_ACTION,
    ATTR_ACTOR,
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
    PROP_TYPE_DEFAULT,
    PROP_TYPE_LIST,
    PROP_TYPE_MULTI_ITEM,
    PROP_TYPE_OBJECT,
    PROP_TYPE_SOURCE,
    PROP_TYPE_TEMPLATE,
    PROP_TYPE_VALUE,
    EVENT_REACT_ACTION,
    PROP_ATTR_TYPE_POSTFIX,
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
    def __init__(self, is_jit: bool, runtime: WorkflowRuntime, config_source: DynamicData, tctx: TemplateContext, value_container: object = None) -> None:
        super().__init__(runtime.react)
        self.runtime = runtime
        self.config_source = config_source
        self.tctx = tctx

        self.template_trackers: list[TemplatePropertyTracker] = []
        self.value_container = type('object', (), {})()
        self.jit_attrs = []
        if is_jit:
            self.jitter = ObjectJitter(runtime.react, "root", self)

        for attr in config_source.names:
            self.init_attr(is_jit, attr, PROP_TYPE_SOURCE)


    def start(self):
        pass
    

    def stop(self):
        pass


    def destroy(self):
        super().destroy()
        if self.tctx:
            self.tctx.destroy()
    

    def start_trackers(self):
        if self.tctx:
            @callback
            def async_update_template_trackers():
                for tracker in self.template_trackers:
                    tracker.async_refresh()
            self.tctx.on_update(async_update_template_trackers)
        
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

        if isinstance(attr_value, MultiItem):
            handler = MultiItemHandler(False, self.runtime, attr_value, self.tctx)
            set_attr(attr, handler.value_container, PROP_TYPE_MULTI_ITEM)

            self.template_trackers.append(MultiItemTracker(
                react=self.runtime.react,
                property=attr,
                handler=handler
            ))
        elif isinstance(attr_value, DynamicData):
            handler = DynamicDataHandler(False, self.runtime, attr_value, self.tctx)
            set_attr(attr, handler.value_container, PROP_TYPE_OBJECT)
            
            self.template_trackers.append(ObjectTracker(
                react=self.runtime.react,
                property=attr,
                handler=handler
            ))
        elif isinstance(attr_value, list):
            if len(attr_value) > 0 and isinstance(attr_value[0], DynamicData):
                handlers = [ DynamicDataHandler(False, self.runtime, item, self.tctx) for item in attr_value ]
                set_attr(attr, [handler.value_container for handler in handlers], PROP_TYPE_LIST)
            else:
                pass
        elif attr_value:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                set_attr(attr, None, PROP_TYPE_TEMPLATE)
                self.template_trackers.append(TemplatePropertyTracker(
                    react=self.runtime.react,
                    owner=self, 
                    property=attr, 
                    template=Template(attr_value),
                    type_converter=type_converter,
                    tctx=self.tctx,
                    update_callback=self.async_update))
            else:
                set_attr(attr, attr_value, PROP_TYPE_VALUE)
        else:
            set_attr(attr, default, PROP_TYPE_DEFAULT)


    def add_jitter(self, attr: str, attr_value: Any, type_converter: Any, default: Any = None):

        def set_jitter(attr: str, value: Any, prop_type: str, target: Any = None):
            self.set_jitter_prop(attr, value)
            self.set_property_type(attr, prop_type)
            # if target:
            #     self.set_property(attr, target)

        if isinstance(attr_value, MultiItem):
            handler = MultiItemHandler(True, self.runtime, attr_value, self.tctx)
            set_jitter(attr, MultiItemJitter(self.runtime.react, attr, handler), PROP_TYPE_MULTI_ITEM, handler.value_container)
        elif isinstance(attr_value, DynamicData):
            handler = DynamicDataHandler(True, self.runtime, attr_value, self.tctx)
            set_jitter(attr, ObjectJitter(self.runtime.react, attr, handler), PROP_TYPE_OBJECT, handler.value_container)
        elif isinstance(attr_value, list):
            if len(attr_value) > 0 and isinstance(attr_value[0], DynamicData):
                handlers = [ DynamicDataHandler(True, self.runtime, item, self.tctx) for item in attr_value ]
                set_jitter(attr, [ObjectJitter(self.runtime.react, attr, handler) for handler in handlers], PROP_TYPE_LIST, [handler.value_container for handler in handlers])
            else:
                pass
        elif attr_value:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                set_jitter(attr, TemplatePropertyJitter(self, attr, Template(attr_value), type_converter, self.tctx), PROP_TYPE_TEMPLATE)
            else:
                set_jitter(attr, ValuePropertyJitter(self, attr, attr_value, type_converter), PROP_TYPE_VALUE)
        else:
            set_jitter(attr, ValuePropertyJitter(self, attr, default, type_converter), PROP_TYPE_DEFAULT)
            
        self.jit_attrs.append(attr)


    # def jit_render(self, attr: str, template_context_data_provider: TemplateContextDataProvider = None, default: Any = None):
    #     attr_jitter = self.get_jitter_prop(attr)
    #     if attr_jitter:
    #         return attr_jitter.render(template_context_data_provider)
    #     else:
    #         return default


    # def jit_render_all(self, template_context_data_provider: TemplateContextDataProvider = None):
    #     result = {}
    #     for attr in self.jit_attrs:
    #         result[attr] = self.jit_render(attr, template_context_data_provider)
    #     return result


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

    
    def set_jitter_prop(self, attr: str, value: BasePropertyJitter):
        jitter_prop = _JITTER_PROPERTY.format(attr)
        setattr(self, jitter_prop, value)
        

    def get_jitter_prop(self, attr: str) -> BasePropertyJitter:
        jitter_prop = _JITTER_PROPERTY.format(attr)
        return getattr(self, jitter_prop, None)


class DynamicDataHandler(RuntimeHandler):
    def __init__(self, is_jit: bool, runtime: WorkflowRuntime, dynamicData: DynamicData, tctx: TemplateContext) -> None:
        super().__init__(is_jit, runtime, dynamicData, tctx)

        self.names = dynamicData.names

        # for name in self.names:
        #     self.init_attr(is_jit, name, PROP_TYPE_SOURCE)

        self.start_trackers()


    def to_dict(self) -> dict:
        return vars(self.value_container)
        

    def as_trace_dict(self) -> dict:
        return { name : self.get_property(name) for name in self.names }

    
    def destroy(self):
        super().destroy()
        for tracker in self.template_trackers:
            tracker.destroy()


class MultiItemHandler(DynamicDataHandler):
    def __init__(self, is_jit: bool, runtime: WorkflowRuntime, multi_item: MultiItem, tctx: TemplateContext) -> None:
        super().__init__(is_jit, runtime, multi_item, tctx)

        this = self
        def iter(self):
            return MultiItem.MultiItemIterator(self, this.names)
        class newclass(self.value_container.__class__):
            pass
        setattr(newclass, "__iter__", iter)
        self.value_container.__class__ = newclass


@dataclass
class ActionContext():
    condition: Union[bool, None] = True
    condition_type: Union[str, None] = None
    index: Union[int, None] = None
    actor_id: Union[str, None] = None
     

class TraceContext():
    variables: dict = {}


class ActionHandler(RuntimeHandler):
    complete: bool = False
    enabled: bool = False

    def __init__(self, runtime: WorkflowRuntime, actor: Actor, index: int, tctx: TemplateContext):
        super().__init__(False, runtime, actor, tctx)

        self.actor = actor
        self.index = index
        # self.data_handler = DynamicDataHandler(False, runtime, actor.data, tctx)
        
        # self.init_attr(False, ATTR_ENTITY, PROP_TYPE_STR)
        # self.init_attr(False, ATTR_TYPE, PROP_TYPE_STR)
        # self.init_attr(False, ATTR_ACTION, PROP_TYPE_STR)
        # self.init_attr(False, ATTR_CONDITION, PROP_TYPE_BOOL, True)

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
        event_reader = ActionEventDataReader(self.runtime.react, event)
        config_data = self.value_container.data if hasattr(self.value_container, ATTR_DATA) else None

        result = False
        if (event_reader.entity in self.get_property(ATTR_ENTITY) and event_reader.type in self.get_property(ATTR_TYPE)):
            config_action = self.get_property(ATTR_ACTION)
            if config_action is None:
                result = True   
            else:
                result = event_reader.action in config_action
            
            if result and config_data and not event_reader.data:
                result = False

            if result and event_reader.data and config_data:
                for name in config_data:
                    if not name in event_reader.data or event_reader.data[name] != config_data[name]:
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


    def get_action_context(self) -> ActionContext:
        return ActionContext(
            condition=self.get_property(ATTR_CONDITION, True),
            index=self.index,
            actor_id=self.actor.id,
            condition_type=self.get_property_type(ATTR_CONDITION)
        )

    
    def create_event(self, context: Context) -> Event:
        data = {
            ATTR_ENTITY: self.get_property(ATTR_ENTITY)[0],
            ATTR_TYPE: self.get_property(ATTR_TYPE)[0],
            ATTR_ACTION: self.get_property(ATTR_ACTION)[0],
            ATTR_DATA: self.get_property(ATTR_DATA),
        }
        return Event(EVENT_REACT_ACTION, data, context=context)


class ReactionHandler(RuntimeHandler):
    enabled: bool = False

    def __init__(self, runtime: WorkflowRuntime, reactor: Reactor, index: int, tctx: TemplateContext):
        super().__init__(True, runtime, reactor, tctx)
        
        self.reactor = reactor
        self.index = index
        # self.data_handler = DynamicDataHandler(True, runtime, reactor.data, tctx)
        
        # self.init_attr(True, ATTR_ENTITY, PROP_TYPE_STR)
        # self.init_attr(True, ATTR_TYPE, PROP_TYPE_STR)
        # self.init_attr(True, ATTR_ACTION, PROP_TYPE_STR)
        # self.init_attr(True, ATTR_RESET_WORKFLOW, PROP_TYPE_STR)
        # self.init_attr(True, ATTR_DELAY, PROP_TYPE_INT)
        # self.init_attr(True, ATTR_CONDITION, PROP_TYPE_BOOL, True)

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
    async def async_handle(self, wctx: WorkflowRunContext):
        template_context_data_provider = ActorTemplateContextDataProvider(self._react, wctx.event_reader)
        
        rendered_reactor = self.jitter.render(template_context_data_provider)

        # reactor_data = self.get_jitter_prop(ATTR_DATA)
        reactor_data = self.value_container.data if hasattr(self.value_container, ATTR_DATA) else None

        wctx.trace_variables_set_reactor_data(reactor_data)
        
        with trace_path(TRACE_PATH_CONDITION):
            condition_result = self.jit_render(ATTR_CONDITION, template_context_data_provider, True)
            if self.get_property_type(ATTR_CONDITION) == PROP_TYPE_TEMPLATE:
                with trace_node(wctx.trace_variables):
                    trace_set_result(result=condition_result)
            if not condition_result:
                self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{self.reactor.id}' skipping (condition false)")
                return

        with trace_path(TRACE_PATH_EVENT):
            with trace_node(wctx.trace_variables):
                if self.reactor.forward_action:
                    # Don't forward toggle actions as they are always accompanied by other actions which will be forwarded
                    if wctx.event_reader.action == ACTION_TOGGLE:
                        self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{wctx.actx.actor_id}' skipping reactor (action 'toggle' with forward_action): '{self.reactor.id}'")
                        trace_set_result(message="Skipped, toggle with forward-action")
                        return
                    # Don't forward availabililty actions as reactors don't support them
                    if wctx.event_reader.action == ACTION_AVAILABLE or wctx.event_reader.action == ACTION_UNAVAILABLE:
                        self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{wctx.actx.actor_id}' skipping reactor (availability action with forward_action): '{self.reactor.id}'")
                        trace_set_result(message="Skipped, availability action with forward_action")
                        return
                    

                reactor_entity = self.jit_render(ATTR_ENTITY, template_context_data_provider)
                reactor_type = self.jit_render(ATTR_TYPE, template_context_data_provider)
                reactor_action = [wctx.event_reader.action] if self.reactor.forward_action else self.jit_render(ATTR_ACTION, template_context_data_provider)

                for item in product(reactor_entity, reactor_type, reactor_action):
                    test = 1

                reaction = ReactReaction(self.runtime.react)
                reaction.data.workflow_id = self.runtime.workflow_config.id
                reaction.data.actor_id = wctx.actx.actor_id
                reaction.data.actor_entity = wctx.event_reader.entity
                reaction.data.actor_type = wctx.event_reader.type
                reaction.data.actor_action = wctx.event_reader.action
                reaction.data.reactor_id = self.reactor.id
                reaction.data.reactor_entity = reactor_entity
                reaction.data.reactor_type = reactor_type
                reaction.data.reactor_action = reactor_action
                reaction.data.reset_workflow = self.jit_render(ATTR_RESET_WORKFLOW, template_context_data_provider)
                reaction.data.overwrite = self.reactor.overwrite
                reaction.data.datetime = calculate_reaction_datetime(self.reactor.timing, self.reactor.schedule, self.jit_render(ATTR_DELAY, template_context_data_provider))
                reaction.data.data = reactor_data

                self.runtime.react.log.info(f"ReactionHandler: '{self.runtime.workflow_config.id}'.'{self.reactor.id}' sending reaction: {format_data(entity=reaction.data.reactor_entity, type=reaction.data.reactor_type, action=reaction.data.reactor_action, overwrite=reaction.data.overwrite, reset_workflow=reaction.data.reset_workflow)}")
                self.runtime.react.reactions.add(reaction)
                async_dispatcher_send(self.runtime.react.hass, SIGNAL_DISPATCH, reaction.data.id)

                trace_set_result(reaction=reaction.data.to_json())


class WorkflowRunContext:
    actx: ActionContext = None
    event_reader: ActionEventDataReader = None
    trace_variables: dict = None


    def __init__(self, react: ReactBase, workflow_config: Workflow, variable_handler: DynamicDataHandler, actx: ActionContext, event_reader: ActionEventDataReader) -> None:
        self.react = react
        self.workflow_config = workflow_config
        self.variable_handler = variable_handler
        self.actx = actx
        self.event_reader = event_reader
        self.trace_variables = {}


    def trace_variables_init(self):
        # Init run variables
        this = None
        if state := self.react.hass.states.get(self.workflow_config.entity_id):
            this = state.as_dict()
        self.trace_variables = {
            ATTR_THIS: this,
            ATTR_VARIABLES: self.variable_handler.as_trace_dict(),
            ATTR_ACTOR: {
                ATTR_ID: self.actx.actor_id, 
                ATTR_DATA: self.event_reader.to_dict(),
                ATTR_CONTEXT: self.event_reader.hass_context
            }
        }

    def trace_variables_set_hass_context(self):
        self.trace_variables[ATTR_CONTEXT] = self.event_reader.hass_context


    def trace_variables_set_reactor_data(self, reactor_data: dict):
        self.trace_variables[ATTR_REACTOR] = {
            ATTR_DATA: reactor_data
        }
        

    def create_hass_run_context(self):
        parent_id = None if self.event_reader.hass_context is None else self.event_reader.hass_context.id
        self.hass_run_context = Context(parent_id=parent_id)


    def create_trace_actor_path(self):
        return f"{TRACE_PATH_ACTOR}/{str(self.actx.index)}"


class WorkflowRun:
    id: str = None
    wctx: WorkflowRunContext = None
    reactor_handlers: list[ReactionHandler] = None
    trace: Union[ReactTrace, None] = None

    def __init__(self, 
        wctx: WorkflowRunContext,
        reactor_handlers: list[ReactionHandler]
    ) -> None:
        self.id = ulid_util.ulid_hex()
        self.wctx = wctx
        self.reactor_handlers = reactor_handlers


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
                # Trace the trigger part 
                with trace_path(TRACE_PATH_TRIGGER):
                    with trace_node(wctx.trace_variables):
                        pass
                with trace_path(TRACE_PATH_CONDITION):
                    result = wctx.actx.condition
                    if wctx.actx.condition_type == PROP_TYPE_TEMPLATE:
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
        self.react.log.info(f"ActionHandler: '{self.workflow_config.id}'.'{actor_handler.actor.id}' receiving action: {format_data(entity=wctx.event_reader.entity, type=wctx.event_reader.type, action=wctx.event_reader.action)}")
        self.last_triggered = utcnow()
        self.async_update()
        return run
