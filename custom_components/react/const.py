import logging
import voluptuous as vol

from typing import Any, Union
from homeassistant.helpers import config_validation as cv
from homeassistant.const import ATTR_FRIENDLY_NAME, CONF_ICON, ATTR_ENTITY_ID

VERSION = "0.0.1"

DOMAIN = 'react'
ENTITY_ID_FORMAT = DOMAIN + '.{}'

CONF_WORKFLOWS = "workflows"
CONF_TEMPLATES = "templates"

ATTR_ACTOR = "actor"
ATTR_ACTOR_ACTION = "actor_action"
ATTR_ACTOR_TYPE = "actor_type"
ATTR_REACTOR = "reactor"
ATTR_REACTOR_TYPE = "reactor_type"
ATTR_REACTOR_ACTION = "reactor_action"
ATTR_REACTION_TIMESTAMP = "reaction_timestamp"
ATTR_REACTOR_TIMING = "reactor_timing"
ATTR_REACTOR_DELAY = "reactor_delay"
ATTR_REACTOR_OVERWRITE = "reactor_overwrite"
ATTR_REACTIONS = "reactions"
ATTR_REACTION_ID = "reaction_id"
ATTR_REACTION_TIMESTAMP = "reaction_timestamp"
ATTR_REACTION_DATETIME = "reaction_datetime"
ATTR_RESET_WORKFLOW = "reset_workflow"
ATTR_TEMPLATE = "template"
ATTR_TOKEN = "token"
ATTR_WORKFLOW_ID = "workflow_id"

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

SERVICE_REMOVE_REACTION = "remove_reaction"
SERVICE_EDIT_REACTION = "edit_reaction"
SERVICE_ADD_REACTION = "add_reaction"

STATE_INIT = "init"
STATE_READY = "ready"
STATE_COMPLETED = "completed"
STATE_STOPPED = "stopped"

DEFAULT_INITIAL_STATE = True

LOGGER = logging.getLogger(__package__)

def device_id(value: Any) -> str:
    """Validate device id."""
    return cv.string(value).lower()

def device_ids(value: Union[str, list]) -> 'list[str]':
    """Help validate device id's"""
    if value is None:
        raise vol.Invalid("Device IDs can not be None")
    if isinstance(value, str):
        value = [ent_id.strip() for ent_id in value.split(",")]

    validator = device_id
    return [validator(ent_id) for ent_id in value]

WORKFLOW_SCHEMA = vol.Schema({
    cv.slug: vol.Any({
        vol.Optional(ATTR_TEMPLATE) : cv.string,
        vol.Optional(ATTR_TOKEN) : cv.string,
        vol.Optional(ATTR_ACTOR): vol.Any(device_ids, None),
        vol.Optional(ATTR_ACTOR_TYPE): cv.string,
        vol.Optional(ATTR_ACTOR_ACTION): cv.string,
        vol.Optional(ATTR_REACTOR): vol.Any(device_ids, None),
        vol.Optional(ATTR_REACTOR_TYPE): cv.string,
        vol.Optional(ATTR_REACTOR_ACTION): cv.string,
        vol.Optional(ATTR_REACTOR_TIMING) : vol.In([REACTOR_TIMING_IMMEDIATE, REACTOR_TIMING_DELAYED]),
        vol.Optional(ATTR_REACTOR_DELAY) : vol.Coerce(int),
        vol.Optional(ATTR_REACTOR_OVERWRITE) : vol.Coerce(bool),
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.string,
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_ICON): cv.icon,
    }, None)
})

TEMPLATE_SCHEMA = vol.Schema({
    cv.slug: vol.Any({
        vol.Optional(ATTR_ACTOR) : vol.Any(device_ids, None),
        vol.Optional(ATTR_ACTOR_TYPE) : cv.string,
        vol.Optional(ATTR_ACTOR_ACTION) : cv.string,
        vol.Optional(ATTR_REACTOR) : vol.Any(device_ids, None),
        vol.Optional(ATTR_REACTOR_TYPE) : cv.string,
        vol.Optional(ATTR_REACTOR_ACTION) : cv.string,
        vol.Optional(ATTR_REACTOR_TIMING) : vol.In([REACTOR_TIMING_IMMEDIATE, REACTOR_TIMING_DELAYED]),
        vol.Optional(ATTR_REACTOR_DELAY) : vol.Coerce(int),
        vol.Optional(ATTR_REACTOR_OVERWRITE) : vol.Coerce(bool),
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.string,
    }, None)
})

ADD_REACTION_SCHEMA = vol.Schema({
    vol.Required(ATTR_REACTOR) : cv.string,
    vol.Required(ATTR_REACTOR_TYPE) : cv.string,
    vol.Required(ATTR_REACTOR_ACTION) : cv.string,
    vol.Required(ATTR_REACTION_TIMESTAMP) : cv.string,
})

REMOVE_REACTION_SCHEMA = vol.Schema({
    vol.Required(ATTR_REACTION_ID): cv.string
})