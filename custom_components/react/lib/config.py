from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Union

from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template
from homeassistant.helpers.typing import ConfigType

from .. import const as co
from . import template_watcher as tw


class PropertyContainer:
    def __init__(self, hass: HomeAssistant, variables: dict):
        self.hass = hass
        self.variables = variables
        self.template_watchers: list[tw.TemplateWatcher] = []


    def init_property(self, name: str, type_converter: Any, config: dict, stencil: dict, default: Any = None):
        value = self.get_property(name, config, stencil, default)
        self.init_property_value(name, type_converter, value)


    def init_property_value(self, name: str, type_converter: Any, value: Any):
        if isinstance(value, Template):
            self.template_watchers.append(tw.TemplateWatcher(self.hass, self, name, type_converter, value, self.variables))
        else:
            setattr(self, name, type_converter(value))


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


class Schedule(PropertyContainer):
    def __init__(self, hass: HomeAssistant, variables: dict, config: dict, stencil: dict):
        super().__init__(hass, variables)

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
    def __init__(self, hass: HomeAssistant, variables: dict, id: str, entity: Union[str, Template]):
        super().__init__(hass, variables)
        
        self.id = id
        self.init_property_value(co.ATTR_ENTITY, co.PROP_TYPE_STR, entity)

    
    def load(self, config: Any, stencil: dict):
        self.init_property(co.ATTR_TYPE, co.PROP_TYPE_STR, config, stencil)
        self.init_property(co.ATTR_ACTION, co.PROP_TYPE_STR, config, stencil)


    def as_dict(self) -> dict:
        return {
            a: getattr(self, a)
            for a in [co.ATTR_ENTITY, co.ATTR_TYPE, co.ATTR_ACTION]
            if getattr(self, a) is not None
        }


    def register_entity(self, entity: Any):
        for template_watcher in self.template_watchers:
            template_watcher.register_entity(entity)
        

class Actor(Ctor):
    def __init__(self, hass: HomeAssistant, variables: dict, id: str, entity: Union[str, Template]):
        super().__init__(hass, variables, id, entity)


class Reactor(Ctor):
    def __init__(self, hass: HomeAssistant, variables: dict, id: str, entity: Union[str, Template]):
        super().__init__(hass, variables, id, entity)


    def load(self, config: dict, stencil: dict):
        super().load(config, stencil)

        self.timing = self.get_property(co.ATTR_TIMING, config,  stencil, 'immediate')
        self.init_property(co.ATTR_DELAY, co.PROP_TYPE_INT, config, stencil)
        self.schedule =  self.load_schedule(config, stencil)
        self.init_property(co.ATTR_OVERWRITE, co.PROP_TYPE_BOOL, config, stencil, False)
        self.init_property(co.ATTR_RESET_WORKFLOW, co.PROP_TYPE_STR, config, stencil)
        self.init_property(co.ATTR_FORWARD_ACTION, co.PROP_TYPE_BOOL, config, stencil, False)


    def load_schedule(self, config: dict, stencil: dict) -> Schedule:
        if co.ATTR_SCHEDULE in config or co.ATTR_SCHEDULE in stencil:
            return Schedule(self.hass, self.variables, config.get(co.ATTR_SCHEDULE, None), stencil.get(co.ATTR_SCHEDULE, None))
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


class Workflow(PropertyContainer):
    def __init__(self, hass: HomeAssistant, id: str, config: dict):
        super().__init__(hass, config.get(co.ATTR_VARIABLES, {}))
        
        self.id = id
        self.entity_id = co.ENTITY_ID_FORMAT.format(id)
        self.stencil = config.get(co.ATTR_STENCIL, None)
        self.friendly_name = config.get(co.ATTR_FRIENDLY_NAME, None)
        self.icon = config.get(co.CONF_ICON, None)


    def load(self, config, stencil):
        self.actors = self.load_items(config, stencil, co.ATTR_ACTOR, Actor)
        self.reactors = self.load_items(config, stencil, co.ATTR_REACTOR, Reactor)


    def load_items(self, config: Any, stencil: dict, item_property: str, item_type: Callable[[HomeAssistant, dict, str, str], Union[Actor, Reactor] ]) -> Dict[str, Union[Actor, Reactor]]:
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


    def load_entities(self, id: str, item_config: dict, item_stencil: dict, item_type: Callable[[HomeAssistant, dict, str, str], Union[Actor, Reactor] ], result: dict):
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

    def load_entity(self, item_id: str, item_config: dict, item_stencil: dict, item_type: Callable[[HomeAssistant, dict, str, str], Union[Actor, Reactor] ], result: dict, entity: Union[str, Template]):
        item: Ctor = item_type(self.hass, self.variables, item_id, entity)
        item.load(item_config, item_stencil)
        result[item.id] = item


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


async def load_from_config(hass: HomeAssistant, domain_config: ConfigType) -> Dict[str, Workflow]:
    co.LOGGER.info("Loading react configuration")

    if domain_config:
        co.LOGGER.info("Found react configuration, processing")

        stencil_config = domain_config.get(co.CONF_STENCIL, {})
        workflow_config = domain_config.get(co.CONF_WORKFLOW, {})

        result = await parse_workflow_config(hass, workflow_config, stencil_config)
    else:
        co.LOGGER.info("No react configuration found")
        result = {}

    return result


async def parse_workflow_config(hass: HomeAssistant, workflow_config: dict, stencils: dict) -> Dict[str, Workflow]:
    co.LOGGER.info("Loading react workflows")

    workflows = {}

    for id, config in workflow_config.items():
        co.LOGGER.info("Processing workflow '{}'".format(id))
        if not config:
            config = {}

        workflow = Workflow(hass, id, config)
        stencil = await get_stencil_by_name(stencils, workflow.stencil)
        workflow.load(config, stencil)
        workflows[id] = workflow

    return workflows


async def get_stencil_by_name(stencil_config, stencil_name) -> dict:
    result = {}
    if stencil_name:
        stencil = stencil_config.get(stencil_name, None)
        if stencil:
            result = stencil
        else:
            co.LOGGER.error("Stencil '{}' not found".format(stencil_name))

    return result
    