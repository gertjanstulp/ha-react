import logging
import voluptuous as vol

from typing import Any, Union
from homeassistant.helpers import config_validation as cv
from homeassistant.const import ATTR_FRIENDLY_NAME, CONF_ICON, ATTR_ENTITY_ID, STATE_OFF, STATE_ON
from homeassistant.helpers.template import result_as_boolean

VERSION = "0.0.1"

DOMAIN = 'react'
ENTITY_ID_FORMAT = DOMAIN + '.{}'

CONF_WORKFLOW = "workflow"
CONF_STENCIL = "stencil"



ATTR_ACTOR = "actor"
ATTR_ACTORS = "actors"
ATTR_REACTOR = "reactor"
ATTR_REACTORS = "reactors"

ATTR_ID = "id"
ATTR_ENTITY = "entity"
ATTR_TYPE = "type"
ATTR_ACTION = "action"

ATTR_VARIABLES = "variables"

ATTR_WORKFLOW_ID = "workflow_id"
ATTR_STENCIL = "stencil"

ATTR_FORWARD_ACTION = "forward_action"
ATTR_RESET_WORKFLOW = "reset_workflow"
ATTR_OVERWRITE = "overwrite"

ATTR_REACTIONS = "reactions"
ATTR_REACTION_ID = "id"
ATTR_REACTION_TIMESTAMP = "timestamp"
ATTR_REACTION_DATETIME = "datetime"

ATTR_TIMING = "timing"
ATTR_DELAY = "delay"
ATTR_SCHEDULE = "schedule"
ATTR_SCHEDULE_AT = "at"
ATTR_SCHEDULE_WEEKDAYS = "weekdays"

DEVICE_REACT_NAME = "React"
DEVICE_REACT_MODEL = "React"
DEVICE_REACT_MANUFACTURER = "@gertjanstulp"

EVENT_STARTED = "react_started"
EVENT_REACT_ACTION = "ev_react_action"
EVENT_REACT_REACTION = "ev_react_reaction"
EVENT_ITEM_CREATED = "react_item_created"
EVENT_ITEM_UPDATED = "react_item_updated"
EVENT_ITEM_REMOVED = "react_item_removed"

REACTOR_SCAN_INTERVAL = 5

REACTOR_TIMING_IMMEDIATE = "immediate"
REACTOR_TIMING_DELAYED = "delayed"
REACTOR_TIMING_SCHEDULED = "scheduled"

REACTOR_WEEKDAY_MONDAY = "mon"
REACTOR_WEEKDAY_TUESDAY = "tue"
REACTOR_WEEKDAY_WEDNESDAY = "wed"
REACTOR_WEEKDAY_THURSDAY = "thu"
REACTOR_WEEKDAY_FRIDAY = "fri"
REACTOR_WEEKDAY_SATURDAY = "sat"
REACTOR_WEEKDAY_SUNDAY = "sun"

SERVICE_REMOVE_REACTION = "remove_reaction"
SERVICE_EDIT_REACTION = "edit_reaction"
SERVICE_ADD_REACTION = "add_reaction"

STATE_INIT = "init"
STATE_READY = "ready"
STATE_COMPLETED = "completed"
STATE_STOPPED = "stopped"

BINARY_SENSOR = "binary_sensor"
BINARY_SENSOR_PREFIX = "{}.".format(BINARY_SENSOR)
GROUP = "group"
GROUP_PREFIX = "{}.".format(GROUP)
SWITCH = "switch"
SWITCH_PREFIX = "{}.".format(SWITCH)
OLD_STATE = "old_state"
NEW_STATE = "new_state"

ACTION_TOGGLE = "toggle"

DEFAULT_INITIAL_STATE = True

LOGGER = logging.getLogger(__package__)


def entity(value: Any) -> str:
    """Validate device id."""
    return cv.string(value).lower()


def is_list_of_strings(obj):
    return bool(obj) and isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)


def entities(value: Union[str, list]) -> list[str]:
    if is_list_of_strings(value):
        return value
    raise vol.Invalid("Not a valid list of entities")


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


PROP_TYPE_STR = result_as_string
PROP_TYPE_INT = result_as_int
PROP_TYPE_BOOL = result_as_boolean

SCHEDULE_SCHEMA = vol.Schema({
    vol.Required(ATTR_SCHEDULE_AT) : cv.time,
    vol.Optional(ATTR_SCHEDULE_WEEKDAYS) : cv.weekdays
})


ENTITY_DATA_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY) : vol.Any(entities, cv.template),
    vol.Optional(ATTR_TYPE) : cv.template,
    vol.Optional(ATTR_ACTION) : cv.template,
})


ACTOR_SCHEMA_STENCIL = vol.Schema({
    cv.slug: ENTITY_DATA_SCHEMA,
})
ACTOR_SCHEMA_WORKFLOW = vol.Schema({
    cv.slug: ENTITY_DATA_SCHEMA,
})


REACTOR_DATA_SCHEMA = ENTITY_DATA_SCHEMA.extend(
    vol.Schema({
        vol.Optional(ATTR_TIMING) : vol.In([REACTOR_TIMING_IMMEDIATE, REACTOR_TIMING_DELAYED, REACTOR_TIMING_SCHEDULED]),
        vol.Optional(ATTR_DELAY) : cv.template,
        vol.Optional(ATTR_SCHEDULE) : SCHEDULE_SCHEMA,
        vol.Optional(ATTR_OVERWRITE) : cv.template,
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.template,
        vol.Optional(ATTR_FORWARD_ACTION): cv.template,
    }).schema
)


REACTOR_SCHEMA_STENCIL = vol.Schema({
    cv.slug: REACTOR_DATA_SCHEMA
})
REACTOR_SCHEMA_WORKFLOW = vol.Schema({
    cv.slug: REACTOR_DATA_SCHEMA
})


STENCIL_SCHEMA = vol.Schema({
    cv.slug: vol.Any({
        vol.Optional(ATTR_ACTOR) : ACTOR_SCHEMA_STENCIL,
        vol.Optional(ATTR_REACTOR) : REACTOR_SCHEMA_STENCIL,
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.string,
    }, None)
})


WORKFLOW_SCHEMA = vol.Schema({
    cv.slug: vol.Any({
        vol.Optional(ATTR_STENCIL) : cv.string,
        vol.Optional(ATTR_VARIABLES) : dict,
        vol.Optional(ATTR_ACTOR): ACTOR_SCHEMA_WORKFLOW,
        vol.Optional(ATTR_REACTOR): REACTOR_SCHEMA_WORKFLOW,
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_ICON): cv.icon,
    }, None)
})
