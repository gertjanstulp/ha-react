from datetime import datetime, timedelta, timezone
from time import strptime
from typing import Callable, Union

from homeassistant.const import ATTR_ID, ATTR_NAME, CONF_ICON
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from custom_components.react.exceptions import ReactException
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import ActorConfig, CtorConfig, DelayData, DynamicData, MultiItem, ReactorConfig, ScheduleConfig, ScheduleRuntime, StateConfig, WaitConfig

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_ACTOR,
    ATTR_CONDITION,
    ATTR_DATA,
    ATTR_DELAY,
    ATTR_DELAY_HOURS,
    ATTR_DELAY_MINUTES,
    ATTR_DELAY_SECONDS,
    ATTR_ENABLED,
    ATTR_ENTITY,
    ATTR_FORWARD_ACTION,
    ATTR_FORWARD_DATA,
    ATTR_INDEX,
    ATTR_MODE,
    ATTR_NOTIFY,
    ATTR_OVERWRITE,
    ATTR_PARALLEL,
    ATTR_REACTOR,
    ATTR_RESET_WORKFLOW,
    ATTR_RESTART_MODE,
    ATTR_SCHEDULE,
    ATTR_SCHEDULE_AT,
    ATTR_SCHEDULE_WEEKDAYS,
    ATTR_STATE,
    ATTR_STENCIL,
    ATTR_TEMPLATE,
    ATTR_TYPE,
    ATTR_VARIABLES,
    ATTR_WAIT,
    CONF_ENTITY_MAPS,
    CONF_PLUGIN,
    CONF_STENCIL,
    CONF_TRACE,
    CONF_WORKFLOW,
    ICON,
    MONIKER_DISPATCH,
    MONIKER_RESET,
    MONIKER_TRIGGER,
    RESTART_MODE_ABORT,
    WORKFLOW_MODE_PARALLEL,
)

_LOGGER = get_react_logger()


class Delay(DelayData):
    def __init__(self, config: dict):
        super().__init__()
        self.load(config)


    def get_trace_config(self) -> dict:
        result = {}
        if self.seconds:
            result[ATTR_DELAY_SECONDS] = self.seconds
        if self.minutes:
            result[ATTR_DELAY_MINUTES] = self.minutes
        if self.hours:
            result[ATTR_DELAY_HOURS] = self.hours
        return result


class Schedule(ScheduleConfig):

    def __init__(self, config: dict):
        super().__init__()
        self.load(config)


    def get_trace_config(self) -> dict:
        result = {
            ATTR_SCHEDULE_AT: self.at,
        }
        if self.weekdays:
            result[ATTR_SCHEDULE_WEEKDAYS] = self.weekdays
        return result


class State(StateConfig):
    
    def __init__(self, config: dict):
        super().__init__()
        self.load(config)


    def get_trace_config(self) -> dict:
        result = {
            ATTR_CONDITION: self.condition
        }
        return result


class Wait(WaitConfig):
    type_hints: dict = {
        ATTR_SCHEDULE: Schedule,
        ATTR_DELAY: Delay,
        ATTR_STATE: State,
    }

    def __init__(self, config: dict) -> None:
        super().__init__()
        self.load(config)


    # def get_trace_config(self) -> dict:
    #     result = {}
    #     if self.state:
    #         result[ATTR_STATE] = self.state.get_trace_config()
    #     if self.delay:
    #         result[ATTR_DELAY] = self.delay.get_trace_config()
    #     if self.schedule:
    #         result[ATTR_SCHEDULE] = self.schedule.get_trace_config()
    #     return result


class Ctor(CtorConfig):
    
    type_hints: dict = {ATTR_ENTITY: MultiItem}


    def __init__(self, config: dict, id: str, index: int):
        super().__init__()

        self.load(config)
    
        self.id: str = None
        self.enabled: bool = False

        self.set(ATTR_ID, id)
        self.set(ATTR_ENABLED, True)
        self.set(ATTR_INDEX, index)


    def get_trace_config(self, moniker) -> dict:
        result = {
            ATTR_INDEX: self.get_flattened(ATTR_INDEX),
            moniker: {
                a: self.get_flattened(a)
                for a in [ATTR_ID, ATTR_ENABLED, ATTR_ENTITY, ATTR_TYPE, ATTR_ACTION]
                if self.get(a) is not None
            }
        }
        if ATTR_CONDITION in self.names and self.condition != None:
            result[ATTR_CONDITION] = { ATTR_TEMPLATE: self.condition}
        if self.data is not None:
            result_data = [ data_item.as_dict() for data_item in self.data ]
            if len(result_data) == 0:
                result_data = None
            elif len(result_data) == 1:
                result_data = result_data[0]
            result[moniker][ATTR_DATA] = result_data
        return result
        

class Actor(Ctor, ActorConfig):
    
    def __init__(self, config: dict, id: str, workflow_id: str, index: int):
        super().__init__(config, id, index)
        
        self.workflow_id = workflow_id


    def get_trace_config(self) -> dict:
        return super().get_trace_config(MONIKER_TRIGGER)


class Reactor(Ctor, ReactorConfig):

    type_hints: dict = {
        ATTR_WAIT: Wait,
    }

    def __init__(self, config: dict, id: str, workflow_id: str, index: int):
        super().__init__(config, id, index)
        
        self.workflow_id = workflow_id


    def get_trace_config(self) -> dict:
        moniker = MONIKER_RESET if self.reset_workflow else MONIKER_DISPATCH
        base_dict = super().get_trace_config(moniker)
        self_dict = {
            moniker: {
                a: self.get_flattened(a)
                for a in [ATTR_OVERWRITE, ATTR_FORWARD_ACTION, ATTR_FORWARD_DATA]
                if self.get(a) not in [None, False]
            }
        }
        
        if self.reset_workflow:
            self_dict[moniker][ATTR_RESET_WORKFLOW] = self.reset_workflow

        if self.wait:
            if self.wait.state:
                self_dict[ATTR_STATE] = self.wait.state.get_trace_config()
            if self.wait.delay is not None:
                self_dict[ATTR_DELAY] = self.wait.delay.get_trace_config()
            if self.wait.schedule:
                self_dict[ATTR_SCHEDULE] = self.wait.schedule.get_trace_config()

        return dict_merge(base_dict, self_dict)


ctor_type = Callable[[dict, str, str, int], Union[Actor, Reactor] ]


class Workflow():

    def __init__(self, workflow_id: str, config: dict):
        self.id: str = workflow_id
        self.stencil: str = config.get(ATTR_STENCIL, {})
        self.name: str = config.get(ATTR_NAME, None)
        self.icon: str = config.get(CONF_ICON, ICON)
        self.trace_config = config.get(CONF_TRACE, None)
        self.mode: str = config.get(ATTR_MODE, WORKFLOW_MODE_PARALLEL)
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
        index = 0
        for id,item_config in items_config.items():
            item: Ctor = item_type(item_config, id, self.id, index)
            result.append(item)
            index += 1

        return result

    
    def get_trace_config(self) -> dict:
        result = {
            a: getattr(self, a)
            for a in [ATTR_ID, ATTR_STENCIL, ATTR_NAME]
            if getattr(self, a) is not None
        }
        if self.variables.any:
            result[ATTR_VARIABLES] = self.variables.as_dict()
        result[ATTR_ACTOR] = [ actor.get_trace_config() for actor in self.actors ]
        result[ATTR_REACTOR] = [ reactor.get_trace_config() for reactor in self.reactors ]

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


def calculate_reaction_datetime(schedule: ScheduleRuntime = None, delay: DelayData = None) -> datetime:
    if delay:
        result = dt_util.utcnow()
        if delay.hours:
            result = result + timedelta(hours=delay.hours)
        if delay.minutes:
            result = result + timedelta(minutes=delay.minutes)
        if delay.seconds:
            result = result + timedelta(seconds=delay.seconds)
        return result
    elif schedule:
        return calculate_next_schedule_hit(schedule)
    else:
        return None


def calculate_next_schedule_hit(schedule: ScheduleRuntime) -> datetime:
    if not schedule or not schedule.at: return None

    at = strptime(schedule.at, "%H:%M:%S")
    weekdays = schedule.weekdays
    
    now_local = dt_util.now(time_zone=dt_util.DEFAULT_TIME_ZONE)
    next_try_local = datetime(now_local.year, now_local.month, now_local.day, at.tm_hour, at.tm_min, at.tm_sec, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    if next_try_local < now_local:
        next_try_local = next_try_local + timedelta(days=1)

    if weekdays and weekdays.any:
        attempt = 1
        while True:
            day_name = next_try_local.strftime("%A")[0:3].lower()
            if day_name in weekdays:
                break
            else:
                next_try_local = next_try_local + timedelta(days=1)
                attempt += 1
                if (attempt > 7): raise ReactException("could not calculate next schedule hit")

    
    return next_try_local.astimezone(timezone.utc)


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