from datetime import datetime, timedelta
from typing import Any, Callable, Dict, MutableMapping, Union

from homeassistant.const import ATTR_FRIENDLY_NAME, ATTR_ID, CONF_ICON
from homeassistant.helpers.typing import ConfigType

from ..exceptions import ReactException
from ..utils.logger import get_react_logger
from ..utils.struct import DynamicData, MultiItem

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
    CONF_IMPL,
    CONF_STENCIL,
    CONF_TRACE,
    CONF_WORKFLOW,
    ENTITY_ID_FORMAT,
    REACTOR_TIMING_DELAYED,
    REACTOR_TIMING_IMMEDIATE,
    REACTOR_TIMING_SCHEDULED
)

_LOGGER = get_react_logger()


class Schedule(DynamicData):
    at: datetime = None
    weekdays: list[str] = []

    def __init__(self, config: dict):
        super().__init__(config)


    def as_dict(self) -> dict:
        result = {
            ATTR_SCHEDULE_AT: self.at.strftime("%H:%M:%S"),
        }
        if self.weekdays:
            result[ATTR_SCHEDULE_WEEKDAYS] = self.weekdays
        return result


class Ctor(DynamicData):
    id: str = None
    enabled: bool
    is_list_item: bool
    
    entity: str = None
    type: str = None
    action: str = None
    condition: str = None
    data: DynamicData = DynamicData(None)

    type_hints: dict = {ATTR_ENTITY: MultiItem}


    def __init__(self, config: dict, id: str, moniker: str):
        super().__init__(config)

        self.id = id
        self.moniker = moniker
        self.enabled = True


    def as_dict(self, index: int) -> dict:
        result = {
            ATTR_INDEX: index,
            self.moniker: {
                a: getattr(self, a)
                for a in [ATTR_ID, ATTR_ENABLED, ATTR_ENTITY, ATTR_TYPE, ATTR_ACTION]
                if getattr(self, a) is not None
            }
        }
        condition = getattr(self, ATTR_CONDITION)
        if condition is not None:
            result[ATTR_CONDITION] = { ATTR_ENABLED: True, ATTR_TEMPLATE: condition}
        if self.data is not None:
            result[self.moniker][ATTR_DATA] = self.data.as_dict()   
        return result
        

class Actor(Ctor):
    def __init__(self, config: dict, id: str, workflow_id: str):
        super().__init__(config, id, ATTR_TRIGGER)
        self.workflow_id = workflow_id


class Reactor(Ctor):
    timing: str = REACTOR_TIMING_IMMEDIATE
    delay: Union[int, str] = None
    schedule: Schedule = None
    overwrite: Union[bool, str] = False
    reset_workflow: str = None
    forward_action: Union[bool, str] = False

    type_hints: dict = {ATTR_SCHEDULE: Schedule}

    def __init__(self, config: dict, id: str, workflow_id: str):
        super().__init__(config, id, ATTR_EVENT)
        self.workflow_id = workflow_id

    # def load(self, config: dict):
    #     _LOGGER.debug(f"Config: '{self.workflow_id}' loading reactor: '{self.id}'")
    #     super().load(config)

    #     self.timing = config.get(ATTR_TIMING, REACTOR_TIMING_IMMEDIATE)
    #     self.delay = config.get(ATTR_DELAY, None)
    #     self.schedule =  self.load_schedule(config)
    #     self.overwrite = config.get(ATTR_OVERWRITE, False)
    #     self.reset_workflow = config.get(ATTR_RESET_WORKFLOW, None)
    #     self.forward_action = config.get(ATTR_FORWARD_ACTION, False)


    # def load_schedule(self, config: dict) -> Schedule:
    #     if ATTR_SCHEDULE in config:
    #         return Schedule(config.get(ATTR_SCHEDULE, None))
    #     return None


    def as_dict(self, index: int) -> dict:
        base_dict = super().as_dict(index)
        self_dict = {
            a: getattr(self, a)
            for a in [ATTR_TIMING, ATTR_DELAY, ATTR_OVERWRITE, ATTR_RESET_WORKFLOW, ATTR_FORWARD_ACTION]
            if getattr(self, a) is not None and getattr(self, a) != False
        }
        if self.schedule:
            self_dict[ATTR_SCHEDULE] = self.schedule.as_dict()

        return base_dict | self_dict


ctor_type = Callable[[dict, str, str], Union[Actor, Reactor] ]


class Workflow():
    id: Union[str, None] = None
    entity_id: Union[str, None] = None
    stencil: Union[dict, None] = None
    friendly_name: Union[str, None] = None
    icon: Union[str, None] = None
    trace_config: Union[Any, None] = None
    variables: Union[DynamicData, None] = None
    actors: Union[list[Actor], None] = None
    reactors: Union[list[Reactor], None] = None

    def __init__(self, workflow_id: str, config: dict):
        self.id = workflow_id
        self.entity_id = ENTITY_ID_FORMAT.format(workflow_id)
        self.stencil = config.get(ATTR_STENCIL, {})
        self.friendly_name = config.get(ATTR_FRIENDLY_NAME, None)
        self.icon = config.get(CONF_ICON, None)
        self.trace_config = config.get(CONF_TRACE, None)
        self.variables = DynamicData(config.get(ATTR_VARIABLES, {}))


    def load(self, config: dict, stencil: dict):
        merged_config = dict_merge(stencil, config)
        self.actors: list[Actor] = self.load_items(merged_config, ATTR_ACTOR, Actor)
        self.reactors: list[Reactor] = self.load_items(merged_config, ATTR_REACTOR, Reactor)


    def load_items(self, config: dict, item_property: str, item_type: ctor_type) -> list[Union[Actor, Reactor]]:
        if not config: return []
        items_config = config.get(item_property, {})

        result = []
        for id,item_config in items_config.items():
            self.load_entity(id, item_config, item_type, result, False)
            # self.load_entities(id, item_config, item_type, result)

        return result


    def load_entities(self, id: str, item_config: dict, item_type: ctor_type, result: list):
        entity_data = item_config.get(ATTR_ENTITY, None)
        if isinstance(entity_data, str):
            self.load_entity(id, item_config, item_type, result, False)
        # elif isinstance(entity_data, list):
        #     is_list_item = len(entity_data) > 1
        #     for i,e in enumerate(entity_data):
        #         item_id = f"{id}_{i}" if is_list_item else id
        #         self.load_entity(item_id, item_config, item_type, result, is_list_item)
        elif entity_data is None:
            self.load_entity(id, item_config, item_type, result, False)


    def load_entity(self, item_id: str, item_config: dict, item_type: ctor_type, result: list, is_list_item: bool):
        item: Ctor = item_type(item_config, item_id, self.id)
        item.is_list_item = is_list_item
        result.append(item)

    
    def as_dict(self, actor_id: str = None) -> dict:
        result = {
            a: getattr(self, a)
            for a in [ATTR_ID, ATTR_STENCIL, ATTR_FRIENDLY_NAME]
            if getattr(self, a) is not None
        }
        if len(self.variables.names) > 0:
            result[ATTR_VARIABLES] = self.variables.as_dict()
        result[ATTR_ACTOR] = []
        result[ATTR_REACTOR] = []
        for index, actor in enumerate(self.actors):
            if (actor_id is None or
                not actor.is_list_item or
                actor.id == actor_id):
                result[ATTR_ACTOR].append(actor.as_dict(index))
        for index, reactor in enumerate(self.reactors):
            result[ATTR_REACTOR].append(reactor.as_dict(index))

        if len(self.reactors) > 1:
            result[ATTR_PARALLEL] = "parallel"

        return result


class ImplConfiguration:
    notify: Union[str, None] = None

    def __init__(self) -> None:
        pass

    def load(self, react_config: ConfigType) -> None:
        impl_config = react_config.get(CONF_IMPL, {})
        self.notify = impl_config.get(ATTR_NOTIFY, None)


class WorkflowConfiguration:
    workflows: Union[list[Workflow], None] = None

    def __init__(self):
        self.workflows = None


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

    if weekdays and len(weekdays) > 0:
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