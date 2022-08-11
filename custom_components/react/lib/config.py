from datetime import datetime, timedelta
from typing import Any, Callable, Union

from homeassistant.const import ATTR_FRIENDLY_NAME, ATTR_ID, CONF_ICON
from homeassistant.helpers.typing import ConfigType

from ..exceptions import ReactException
from ..utils.logger import get_react_logger
from ..utils.struct import ActorConfig, CtorConfig, DynamicData, MultiItem, ReactorConfig, ScheduleData

from ..const import (
    ATTR_ACTION,
    ATTR_ACTOR,
    ATTR_CONDITION,
    ATTR_DATA,
    ATTR_DELAY,
    ATTR_ENABLED,
    ATTR_ENTITY,
    ATTR_EVENT,
    ATTR_FORWARD_ACTION,
    ATTR_INDEX,
    ATTR_NOTIFY,
    ATTR_OVERWRITE,
    ATTR_PARALLEL,
    ATTR_REACTOR,
    ATTR_RESET_WORKFLOW,
    ATTR_SCHEDULE,
    ATTR_SCHEDULE_AT,
    ATTR_SCHEDULE_WEEKDAYS,
    ATTR_STENCIL,
    ATTR_TEMPLATE,
    ATTR_TIMING,
    ATTR_TRIGGER,
    ATTR_TYPE,
    ATTR_VARIABLES,
    CONF_ENTITY_MAPS,
    CONF_PLUGIN,
    CONF_STENCIL,
    CONF_TRACE,
    CONF_WORKFLOW,
    ENTITY_ID_FORMAT,
    REACTOR_TIMING_DELAYED,
    REACTOR_TIMING_IMMEDIATE,
    REACTOR_TIMING_SCHEDULED
)

_LOGGER = get_react_logger()


class Schedule(ScheduleData):

    def __init__(self, config: dict):
        super().__init__()
        self.load(config)


    def as_dict(self) -> dict:
        result = {
            ATTR_SCHEDULE_AT: self.at.strftime("%H:%M:%S"),
        }
        if self.weekdays:
            result[ATTR_SCHEDULE_WEEKDAYS] = self.weekdays
        return result


class Ctor(CtorConfig):
    
    type_hints: dict = {ATTR_ENTITY: MultiItem}


    def __init__(self, config: dict, id: str, moniker: str):
        super().__init__()

        self.load(config)
    
        self.id: str = None
        self.enabled: bool = False

        self.set(ATTR_ID, id)
        self.set(ATTR_ENABLED, True)
        self.moniker = moniker


    def as_dict(self, index: int) -> dict:
        result = {
            ATTR_INDEX: index,
            self.moniker: {
                a: self.get_flattened(a)
                for a in [ATTR_ID, ATTR_ENABLED, ATTR_ENTITY, ATTR_TYPE, ATTR_ACTION]
                if self.get(a) is not None
            }
        }
        if ATTR_CONDITION in self.names and self.condition != None:
            result[ATTR_CONDITION] = { ATTR_TEMPLATE: self.condition}
        if self.data is not None:
            result[self.moniker][ATTR_DATA] = self.data.as_dict()   
        return result
        

class Actor(Ctor, ActorConfig):
    
    def __init__(self, config: dict, id: str, workflow_id: str):
        super().__init__(config, id, ATTR_TRIGGER)
        
        self.workflow_id = workflow_id


class Reactor(Ctor, ReactorConfig):

    type_hints: dict = {ATTR_SCHEDULE: Schedule}

    def __init__(self, config: dict, id: str, workflow_id: str):
        super().__init__(config, id, ATTR_EVENT)
        
        self.workflow_id = workflow_id


    def as_dict(self, index: int) -> dict:
        base_dict = super().as_dict(index)
        self_dict = {
            self.moniker: {
                a: self.get_flattened(a)
                for a in [ATTR_TIMING, ATTR_DELAY, ATTR_OVERWRITE, ATTR_RESET_WORKFLOW, ATTR_FORWARD_ACTION]
                if self.get(a) not in [None, False]
            }
        }
        if self.schedule:
            self_dict[self.moniker][ATTR_SCHEDULE] = self.schedule.as_dict()

        return dict_merge(base_dict, self_dict)


ctor_type = Callable[[dict, str, str], Union[Actor, Reactor] ]


class Workflow():

    def __init__(self, workflow_id: str, config: dict):
        self.id = workflow_id
        self.entity_id = ENTITY_ID_FORMAT.format(workflow_id)
        self.stencil = config.get(ATTR_STENCIL, {})
        self.friendly_name = config.get(ATTR_FRIENDLY_NAME, None)
        self.icon = config.get(CONF_ICON, None)
        self.trace_config = config.get(CONF_TRACE, None)
        self.variables = DynamicData(config.get(ATTR_VARIABLES, {}))
        self.actors: Union[list[Actor], None] = None
        self.reactors: Union[list[Reactor], None] = None


    def load(self, config: dict, stencil: dict):
        merged_config = dict_merge(stencil, config)
        self.actors: list[Actor] = self.load_items(merged_config, ATTR_ACTOR, Actor)
        self.reactors: list[Reactor] = self.load_items(merged_config, ATTR_REACTOR, Reactor)


    def load_items(self, config: dict, item_property: str, item_type: ctor_type) -> list[Union[Actor, Reactor]]:
        if not config: return []
        items_config = config.get(item_property, {})

        result = []
        for id,item_config in items_config.items():
            item: Ctor = item_type(item_config, id, self.id)
            result.append(item)

        return result

    
    def as_dict(self, actor_id: str = None) -> dict:
        result = {
            a: getattr(self, a)
            for a in [ATTR_ID, ATTR_STENCIL, ATTR_FRIENDLY_NAME]
            if getattr(self, a) is not None
        }
        if self.variables.any:
            result[ATTR_VARIABLES] = self.variables.as_dict()
        result[ATTR_ACTOR] = []
        result[ATTR_REACTOR] = []
        for index, actor in enumerate(self.actors):
            # if (actor_id is None or
            #     not actor.is_list_item or
            #     actor.id == actor_id):
            #     result[ATTR_ACTOR].append(actor.as_dict(index))
            result[ATTR_ACTOR].append(actor.as_dict(index))
        for index, reactor in enumerate(self.reactors):
            result[ATTR_REACTOR].append(reactor.as_dict(index))

        if len(self.reactors) > 1:
            result[ATTR_PARALLEL] = "parallel"

        return result


class PluginConfiguration:

    def __init__(self) -> None:
        self.notify: Union[str, None] = None

    def load(self, react_config: ConfigType) -> None:
        plugin_config = react_config.get(CONF_PLUGIN, {})
        self.notify = plugin_config.get(ATTR_NOTIFY, None)


class WorkflowConfiguration:

    def __init__(self):
        self.workflows: dict[str, Workflow] = None


    def load(self, react_config: ConfigType) -> None:
        _LOGGER.debug(f"Config: loading react configuration")
        
        self.config = react_config

        if self.workflows:
            _LOGGER.debug("Config: unloading existing react configuration")
            self.workflows = None
            self.workflow_config = None
            self.stencil_config = None

        if react_config:
            _LOGGER.debug("Config: found react configuration, processing")

            self.entity_maps_config = react_config.get(CONF_ENTITY_MAPS, {})
            self.stencil_config = react_config.get(CONF_STENCIL, {})
            self.workflow_config = react_config.get(CONF_WORKFLOW, {})

            self.parse_workflow_config()
        else:
            self.workflows: dict[str, Workflow] = {}
            _LOGGER.debug("Config: no react configuration found")


    def parse_workflow_config(self):
        _LOGGER.debug("Config: loading react workflows")

        self.workflows: dict[str, Workflow] = {}

        for id, config in self.workflow_config.items():
            _LOGGER.debug(f"Config: '{id}' processing workflow")
            if not config:
                config = {}

            workflow = Workflow(id, config)
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
                _LOGGER.error(f"Config: Stencil not found: '{stencil_name}'")

        return result


def calculate_reaction_datetime(timing: str, schedule: Schedule = None, delay: int = 0) -> datetime:
    if (timing == REACTOR_TIMING_IMMEDIATE):
        return None
    if timing == REACTOR_TIMING_DELAYED:
        return datetime.now() + timedelta(seconds = delay)
    elif timing == REACTOR_TIMING_SCHEDULED:
        return calculate_next_schedule_hit(schedule)


def calculate_next_schedule_hit(schedule: Schedule) -> datetime:
    if not schedule or not schedule.at: return None

    at = schedule.at
    weekdays = schedule.weekdays

    now = datetime.now()
    next_try = datetime(now.year, now.month, now.day, at.hour, at.minute, at.second)

    if next_try < now:
        next_try = next_try + timedelta(days=1)

    if weekdays and weekdays.any:
        attempt = 1
        while True:
            day_name = next_try.strftime("%A")[0:3].lower()
            if day_name in weekdays:
                break
            else:
                next_try = next_try + timedelta(days=1)
                attempt += 1
                if (attempt > 7): raise ReactException("could not calculate next schedule hit")

    return next_try


def dict_merge(dct: dict, merge_dct: dict) -> dict:
    rtn_dct = dct.copy()
    
    for k, v in merge_dct.items():
        if not rtn_dct.get(k):
            rtn_dct[k] = v
        elif k in rtn_dct and type(v) != type(rtn_dct[k]):
            raise TypeError(f"Overlapping keys exist with different types: original is {type(rtn_dct[k])}, new value is {type(v)}")
        elif isinstance(rtn_dct[k], dict) and isinstance(merge_dct[k], dict):
            rtn_dct[k] = dict_merge(rtn_dct[k], merge_dct[k])
        elif isinstance(v, list):
            for list_value in v:
                if list_value not in rtn_dct[k]:
                    rtn_dct[k].append(list_value)
        else:
            rtn_dct[k] = v
    return rtn_dct