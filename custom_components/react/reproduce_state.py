import asyncio
import logging

from __future__ import annotations
from collections.abc import Iterable
from typing import Any, Union

from homeassistant.const import  ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_OFF, STATE_ON
from homeassistant.core import Context, HomeAssistant, State

from . import const as co


VALID_STATES = {STATE_ON, STATE_OFF}


async def _async_reproduce_state(
    hass: HomeAssistant,
    state: State,
    *,
    context: Union[Context, None] = None,
    reproduce_options: Union[dict[str, Any], None] = None) -> None:

    if (cur_state := hass.states.get(state.entity_id)) is None:
        co.LOGGER.warn("State", "Unable to find entity {}", state.entity_id)
        return

    if state.state not in VALID_STATES:
        co.LOGGER.warn("State", "Invalid state specified for {}: {}", state.entity_id, state.state)
        return

    # Return if we are already at the right state.
    if cur_state.state == state.state:
        return

    service_data = {ATTR_ENTITY_ID: state.entity_id}

    if state.state == STATE_ON:
        service = SERVICE_TURN_ON
    elif state.state == STATE_OFF:
        service = SERVICE_TURN_OFF

    await hass.services.async_call(co.DOMAIN, service, service_data, context=context, blocking=True)


async def async_reproduce_states(
    hass: HomeAssistant,
    states: Iterable[State],
    *,
    context: Union[Context, None] = None,
    reproduce_options: Union[dict[str, Any], None] = None) -> None:
    await asyncio.gather(
        *(
            _async_reproduce_state(
                hass, state, context=context, reproduce_options=reproduce_options
            )
            for state in states
        )
    )
