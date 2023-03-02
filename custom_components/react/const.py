import logging
import voluptuous as vol

from typing import Any, Union
from homeassistant.helpers import config_validation as cv
from homeassistant.const import ATTR_NAME, CONF_ICON
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
ICON = "mdi:sitemap-outline"

CONF_FRONTEND_REPO_URL = "frontend_repo_url"
CONF_ENTITY_MAPS = "entity_maps"
CONF_PLUGINS = "plugins"
CONF_WORKFLOW = "workflow"
CONF_STENCIL = "stencil"

# reaction attributes
ATTR_ID = "id"

# workflow attributes
ATTR_MODE = "mode"

# plugin config attributes
ATTR_PLUGIN_MODULE = "module"
ATTR_PLUGIN_CONFIG = "config"

ATTR_WORKFLOW_WHEN = "when"
ATTR_WORKFLOW_THEN = "then"

# actor attributes
ATTR_ACTOR = "actor"
ATTR_ACTOR_ID = "actor_id"
ATTR_ACTOR_ENTITY = "actor_entity"
ATTR_ACTOR_TYPE = "actor_type"
ATTR_ACTOR_ACTION = "actor_action"
ATTR_ACTOR_DATA = "actor_data"

# reactor attributes
ATTR_REACTOR = "reactor"
ATTR_REACTOR_ID = "reactor_id"
ATTR_REACTOR_ENTITY = "reactor_entity"
ATTR_REACTOR_TYPE = "reactor_type"
ATTR_REACTOR_ACTION = "reactor_action"
ATTR_REACTOR_DELAY = "reactor_delay"
ATTR_FORWARD_ACTION = "forward_action"
ATTR_FORWARD_DATA = "forward_data"
ATTR_RESET_WORKFLOW = "reset_workflow"
ATTR_OVERWRITE = "overwrite"
ATTR_STATE = "state"
ATTR_DELAY = "delay"
ATTR_WAIT = "wait"
ATTR_SCHEDULE = "schedule"
ATTR_RESTART_MODE = "restart_mode"
# reactor delay attributes
ATTR_DELAY_SECONDS = "seconds"
ATTR_DELAY_MINUTES = "minutes"
ATTR_DELAY_HOURS = "hours"
# reactor schedule attributes
ATTR_SCHEDULE_AT = "at"
ATTR_SCHEDULE_WEEKDAYS = "weekdays"
# reactor wait attributes
ATTR_WAIT_CONDITION = "condition"
# reactor schedule weekdays
REACTOR_WEEKDAY_MONDAY = "mon"
REACTOR_WEEKDAY_TUESDAY = "tue"
REACTOR_WEEKDAY_WEDNESDAY = "wed"
REACTOR_WEEKDAY_THURSDAY = "thu"
REACTOR_WEEKDAY_FRIDAY = "fri"
REACTOR_WEEKDAY_SATURDAY = "sat"
REACTOR_WEEKDAY_SUNDAY = "sun"
# reactor wait restart modes
RESTART_MODE_ABORT = "abort"
RESTART_MODE_FORCE = "force"
RESTART_MODE_RERUN = "rerun"

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

# Internal attributes
ATTR_DATA = "data"
ATTR_THIS = "this"
ATTR_CONTEXT = "context"
ATTR_PARALLEL = "parallel"
ATTR_ENABLED = "enabled"
ATTR_TEMPLATE = "template"
ATTR_INDEX = "index"
ATTR_TRIGGER = "trigger"
ATTR_EVENT = "event"
ATTR_TYPE_HINTS = "type_hints"

# Monikers
MONIKER_TRIGGER = "trigger"
MONIKER_DISPATCH = "dispatch"
MONIKER_RESET = "reset"

# event custom attributes
ATTR_EVENT_MESSAGE = "message"
ATTR_EVENT_FEEDBACK_ITEMS = "feedback_items"
ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK = "feedback"
ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT = "acknowledgement"
ATTR_EVENT_PLUGIN = "plugin"
ATTR_EVENT_PLUGIN_PAYLOAD = "plugin_payload"

# service attributes
ATTR_RUN_ID = "run_id"
ATTR_REACTION_ID = "reaction_id"

# trace attributes
ATTR_DONE = "done"
ATTR_REMAINING = "remaining"
ATTR_TIMESTAMP = "timestamp"
ATTR_START_TIME = "start_time"
ATTR_CREATED = "created"
ATTR_WHEN = "when"
ATTR_WAIT_TYPE = "wait_type"

# events
EVENT_REACT_ACTION = "ev_react_action"
EVENT_REACT_REACTION = "ev_react_reaction"

EVENT_RUN_REGISTRY_UPDATED = "run_registry_updated"
EVENT_REACTION_REGISTRY_UPDATED = "reaction_registry_updated"

# event payload
EVENTPAYLOAD_COMMAND_REACT = "/react"

# React types
REACT_TYPE_NOTIFY = "notify"
REACT_TYPE_TTS = "tts"
REACT_TYPE_MEDIA_PLAYER = "media_player"
REACT_TYPE_INPUT_NUMBER = "input_number"
REACT_TYPE_INPUT_TEXT = "input_text"
REACT_TYPE_INPUT_BOOLEAN = "input_boolean"

# React actions
REACT_ACTION_SEND_MESSAGE = "send_message"
REACT_ACTION_FEEDBACK = "feedback"
REACT_ACTION_FEEDBACK_RETRIEVED = "feedback_retrieved"
REACT_ACTION_CONFIRM_FEEDBACK = "confirm_feedback"
REACT_ACTION_SPEEK = "speek"

# signals
SIGNAL_ITEM_CREATED = "react_item_created"
SIGNAL_ITEM_UPDATED = "react_item_updated"
SIGNAL_ITEM_REMOVED = "react_item_removed"
SIGNAL_ACTION_HANDLER_CREATED = "signal_action_handler_created"
SIGNAL_ACTION_HANDLER_DESTROYED = "signal_action_handler_destroyed"
SIGNAL_REACTION_READY = "signal_reaction_ready"
SIGNAL_DISPATCH = "dispatch"
SIGNAL_TRACK_UPDATE = "track_update"
SIGNAL_WAIT_FINISHED = "wait_finished"
SIGNAL_JOB_RESUMED = "job_resumed"
SIGNAL_WORKFLOW_RESET = "workflow_reset"

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
INPUT_BOOLEAN = "input_boolean"
INPUT_BOOLEAN_PREFIX = f"{INPUT_BOOLEAN}."
INPUT_NUMBER = "input_number"
INPUT_NUMBER_PREFIX = f"{INPUT_NUMBER}."
INPUT_TEXT = "input_text"
INPUT_TEXT_PREFIX = f"{INPUT_TEXT}."
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
TRACE_PATH_PARALLEL = "parallel"
TRACE_PATH_ACTOR = "actor"
TRACE_PATH_REACTOR = "reactor"
TRACE_PATH_DATA = "data"
TRACE_PATH_TRIGGER = "trigger"
TRACE_PATH_DISPATCH = "dispatch"
TRACE_PATH_DELAY = "delay"
TRACE_PATH_SCHEDULE = "schedule"
TRACE_PATH_WAIT = "wait"
TRACE_PATH_RESET = "reset"
TRACE_PATH_STATE = "state"

# dynamic properties
PROP_ATTR_TYPE_POSTFIX = "_attr_type"
PROP_TYPE_TEMPLATE = "template"
PROP_TYPE_VALUE = "value"
PROP_TYPE_DEFAULT = "default"
PROP_TYPE_OBJECT = "object"
PROP_TYPE_LIST = "list"
PROP_TYPE_MULTI_ITEM = "multiitem"

# services
SERVICE_TRIGGER_WORKFLOW = "trigger_workflow"
SERVICE_TRIGGER_REACTION = "trigger_reaction"
SERVICE_DELETE_REACTION = "delete_reaction"
SERVICE_RUN_NOW = "run_now"
SERVICE_REACT_NOW = "react_now"
SERVICE_DELETE_RUN = "delete_run"

# workflow modes
WORKFLOW_MODE_SINGLE = "single"
WORKFLOW_MODE_RESTART = "restart"
WORKFLOW_MODE_QUEUED = "queued"
WORKFLOW_MODE_PARALLEL = "parallel"

# time
ACTOR_ENTITY_TIME = "time"
ACTOR_TYPE_CLOCK = "clock"
ACTOR_TYPE_PATTERN = "pattern"


def is_list_of_strings(obj):
    return bool(obj) and isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)


def list(value: str | list) -> list[str]:
    if is_list_of_strings(value):
        return value
    raise vol.Invalid("Not a valid list")

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
DELAY_SCHEMA = vol.Schema({
    vol.Optional(ATTR_DELAY_SECONDS) : vol.Any(vol.Coerce(int), cv.string),
    vol.Optional(ATTR_DELAY_MINUTES) : vol.Any(vol.Coerce(int), cv.string),
    vol.Optional(ATTR_DELAY_HOURS) : vol.Any(vol.Coerce(int), cv.string),
    vol.Optional(ATTR_RESTART_MODE) : vol.In([RESTART_MODE_ABORT, RESTART_MODE_FORCE, RESTART_MODE_RERUN]),
})

# schema for schedule
SCHEDULE_SCHEMA = vol.Schema({
    vol.Required(ATTR_SCHEDULE_AT) : cv.string,
    vol.Optional(ATTR_SCHEDULE_WEEKDAYS) : cv.weekdays,
    vol.Optional(ATTR_RESTART_MODE) : vol.In([RESTART_MODE_ABORT, RESTART_MODE_FORCE, RESTART_MODE_RERUN]),
})

STATE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_CONDITION) : cv.string,
    vol.Optional(ATTR_RESTART_MODE) : vol.In([RESTART_MODE_ABORT, RESTART_MODE_FORCE, RESTART_MODE_RERUN]),
})

WAIT_SCHEMA = vol.Schema({
    vol.Optional(ATTR_STATE) : STATE_SCHEMA,
    vol.Optional(ATTR_DELAY) : DELAY_SCHEMA,
    vol.Optional(ATTR_SCHEDULE) : SCHEDULE_SCHEMA,
})

# schema for common elements of actors/reactors
ENTITY_DATA_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ID) : cv.string,
    vol.Optional(ATTR_ENTITY) : vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(ATTR_TYPE) : vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(ATTR_ACTION) : vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(ATTR_CONDITION) : cv.string,
    vol.Optional(ATTR_DATA): vol.All(cv.ensure_list, [dict]),
})

# schema for reactor elements
REACTOR_DATA_SCHEMA = ENTITY_DATA_SCHEMA.extend(
    vol.Schema({
        vol.Optional(ATTR_OVERWRITE) : cv.boolean,
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.string,
        vol.Optional(ATTR_FORWARD_ACTION): cv.boolean,
        vol.Optional(ATTR_FORWARD_DATA): cv.boolean,
        vol.Optional(ATTR_WAIT) : WAIT_SCHEMA,
    }).schema
)

# stencil schema
STENCIL_SCHEMA = vol.Schema({
    cv.slug: vol.Schema({
        vol.Optional(ATTR_MODE) : vol.In([WORKFLOW_MODE_SINGLE, WORKFLOW_MODE_RESTART, WORKFLOW_MODE_QUEUED, WORKFLOW_MODE_PARALLEL]),
        vol.Optional(ATTR_WORKFLOW_WHEN) : vol.All(cv.ensure_list, [ENTITY_DATA_SCHEMA]),
        vol.Optional(ATTR_WORKFLOW_THEN) : vol.All(cv.ensure_list, [REACTOR_DATA_SCHEMA]),
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.string,
    })
})

# workflow schema
WORKFLOW_SCHEMA = vol.Schema({
    cv.slug: vol.Schema({
        vol.Optional(ATTR_STENCIL) : cv.string,
        vol.Optional(ATTR_MODE) : vol.In([WORKFLOW_MODE_SINGLE, WORKFLOW_MODE_RESTART, WORKFLOW_MODE_QUEUED, WORKFLOW_MODE_PARALLEL]),
        vol.Optional(ATTR_VARIABLES) : vol.All(dict),
        vol.Optional(ATTR_WORKFLOW_WHEN) : vol.All(cv.ensure_list, [ENTITY_DATA_SCHEMA]),
        vol.Optional(ATTR_WORKFLOW_THEN) : vol.All(cv.ensure_list, [REACTOR_DATA_SCHEMA]),
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(CONF_ICON): cv.icon,
        vol.Optional(CONF_TRACE, default={}): TRACE_CONFIG_SCHEMA,
    }, )
})

PLUGIN_SCHEMA = vol.Schema({
    vol.Required(ATTR_PLUGIN_MODULE): cv.string,
    vol.Optional(ATTR_PLUGIN_CONFIG): dict
})