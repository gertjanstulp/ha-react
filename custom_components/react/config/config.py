from copy import deepcopy
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
    ATTR_REACTOR,
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
    ATTR_OVERWRITE,
    ATTR_PARALLEL,
    ATTR_RESET_WORKFLOW,
    ATTR_SCHEDULE,
    ATTR_SCHEDULE_AT,
    ATTR_SCHEDULE_WEEKDAYS,
    ATTR_STATE,
    ATTR_STENCIL,
    ATTR_TEMPLATE,
    ATTR_TYPE,
    ATTR_VARIABLES,
    ATTR_WAIT,
    ATTR_WORKFLOW_THEN,
    ATTR_WORKFLOW_WHEN,
    CONF_PLUGINS,
    CONF_STENCIL,
    CONF_TRACE,
    CONF_WORKFLOW,
    ICON,
    MONIKER_DISPATCH,
    MONIKER_RESET,
    MONIKER_TRIGGER,
    REACT_LOGGER_CONFIG,
    WORKFLOW_MODE_PARALLEL,
)

_LOGGER = get_react_logger(REACT_LOGGER_CONFIG)


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


class Ctor(CtorConfig):
    
    type_hints: dict = {ATTR_ENTITY: MultiItem}


    def __init__(self, config: dict, index: int):
        super().__init__()

        self.load(config)
    
        self.enabled: bool = False

        self.set(ATTR_ENABLED, True)
        self.set(ATTR_INDEX, index)
        if not self.id:
            self.set(ATTR_ID, str(index))


    def get_trace_config(self, moniker) -> dict:
        result = {
            ATTR_INDEX: self.get_flattened(ATTR_INDEX),
            moniker: {
                a: self.get_flattened(a)
                for a in [ATTR_ID, ATTR_ENABLED, ATTR_ENTITY, ATTR_TYPE, ATTR_ACTION]
                if self.get(a) is not None
            }
        }
        if ATTR_CONDITION in self.keys() and self.condition != None:
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
    
    def __init__(self, config: dict, index: int, workflow_id: str):
        super().__init__(config, index)
        
        self.workflow_id = workflow_id


    def get_trace_config(self) -> dict:
        return super().get_trace_config(MONIKER_TRIGGER)


class Reactor(Ctor, ReactorConfig):

    type_hints: dict = {
        ATTR_WAIT: Wait,
    }

    def __init__(self, config: dict, index: int, workflow_id: str):
        super().__init__(config, index)
        
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


ctor_type = Callable[[dict, int, str], Union[Actor, Reactor] ]


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
        
        self.errors: list[str] = []


    @property
    def is_valid(self):
        return len(self.errors) == 0


    def load(self, config: dict, stencil: dict):
        merged_config = dict_merge(stencil, config)
        self.actors: list[Actor] = self.load_items(merged_config, ATTR_WORKFLOW_WHEN, Actor)
        self.reactors: list[Reactor] = self.load_items(merged_config, ATTR_WORKFLOW_THEN, Reactor)
        if ATTR_MODE in merged_config:
            self.mode = merged_config.get(ATTR_MODE)
        self.validate()


    def validate(self):
        if not self.actors:
            self.errors.append("No actors found. A workflow must have at least one actor")
        if not self.reactors:
            self.errors.append("No reactors found. A workflow must have at least one reactor")
        for reactor in self.reactors:
            if reactor.wait :
                if reactor.wait.delay:
                    if reactor.wait.schedule:
                        self.errors.append(f"Reactor {reactor.id} has a delay and schedule. A reactor can only have one instance of either a delay or schedule")
                    if not (reactor.wait.delay.hours or reactor.wait.delay.minutes or reactor.wait.delay.seconds):
                        self.errors.append(f"Reactor {reactor.id} has a delay without timing settings. A delay must have at least one of hour, minute or second settings.")


    def load_items(self, config: dict, item_property: str, item_type: ctor_type) -> list[Union[Actor, Reactor]]:
        if not config: return []
        items_config = config.get(item_property, [])

        result = []
        for idx,item_config in enumerate(items_config):
            item: Ctor = item_type(item_config, idx, self.id)
            result.append(item)

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
        self.plugins: Union[list[Plugin], None] = None


    def load(self, react_config: ConfigType) -> None:
        plugins_raw = react_config.get(CONF_PLUGINS, {})
        self.plugins = [Plugin(plugin_raw) for plugin_raw in plugins_raw]
        test = 1


class Plugin(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.module: str = None
        self.config: DynamicData = None
        self.load(source)


class WorkflowConfiguration:

    def __init__(self):
        self.workflows: dict[str, Workflow] = None


    def load(self, react_config: ConfigType) -> None:
        
        self.config = react_config

        if self.workflows:
            _LOGGER.debug("Unloading existing react configuration")
            self.workflows = None
            self.workflow_config = None
            self.stencil_config = None

        if react_config:
            _LOGGER.debug(f"Loading react configuration")
            # _LOGGER.debug("Found react configuration, processing")

            self.stencil_config = react_config.get(CONF_STENCIL, {}) or {}
            self.workflow_config = react_config.get(CONF_WORKFLOW, {}) or {}

            self.parse_workflow_config()
        else:
            self.workflows: dict[str, Workflow] = {}
            _LOGGER.debug("No react configuration found")


    def parse_workflow_config(self):
        _LOGGER.debug("Loading react workflows")

        self.workflows: dict[str, Workflow] = {}

        if not self.workflow_config: return

        for id, config in self.workflow_config.items():
            _LOGGER.debug(f"Loading config for react.{id}")
            if not config:
                config = {}

            workflow = Workflow(id, config)
            stencil = self.get_stencil_by_name(workflow.stencil)
            workflow.load(config, stencil)
            if not workflow.is_valid:
                _LOGGER.error(f"'{id}' has invalid configuration and will not be loaded:" + '\n- '.join([""] + workflow.errors))
            self.workflows[id] = workflow


    def get_stencil_by_name(self, stencil_name) -> dict:
        result = {}
        if stencil_name and self.stencil_config:
            stencil = self.stencil_config.get(stencil_name, None)
            if stencil:
                result = stencil
            else:
                _LOGGER.error(f"Stencil not found: '{stencil_name}'")

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
    result = deepcopy(dct)
    
    for key, new in merge_dct.items():
        existing = result.get(key)
        if not existing:
            result[key] = new
        elif type(new) != type(existing):
            raise TypeError(f"Overlapping keys exist with different types: original is {type(existing)}, new value is {type(new)}")
        elif isinstance(new, dict):
            result[key] = dict_merge(existing, new)
        elif isinstance(new, list) and len(new) > 0:
            if isinstance(new[0], dict) and ATTR_ID in new[0]: 
                existing_dict = { ex.get(ATTR_ID, exidx):ex for exidx,ex in enumerate(existing) }
                new_dict = { n.get(ATTR_ID, nidx + 1000):n for nidx,n in enumerate(new) }
                result_dict = dict_merge(existing_dict, new_dict)
                result[key] = list(result_dict.values())
            else:
                for list_value in new:
                    if list_value not in existing:
                        existing.append(list_value)
        else:
            result[key] = new
    return result