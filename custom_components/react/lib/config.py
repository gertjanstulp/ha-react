from datetime import datetime, timedelta
from jinja2 import Template as JinjaTemplate
from typing import Any, Callable, Dict, Tuple, Union

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.event import TrackTemplate, TrackTemplateResult, async_track_template_result
from homeassistant.helpers.template import LoggingUndefined, Template, TemplateEnvironment
from homeassistant.helpers.typing import ConfigType

from .. import const as co
from .store import ReactionEntry
from .dispatcher import get as Dispatcher
from .common import Updatable, Unloadable, callable_type


RUNTIME_VALUES = ["actor"]


class RuntimeValueUsedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NonLoggingUndefined(LoggingUndefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        if self._undefined_name in RUNTIME_VALUES:
            raise RuntimeValueUsedError()
        else:
            raise Exception()
    

class ValidateEnv(TemplateEnvironment):
    def __init__(self, hass, limited=False, strict=False):
        super().__init__(hass, limited, strict)
        self.undefined = NonLoggingUndefined


class TemplateWatcher(Updatable):
    def __init__(self, hass: HomeAssistant, owner: Any, property: str, type_converter: Any, template: Template, variables: dict):
        super().__init__(hass)
        self.owner = owner
        self.property = property
        self.type_converter = type_converter
        self.template = template
        self.static_variables = variables

        template.hass = hass

        setattr(owner, property, None)

        self.needs_runtime_values = False
            
        def template_needs_runtime_values(template: Template, kwargs: dict):
            result = False
            if not(template.is_static):
                try:
                    validate_env = ValidateEnv(hass, False, False)
                    validate_template = validate_env.compile(template.template)
                    jinja_template = JinjaTemplate.from_code(validate_env, validate_template, validate_env.globals, None)
                    jinja_template.render(**kwargs)
                except RuntimeValueUsedError:
                    result = True
                except Exception:
                    result = False

            return result

        self.needs_runtime_values = template_needs_runtime_values(template, self.static_variables)
        self.runtime_variables = self.static_variables | (co.RUNTIME_VARIABLES if self.needs_runtime_values else {})

        self.result_info = async_track_template_result(hass, [TrackTemplate(template, self.runtime_variables)], self.async_update_template)
        self.async_remove = self.result_info.async_remove
        self.async_refresh = self.result_info.async_refresh

        self.result_info.async_refresh()


    @callback
    def async_update_template(self, event: Union[Event, None], updates: list[TrackTemplateResult]):
        if updates and len(updates) > 0:
            result = updates.pop().result
            if isinstance(result, TemplateError):
                co.LOGGER.error("Config", "Error rendering {}: {}", self.property, result)
                return

            if hasattr(self.owner, "set_property"):
                self.owner.set_property(self.property, self.type_converter(result))
            else:
                self.owner.__setattr__(self.property, self.type_converter(result))

            self.async_update()


    def runtime_value(self, additional_variables: dict):
        runtime_variables = self.static_variables | additional_variables
        result = None
        try:
            result = self.template.async_render(runtime_variables)
        except TemplateError:
            co.LOGGER("Could not evaluate runtime value for '{}'".format(self.property))
        return result


class WorkflowContext(Updatable, Unloadable):
    _on_unload: Union[list[callable_type], None] = None
    _templates_with_variables: Union[list[TemplateWatcher], None] = None


    def __init__(self, hass: HomeAssistant,  workflow_id: str) -> None:
        super().__init__(hass)
        self.hass = hass
        self.workflow_id = workflow_id
        self._templates_with_variables = []
        self.on_unload(self._templates_with_variables.clear)    # Make sure the list of watchers is cleared when context is unloaded


    def load_variables(self, variables_config: dict):
        self.variables = type('object', (), {})()
        for key,value in variables_config.items():
            if isinstance(value, Template):
                self.create_variable_template_watcher(self.variables, key, co.PROP_TYPE_SOURCE, value)
            else:
                setattr(self.variables, key, value)


    def create_template_watcher(self, owner: Any, property: str, type_converter: Any, template: Template, use_variables: bool = True):
        result = TemplateWatcher(self.hass, owner, property, type_converter, template, vars(self.variables) if use_variables else {})
        result.on_update(self.async_update)     # When the watcher gets updated the context should be updated
        self.on_unload(result.async_remove)     # When the context is unloaded the watcher should be unloaded
        if use_variables:
            self._templates_with_variables.append(result)
        return result


    def create_variable_template_watcher(self, owner: Any, property: str, type_converter: Any, template: Template):
        result = self.create_template_watcher(owner, property, type_converter, template, False)
        result.on_update(self.async_shake)      # When the watcher of a variable gets updated all depending watchers should be updated
        return result

    
    @callback
    def async_shake(self):
        for watcher in self._templates_with_variables:
            self.hass.add_job(watcher.async_refresh)


class PropertyContainer:
    def __init__(self, context: WorkflowContext):
        self.context = context
        self.watchers_with_need_for_runtime_values: dict[str, TemplateWatcher] = {}


    def init_property(self, name: str, type_converter: Any, config: dict, stencil: dict, default: Any = None):
        value = self.get_property(name, config, stencil, default)
        self.init_property_value(name, type_converter, value)


    def init_property_value(self, name: str, type_converter: Any, value: Any):
        if isinstance(value, Template):
            watcher = self.context.create_template_watcher(self, name, type_converter, value)
            if watcher.needs_runtime_values:
                self.watchers_with_need_for_runtime_values[name] = watcher
        else:
            self.set_property(name, type_converter(value))


    def get_property(self, name: str, config: dict, stencil: dict, default: Any = None):
        result = config.get(name, None) if config else None
        if not result and stencil:
            stencil_value = stencil.get(name, None)
            if isinstance(stencil_value, list):
                result = stencil_value[:]
            else:
                result = stencil_value

        if result is None:
            result = default

        return result

    
    def set_property(self, name: str, value: Any):
        if hasattr(self, name) and getattr(self, name) == value: 
            return

        setattr(self, name, value)
        entity = getattr(self, co.ATTR_ENTITY, None)
        type = getattr(self, co.ATTR_TYPE, None)
        if entity and type:
            Dispatcher(self.context.hass).send_signal(co.SIGNAL_PROPERTY_COMPLETE, entity, type)


class Schedule(PropertyContainer):
    def __init__(self, context: WorkflowContext, config: dict, stencil: dict):
        super().__init__(context)

        if not (config or stencil): return
        self.at = self.get_property(co.ATTR_SCHEDULE_AT, config, stencil)
        self.weekdays = self.get_property(co.ATTR_SCHEDULE_WEEKDAYS, config, stencil, [])


    def as_dict(self) -> dict:
        result = {
            co.ATTR_SCHEDULE_AT: self.at.strftime("%H:%M:%S"),
        }
        if self.weekdays:
            result[co.ATTR_SCHEDULE_WEEKDAYS] = self.weekdays
        return result


class Ctor(PropertyContainer):
    entity: str
    type: str
    action: str
    
    def __init__(self, context: WorkflowContext, id: str, entity: Union[str, Template]):
        super().__init__(context)
        
        self.id = id
        self.init_property_value(co.ATTR_ENTITY, co.PROP_TYPE_STR, entity)

    
    def load(self, config: Any, stencil: dict):
        self.init_property(co.ATTR_TYPE, co.PROP_TYPE_STR, config, stencil)
        self.init_property(co.ATTR_ACTION, co.PROP_TYPE_STR, config, stencil)
        self.init_property(co.ATTR_CONDITION, co.PROP_TYPE_BOOL, config, stencil, True)


    def runtime_value(self, name: str, backup: Any = None) -> Any:
        result = None
        if hasattr(self, name):
            result = getattr(self, name)
        if not result and backup and hasattr(backup, name):
            result = getattr(backup, name)
        return result


    def as_dict(self) -> dict:
        return {
            a: getattr(self, a)
            for a in [co.ATTR_ENTITY, co.ATTR_TYPE, co.ATTR_ACTION, co.ATTR_CONDITION]
            if getattr(self, a) is not None
        }
        

class RuntimeActor:
    id: str
    entity: str
    type: str
    action: str
    condition: bool


class Actor(Ctor):
    def __init__(self, context: WorkflowContext, id: str, entity: Union[str, Template]):
        super().__init__(context, id, entity)


    def load(self, config: Any, stencil: dict):
        co.LOGGER.info("Config", "'{}' loading actor: '{}'", self.context.workflow_id, self.id)
        return super().load(config, stencil)

    def to_runtime(self, reaction: ReactionEntry) -> RuntimeActor:
        result = RuntimeActor()
        for attr in [co.ATTR_ID, co.ATTR_CONDITION, co.ATTR_ENTITY, co.ATTR_TYPE, co.ATTR_ACTION]:
            setattr(result, attr, self.runtime_value(attr, reaction))
        return result


class RuntimeReactor:
    id: str
    entity: str
    type: str
    action: str
    timing: str
    delay: int
    schedule: Any
    overwrite: bool
    reset_workflow: str
    forward_action: str
    condition: bool


class Reactor(Ctor):
    timing: str
    delay: int
    overwrite: bool
    reset_workflow: str
    forward_action: bool


    def __init__(self, context: WorkflowContext, id: str, entity: Union[str, Template]):
        super().__init__(context, id, entity)


    def load(self, config: dict, stencil: dict):
        co.LOGGER.info("Config", "'{}' loading reactor: '{}'", self.context.workflow_id, self.id)
        super().load(config, stencil)

        self.timing = self.get_property(co.ATTR_TIMING, config,  stencil, 'immediate')
        self.init_property(co.ATTR_DELAY, co.PROP_TYPE_INT, config, stencil)
        self.schedule =  self.load_schedule(config, stencil)
        self.init_property(co.ATTR_OVERWRITE, co.PROP_TYPE_BOOL, config, stencil, False)
        self.init_property(co.ATTR_RESET_WORKFLOW, co.PROP_TYPE_STR, config, stencil)
        self.init_property(co.ATTR_FORWARD_ACTION, co.PROP_TYPE_BOOL, config, stencil, False)


    def load_schedule(self, config: dict, stencil: dict) -> Schedule:
        if co.ATTR_SCHEDULE in config or co.ATTR_SCHEDULE in stencil:
            return Schedule(self.context, config.get(co.ATTR_SCHEDULE, None), stencil.get(co.ATTR_SCHEDULE, None))
        return None


    def calculate_reaction_datetime(self):
        if (self.timing == co.REACTOR_TIMING_IMMEDIATE):
            return None
        if self.timing == co.REACTOR_TIMING_DELAYED:
            return datetime.now() + timedelta(seconds = self.delay)
        elif self.timing == co.REACTOR_TIMING_SCHEDULED:
            return self.calculate_next_schedule_hit()


    def calculate_next_schedule_hit(self):
        if not self.schedule or not self.schedule.at: return None

        at = self.schedule.at
        weekdays = self.schedule.weekdays

        now = datetime.now()
        next_try = datetime(now.year, now.month, now.day, at.hour, at.minute, at.second)

        if next_try < now:
            next_try = next_try + timedelta(days=1)

        if weekdays and len(weekdays) > 0:
            attempt = 1
            while True:
                day_name = next_try.strftime("%A")[0:3].lower()
                if day_name in weekdays:
                    break
                else:
                    next_try = next_try + timedelta(days=1)
                    attempt += 1
                    if (attempt > 7): raise Exception("could not calculate next schedule hit")

        return next_try


    def to_runtime(self, actor: RuntimeActor) -> RuntimeReactor:
        result = RuntimeReactor()
        for attr in [co.ATTR_ID, co.ATTR_CONDITION, co.ATTR_ENTITY, co.ATTR_TYPE, co.ATTR_ACTION, co.ATTR_TIMING, co.ATTR_DELAY, co.ATTR_SCHEDULE, co.ATTR_OVERWRITE, co.ATTR_RESET_WORKFLOW, co.ATTR_FORWARD_ACTION]:
            setattr(result, attr, self.runtime_value(attr, actor))
        return result


    def runtime_value(self, name: str, actor: Actor) -> Any:
        if name in self.watchers_with_need_for_runtime_values:
            runtime_values = {
                co.ATTR_ACTOR: actor.__dict__
            }
            return self.watchers_with_need_for_runtime_values[name].runtime_value(runtime_values)
        else:
            return super().runtime_value(name)


    def as_dict(self) -> dict:
        base_dict = super().as_dict()
        self_dict = {
            a: getattr(self, a)
            for a in [co.ATTR_TIMING, co.ATTR_DELAY, co.ATTR_OVERWRITE, co.ATTR_RESET_WORKFLOW, co.ATTR_FORWARD_ACTION]
            if getattr(self, a) is not None and getattr(self, a) != False
        }
        if self.schedule:
            self_dict[co.ATTR_SCHEDULE] = self.schedule.as_dict(),

        return base_dict | self_dict


ctor_type = Callable[[WorkflowContext, str, str], Union[Actor, Reactor] ]


class Workflow(PropertyContainer):
    def __init__(self, context: WorkflowContext, config: dict):
        super().__init__(context)
        
        self.id = context.workflow_id
        self.entity_id = co.ENTITY_ID_FORMAT.format(context.workflow_id)
        self.stencil = config.get(co.ATTR_STENCIL, None)
        self.friendly_name = config.get(co.ATTR_FRIENDLY_NAME, None)
        self.icon = config.get(co.CONF_ICON, None)


    def load(self, config, stencil):
        self.actors: dict[str, Actor] = self.load_items(config, stencil, co.ATTR_ACTOR, Actor)
        self.reactors: dict[str, Reactor] = self.load_items(config, stencil, co.ATTR_REACTOR, Reactor)


    def load_items(self, config: Any, stencil: dict, item_property: str, item_type: ctor_type) -> Dict[str, Union[Actor, Reactor]]:
        if not config: return []
        items_config = self.get_property(item_property, config, None, {})
        items_stencil = stencil.get(item_property, {})

        result = {}
        for id,item_config in items_config.items():
            item_stencil = items_stencil.get(id, {})
            self.load_entities(id, item_config, item_stencil, item_type, result)

        for id,item_stencil in items_stencil.items():
            # Check for any stencil item that is not part of the workflow yet.
            # Add an entity for each match.
            if id not in result:
                self.load_entities(id, {}, item_stencil, item_type, result)

        return result


    def load_entities(self, id: str, item_config: dict, item_stencil: dict, item_type: ctor_type, result: dict):
        entity_data = self.get_property(co.ATTR_ENTITY, item_config, item_stencil)
        if isinstance(entity_data, Template):
            self.load_entity(id, item_config, item_stencil, item_type, result, entity_data)
        elif isinstance(entity_data, list):
            is_multiple = len(entity_data) > 1
            for i,entity in enumerate(entity_data):
                item_id = "{}_{}".format(id, i) if is_multiple else id
                self.load_entity(item_id, item_config, item_stencil, item_type, result, entity)
        elif entity_data is None:
            self.load_entity(id, item_config, item_stencil, item_type, result, None)


    def load_entity(self, item_id: str, item_config: dict, item_stencil: dict, item_type: ctor_type, result: dict, entity: Union[str, Template]):
        item: Ctor = item_type(self.context, item_id, entity)
        item.load(item_config, item_stencil)
        result[item.id] = item

    
    def on_update(self, callable: callable_type) -> None:
        self.context.on_update(callable)


    def as_dict(self) -> dict:
        result = {
            a: getattr(self, a)
            for a in [co.ATTR_ID, co.ATTR_STENCIL, co.ATTR_FRIENDLY_NAME]
            if getattr(self, a) is not None
        }
        result[co.ATTR_ACTOR] = {}
        result[co.ATTR_REACTOR] = {}
        for id,actor in self.actors.items():
            result[co.ATTR_ACTOR][id] = actor.as_dict()
        for id,reactor in self.reactors.items():
            result[co.ATTR_REACTOR][id] = reactor.as_dict()

        return result


    @callback
    def async_unload(self) -> None:
        self.context.unload()


class ConfigManager:
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.workflows = None


    def load(self, config: ConfigType) -> None:
        co.LOGGER.info("Config", "loading react configuration")
        
        self.domain_config = config.get(co.DOMAIN, {})

        if self.domain_config:
            co.LOGGER.info("Config", "found react configuration, processing")

            self.stencil_config = self.domain_config.get(co.CONF_STENCIL, {})
            self.workflow_config = self.domain_config.get(co.CONF_WORKFLOW, {})

            self.parse_workflow_config(self.hass)
        else:
            self.workflows: dict[str, Workflow] = {}
            co.LOGGER.info("Config", "no react configuration found")


    def unload(self):
        co.LOGGER.info("Config", "unloading react configuration")
        if self.workflows:
            for workflow in self.workflows.values():
                workflow.async_unload()
            self.workflows = None
        self.workflow_config = None
        self.stencil_config = None
        

    def reload(self, config: ConfigType):
        self.unload()
        self.load(config)


    def parse_workflow_config(self, hass: HomeAssistant):
        co.LOGGER.info("Config", "loading react workflows")

        self.workflows: dict[str, Workflow] = {}

        for id, config in self.workflow_config.items():
            co.LOGGER.info("Config", "'{}' processing workflow", id)
            if not config:
                config = {}

            context = WorkflowContext(hass, id)
            context.load_variables(config.get(co.ATTR_VARIABLES, {}))
            workflow = Workflow(context, config)
            stencil = self.get_stencil_by_name(workflow.stencil)
            workflow.load(config, stencil)
            self.workflows[id] = workflow


    def get_stencil_by_name(self, stencil_name) -> dict:
        result = {}
        if stencil_name:
            stencil = self.stencil_config.get(stencil_name, None)
            if stencil:
                result = stencil
            else:
                co.LOGGER.error("Config", "Stencil not found: '{}'".format(stencil_name))

        return result


    def get_workflow_metadata(self, reaction: ReactionEntry) -> Tuple[Workflow, Actor, Reactor]:
        workflow = self.workflows.get(reaction.workflow_id, None)
        if workflow is None:
            co.LOGGER.warn("Config: workflow that created reaction not found: '{}'".format(reaction.id))
            return None, None, None

        actor = workflow.actors.get(reaction.actor_id, None)
        if actor is None:
            co.LOGGER.warn("Config: actor in workflow that created reaction not found: '{}'.'{}'".format(workflow.id, reaction.id))
            return None, None, None

        reactor = workflow.reactors.get(reaction.reactor_id, None)
        if reactor is None:
            co.LOGGER.warn("Config: reactor in workflow  that created reaction not found: '{}'.'{}'".format(workflow.id, reaction.id))
            return None, None, None

        return workflow, actor, reactor

    
def get(hass: HomeAssistant) -> ConfigManager:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER].config_manager
    return None
