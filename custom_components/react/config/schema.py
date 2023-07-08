import voluptuous as vol

from homeassistant.components.trace import TRACE_CONFIG_SCHEMA
from homeassistant.const import ATTR_NAME, CONF_ICON
from homeassistant.helpers import config_validation as cv
from custom_components.react.config.fluent import ensure_entity_data

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_CONDITION,
    ATTR_DATA,
    ATTR_DELAY,
    ATTR_DELAY_HOURS,
    ATTR_DELAY_MINUTES, 
    ATTR_DELAY_SECONDS,
    ATTR_ENTITY,
    ATTR_ENTITY_GROUP,
    ATTR_FORWARD_ACTION,
    ATTR_FORWARD_DATA,
    ATTR_ID,
    ATTR_MODE,
    ATTR_OVERWRITE,
    ATTR_PLUGIN_CONFIG,
    ATTR_PLUGIN_MODULE,
    ATTR_RESET_WORKFLOW,
    ATTR_RESTART_MODE,
    ATTR_SCHEDULE,
    ATTR_SCHEDULE_AT,
    ATTR_SCHEDULE_WEEKDAYS,
    ATTR_STATE,
    ATTR_STENCIL,
    ATTR_TYPE,
    ATTR_VARIABLES,
    ATTR_WAIT,
    ATTR_WORKFLOW_THEN,
    ATTR_WORKFLOW_WHEN,
    CONF_ENTITY_GROUPS,
    CONF_FRONTEND_REPO_URL,
    CONF_PLUGINS,
    CONF_STENCIL,
    CONF_TRACE,
    CONF_WORKFLOW,
    DOMAIN,
    RESTART_MODE_ABORT,
    RESTART_MODE_FORCE,
    RESTART_MODE_RERUN,
    WORKFLOW_MODE_PARALLEL,
    WORKFLOW_MODE_QUEUED,
    WORKFLOW_MODE_RESTART,
    WORKFLOW_MODE_SINGLE,
)

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
    vol.Optional(ATTR_ENTITY_GROUP) : vol.All(cv.ensure_list, [cv.string]),
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

ENTITY_GROUPS_SCHEMA = vol.Schema({
    cv.slug: vol.All(cv.ensure_list, [cv.string])
})

# stencil schema
STENCIL_SCHEMA = vol.Schema({
    cv.slug: vol.Schema({
        vol.Optional(ATTR_MODE) : vol.In([WORKFLOW_MODE_SINGLE, WORKFLOW_MODE_RESTART, WORKFLOW_MODE_QUEUED, WORKFLOW_MODE_PARALLEL]),
        vol.Optional(ATTR_WORKFLOW_WHEN) : vol.All(cv.ensure_list, ensure_entity_data, [ENTITY_DATA_SCHEMA]),
        vol.Optional(ATTR_WORKFLOW_THEN) : vol.All(cv.ensure_list, ensure_entity_data, [REACTOR_DATA_SCHEMA]),
        vol.Optional(ATTR_RESET_WORKFLOW) : cv.string,
    })
})

# workflow schema
WORKFLOW_SCHEMA = vol.Schema({
    cv.slug: vol.Schema({
        vol.Optional(ATTR_STENCIL) : cv.string,
        vol.Optional(ATTR_MODE) : vol.In([WORKFLOW_MODE_SINGLE, WORKFLOW_MODE_RESTART, WORKFLOW_MODE_QUEUED, WORKFLOW_MODE_PARALLEL]),
        vol.Optional(ATTR_VARIABLES) : vol.All(dict),
        vol.Optional(ATTR_WORKFLOW_WHEN) : vol.All(cv.ensure_list, ensure_entity_data, [ENTITY_DATA_SCHEMA]),
        vol.Optional(ATTR_WORKFLOW_THEN) : vol.All(cv.ensure_list, ensure_entity_data, [REACTOR_DATA_SCHEMA]),
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(CONF_ICON): cv.icon,
        vol.Optional(CONF_TRACE, default={}): TRACE_CONFIG_SCHEMA,
    }, )
})

PLUGIN_SCHEMA = vol.Schema({
    vol.Required(ATTR_PLUGIN_MODULE): cv.string,
    vol.Optional(ATTR_PLUGIN_CONFIG): dict
})

REACT_SCHEMA = vol.Schema({
    vol.Optional(DOMAIN, default={}): vol.Schema({
        vol.Optional(CONF_FRONTEND_REPO_URL): cv.string,
        vol.Optional(CONF_PLUGINS): vol.All(cv.ensure_list, [PLUGIN_SCHEMA]),
        vol.Optional(CONF_WORKFLOW): vol.Any(WORKFLOW_SCHEMA, None),
        vol.Optional(CONF_STENCIL): vol.Any(STENCIL_SCHEMA, None),
        vol.Optional(CONF_ENTITY_GROUPS): vol.Any(ENTITY_GROUPS_SCHEMA, None),
    })
}, extra=vol.ALLOW_EXTRA)