import logging
import voluptuous as vol

from typing import Any, Union
from homeassistant.helpers import config_validation as cv
from homeassistant.const import ATTR_FRIENDLY_NAME, CONF_ICON
from homeassistant.helpers.template import result_as_boolean
from homeassistant.components.trace import TRACE_CONFIG_SCHEMA

STARTUP = """
-------------------------------------------------------------------
React

Version: %s
This is a custom integration
If you have any issues with this you need to open an issue here:
https://github.com/gertjanstulp/ha-react/issues
-------------------------------------------------------------------
"""


# VERSION = "0.7.0"
VERSION_STORAGE = "6"
MINIMUM_HA_VERSION = "2021.9.0"

TITLE = 'React'
DOMAIN = 'react'
PACKAGE_NAME = "custom_components.react"
ENTITY_ID_FORMAT = DOMAIN + '.{}'

CONF_FRONTEND_REPO_URL = "frontend_repo_url"
CONF_WORKFLOW = "workflow"
CONF_STENCIL = "stencil"

# actor attributes
ATTR_ACTOR = "actor"
ATTR_ACTOR_ID = "actor_id"
ATTR_ACTOR_ENTITY = "actor_entity"
ATTR_ACTOR_TYPE = "actor_type"
ATTR_ACTOR_ACTION = "actor_action"

# reactor attributes
ATTR_REACTOR = "reactor"
ATTR_REACTOR_ID = "reactor_id"
ATTR_REACTOR_ENTITY = "reactor_entity"
ATTR_REACTOR_TYPE = "reactor_type"
ATTR_REACTOR_ACTION = "reactor_action"
ATTR_FORWARD_ACTION = "forward_action"
ATTR_RESET_WORKFLOW = "reset_workflow"
ATTR_OVERWRITE = "overwrite"
ATTR_TIMING = "timing"
ATTR_DELAY = "delay"
ATTR_SCHEDULE = "schedule"
# reactor schedule attributes
ATTR_SCHEDULE_AT = "at"
ATTR_SCHEDULE_WEEKDAYS = "weekdays"
# reactor timings
REACTOR_TIMING_IMMEDIATE = "immediate"
REACTOR_TIMING_DELAYED = "delayed"
REACTOR_TIMING_SCHEDULED = "scheduled"
# reactor schedule weekdays
REACTOR_WEEKDAY_MONDAY = "mon"
REACTOR_WEEKDAY_TUESDAY = "tue"
REACTOR_WEEKDAY_WEDNESDAY = "wed"
REACTOR_WEEKDAY_THURSDAY = "thu"
REACTOR_WEEKDAY_FRIDAY = "fri"
REACTOR_WEEKDAY_SATURDAY = "sat"
REACTOR_WEEKDAY_SUNDAY = "sun"

# shared actor/reactor attributes
ATTR_ENTITY = "entity"
ATTR_TYPE = "type"
ATTR_ACTION = "action"
ATTR_CONDITION = "condition"

# workflow attributes
ATTR_VARIABLES = "variables"
ATTR_WORKFLOW_ID = "workflow_id"
ATTR_STENCIL = "stencil"
CONF_TRACE = "trace"

# reaction attributes
ATTR_REACTION_DATETIME = "datetime"

# Internal attributes
ATTR_DATA = "data"
ATTR_THIS = "this"
ATTR_CONTEXT = "context"
ATTR_PARALLEL = "parallel"
ATTR_ENABLED = "enabled"
ATTR_TEMPLATE = "template"
ATTR_TRIGGER = "trigger"
ATTR_EVENT = "event"
ATTR_INDEX = "index"

# events
EVENT_REACT_ACTION = "ev_react_action"
EVENT_REACT_REACTION = "ev_react_reaction"

# signals
SIGNAL_ITEM_CREATED = "react_item_created"
SIGNAL_ITEM_UPDATED = "react_item_updated"
SIGNAL_ITEM_REMOVED = "react_item_removed"
SIGNAL_PROPERTY_COMPLETE = "signal_property_complete"
SIGNAL_REACTION_READY = "signal_reaction_ready"
SIGNAL_REACT = "signal_react_{}"
SIGNAL_DISPATCH = "dispatch"

# transformer types
BINARY_SENSOR = "binary_sensor"
BINARY_SENSOR_PREFIX = f"{BINARY_SENSOR}."
SENSOR = "sensor"
SENSOR_PREFIX = f"{SENSOR}."
GROUP = "group"
GROUP_PREFIX = f"{GROUP}."
SWITCH = "switch"
SWITCH_PREFIX = f"{SWITCH}."
MEDIAPLAYER = "media_player"
MEDIAPLAYER_PREFIX = f"{MEDIAPLAYER}."
PERSON = "person"
PERSON_PREFIX = f"{PERSON}."
DEVICE_TRACKER = "device_tracker"
DEVICE_TRACKER_PREFIX = f"{DEVICE_TRACKER}."
ALARM = "alarm_control_panel"
ALARM_PREFIX = f"{ALARM}."
INPUT_BUTTON = "input_button"
INPUT_BUTTON_PREFIX = f"{INPUT_BUTTON}."
LIGHT = "light"
LIGHT_PREFIX = f"{LIGHT}."
# transformer states
OLD_STATE = "old_state"
NEW_STATE = "new_state"
# transformer actions
ACTION_TOGGLE = "toggle"
ACTION_CHANGE = "change"
ACTION_PRESS = "press"
ACTION_AVAILABLE = "available"
ACTION_UNAVAILABLE = "unavailable"

# workflow entity settings
DEFAULT_INITIAL_STATE = True
ATTR_LAST_TRIGGERED = "last_triggered"

# trace
TRACE_PATH_CONDITION = "condition"
TRACE_PATH_TRIGGER = "trigger"
TRACE_PATH_PARALLEL = "parallel"
TRACE_PATH_EVENT = "event"
TRACE_PATH_ACTOR = "actor"
TRACE_PATH_REACTOR = "reactor"

# dynamic properties
PROP_ATTR_TYPE_POSTFIX = "_attr_type"
PROP_TYPE_TEMPLATE = "template"
PROP_TYPE_VALUE = "value"
PROP_TYPE_DEFAULT = "default"

def is_list_of_strings(obj):
    return bool(obj) and isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)


def entities(value: Union[str, list]) -> list[str]:
    if is_list_of_strings(value):
        return value
    raise vol.Invalid("Not a valid list of entities")

# template tracker type conversion
def result_as_string(value):
    if not value:
        return None
    elif isinstance(value, str):
        return value
    else:
        return str(value)

def result_as_int(value):
    if not value:
        return 0
    elif isinstance(value, int):
        result = value
    else:
        try:
            result = int(value)
        except:
            result = 0
    return result

def result_as_source(value):
    return value

PROP_TYPE_STR = result_as_string
PROP_TYPE_INT = result_as_int
PROP_TYPE_BOOL = result_as_boolean
PROP_TYPE_SOURCE = result_as_source


# schema for schedule
SCHEDULE_SCHEMA = vol.Schema({
    vol.Required(ATTR_SCHEDULE_AT) : cv.time,
    vol.Optional(ATTR_SCHEDULE_WEEKDAYS) : cv.weekdays
})

# schema for common elements of actors/reactors
ENTITY_DATA_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY) : vol.Any(entities, cv.string),
    vol.Optional(ATTR_TYPE) : cv.string,
    vol.Optional(ATTR_ACTION) : cv.string,
    vol.Optional(ATTR_CONDITION) : cv.string,
    vol.Optional(ATTR_DATA): dict,
})

# schema for reactor elements
REACTOR_DATA_SCHEMA = ENTITY_DATA_SCHEMA.extend(
    vol.Schema({
        vol.Optional(ATTR_TIMING) : vol.In([REACTOR_TIMING_IMMEDIATE, REACTOR_TIMING_DELAYED, REACTOR_TIMING_SCHEDULED]),
        vol.Optional(ATTR_DELAY) : cv.string,
        vol.Optional(ATTR_SCHEDULE) : SCHEDULE_SCHEMA,
        vol.Optional(ATTR_OVERWRITE) : cv.boolean,
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.string,
        vol.Optional(ATTR_FORWARD_ACTION): cv.boolean,
    }).schema
)

# stencil schema
STENCIL_SCHEMA = vol.Schema({
    cv.slug: vol.Any({
        vol.Optional(ATTR_ACTOR) : vol.Schema({
            cv.slug: ENTITY_DATA_SCHEMA,
        }),
        vol.Optional(ATTR_REACTOR) : vol.Schema({
            cv.slug: REACTOR_DATA_SCHEMA
        }),
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.string,
    }, None)
})

# workflow schema
WORKFLOW_SCHEMA = vol.Schema({
    cv.slug: vol.Any({
        vol.Optional(ATTR_STENCIL) : cv.string,
        vol.Optional(ATTR_VARIABLES) : vol.All(dict),
        vol.Optional(ATTR_ACTOR): vol.Schema({
            cv.slug: ENTITY_DATA_SCHEMA,
        }),
        vol.Optional(ATTR_REACTOR): vol.Schema({
            cv.slug: REACTOR_DATA_SCHEMA
        }),
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_ICON): cv.icon,
        vol.Optional(CONF_TRACE, default={}): TRACE_CONFIG_SCHEMA,
    }, None)
})
