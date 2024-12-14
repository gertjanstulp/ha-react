from __future__ import annotations

import json
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.trace.util import async_get_trace, async_list_traces
from homeassistant.components.websocket_api import async_register_command
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.json import ExtendedJSONEncoder

from custom_components.react.base import ReactBase
from custom_components.react.const import DOMAIN
from custom_components.react.tasks.base import ReactTask, ReactTaskType


async def async_setup_task(react: ReactBase) -> Task:
    return Task(react=react)


class Task(ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.STARTUP


    async def async_execute(self) -> None:
        self.task_logger.debug("Setting up websocket commands")
        async_register_command(self.react.hass, react_get_traces)
        async_register_command(self.react.hass, react_get_trace)
        async_register_command(self.react.hass, websocket_list_runs)
        async_register_command(self.react.hass, websocket_list_reactions)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "react/trace/list",
        vol.Required("workflow_id"): cv.string,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def react_get_traces(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    react: ReactBase = hass.data.get(DOMAIN)
    workflow_id = msg.get("workflow_id")
    if workflow_id is None:
        return
    key = f"{DOMAIN}.{msg['workflow_id']}" if "workflow_id" in msg else None

    traces = await async_list_traces(hass, DOMAIN, key)

    connection.send_result(msg["id"], traces)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "react/trace/get",
        vol.Required("workflow_id"): str,
        vol.Required("run_id"): str,
    }
)
@websocket_api.async_response
async def react_get_trace(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    key = f"{DOMAIN}.{msg['workflow_id']}"
    run_id = msg["run_id"]

    try:
        requested_trace = await async_get_trace(hass, key, run_id)
    except KeyError:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "The trace could not be found"
        )
        return

    message = websocket_api.messages.result_message(msg["id"], requested_trace)

    connection.send_message(
        json.dumps(message, cls=ExtendedJSONEncoder, allow_nan=False)
    )


@websocket_api.websocket_command({vol.Required("type"): "react/run/list"})
@callback
def websocket_list_runs(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    react: ReactBase = hass.data.get(DOMAIN)
    connection.send_result(
        msg["id"],
        react.runtime.run_registry.get_all_runs()
    )


@websocket_api.websocket_command({vol.Required("type"): "react/reaction/list"})
@callback
def websocket_list_reactions(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    react: ReactBase = hass.data.get(DOMAIN)
    connection.send_result(
        msg["id"],
        react.runtime.reaction_registry.get_all_reactions()
    )
