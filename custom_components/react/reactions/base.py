"""Reaction"""
from __future__ import annotations

from datetime import datetime
from functools import partial

from typing import TYPE_CHECKING, Optional, Union
import attr
from homeassistant.core import CALLBACK_TYPE

from homeassistant.helpers.event import async_track_point_in_time

from ..const import (
    ACTION_AVAILABLE,
    ACTION_TOGGLE,
    ACTION_UNAVAILABLE,
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_REACTOR_ID,
    ATTR_TYPE,
    EVENT_REACT_REACTION
)

if TYPE_CHECKING:
    from ..base import ReactBase


@attr.s(auto_attribs=True)
class ReactionData:
    """ReactionData class."""

    id: str = ""
    datetime: datetime = 0
    workflow_id: str = ""
    actor_id: str = ""
    actor_entity: str = ""
    actor_type: str = ""
    actor_action: str = ""
    reactor_id: str = ""
    reactor_entity: str = ""
    reactor_type: str = ""
    reactor_action: str = ""
    reset_workflow: str = ""
    overwrite: bool = False
    forward_action: bool = False
    data: dict = {}

    def to_json(self):
        """Export to json."""
        return attr.asdict(
            self,
            # filter=lambda attr, _: attr.name not in [],
        )


class ReactReaction:

    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.data = ReactionData()
        self._cancel_callback: Union[CALLBACK_TYPE, None] = None

    
    def to_event_data(self) -> dict:
        return {
            ATTR_REACTOR_ID: self.data.reactor_id,
            ATTR_ENTITY: self.data.reactor_entity,
            ATTR_TYPE: self.data.reactor_type,
            ATTR_ACTION:  self.data.reactor_action,
            ATTR_DATA: self.data.data
        }


    def needs_sensor(self) -> bool:
        return self.data.datetime is not None


    @property
    def is_forward_action(self):
        return self.data.forward_action if self.data else False


    @property
    def is_forward_toggle(self):
        return self.is_forward_action and self.data.actor_action == ACTION_TOGGLE if self.data else False


    @property
    def is_forward_availability(self):
        return self.is_forward_action and (self.data.actor_action == ACTION_AVAILABLE or self.data.actor_action == ACTION_UNAVAILABLE) if self.data else False
        

    def schedule(self, callback: CALLBACK_TYPE, dt: datetime):
        self.cancel_schedule()
        reaction_partial = partial(callback, self)
        self._cancel_callback = async_track_point_in_time(self.react.hass, reaction_partial, dt)
    

    def cancel_schedule(self):
        if self._cancel_callback:
            self._cancel_callback()
            self._cancel_callback = None
