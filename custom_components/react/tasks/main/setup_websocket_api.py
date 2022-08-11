from __future__ import annotations
import json
from typing import Union

from anyio import TASK_STATUS_IGNORED
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.trace import async_get_trace, async_list_traces
from homeassistant.components.websocket_api import async_register_command
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.json import ExtendedJSONEncoder

from ..base import ReactTask

from ...base import ReactBase
from ...enums import ReactStage

from ...const import (
    DOMAIN,
)


async def async_setup_task(react: ReactBase) -> TASK_STATUS_IGNORED:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Setup the React websocket API."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        
        self.stages = [ReactStage.SETUP]


    async def async_execute(self) -> None:
        """Execute the task."""
        async_register_command(self.react.hass, react_status)
        async_register_command(self.react.hass, react_subscribe)
        async_register_command(self.react.hass, react_get_traces)
        async_register_command(self.react.hass, react_get_trace)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "react/trace/list",
        vol.Required("workflow_id"): cv.string,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def react_get_traces(hass, connection, msg):
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
async def react_get_trace(hass, connection, msg):
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


@websocket_api.websocket_command({vol.Required("type"): "react/status"})
@websocket_api.require_admin
@websocket_api.async_response
async def react_status(hass, connection, msg):
    react: ReactBase = hass.data.get(DOMAIN)
    connection.send_message(
        websocket_api.result_message(
            msg["id"],
            {
                "startup": react.status.startup,
                "background_task": False,
                # "lovelace_mode": react.core.lovelace_mode,
                "reloading_data": react.status.reloading_data,
                "upgrading_all": react.status.upgrading_all,
                "disabled": react.system.disabled,
                "disabled_reason": react.system.disabled_reason,
                # "has_pending_tasks": react.queue.has_pending_tasks,
                "stage": react.stage,
            },
        )
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "react/subscribe",
        vol.Required("signal"): str,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def react_subscribe(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Handle websocket subscriptions."""

    @callback
    def forward_messages(data: Union[dict, None] = None):
        """Forward events to websocket."""
        connection.send_message(websocket_api.event_message(msg["id"], data))

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass,
        msg["signal"],
        forward_messages,
    )
    connection.send_message(websocket_api.result_message(msg["id"]))
