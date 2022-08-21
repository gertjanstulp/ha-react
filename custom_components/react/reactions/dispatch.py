from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import TYPE_CHECKING

import pytz

from homeassistant.helpers.event import async_track_point_in_time

from ..reactions.base import ReactReaction
from ..utils.logger import format_data

from ..const import (
    EVENT_REACT_REACTION,
)

if TYPE_CHECKING:
    from ..base import ReactBase


class ReactDispatch:
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    def dispatch(self, reaction_id: str):
        reaction = self.react.reactions.get_by_id(reaction_id)
        if not reaction:
            self.react.log.warn(f"Dispatch: Could not dispatch reaction with id '{reaction_id}', id not found")
            return
        
        if reaction.data.datetime:
            self._dispatch_later(reaction)
        else:
            self._dispatch_now(reaction)


    def force_dispatch(self, reaction_id: str, delete_reaction: bool):
        reaction = self.react.reactions.get_by_id(reaction_id)
        if not reaction:
            self.react.log.warn(f"Dispatch: Could not dispatch reaction with id '{reaction_id}', id not found")
            return
        
        self._dispatch_now(reaction, delete_reaction)


    def _dispatch_later(self, reaction: ReactReaction):
        if reaction.data.datetime < datetime.now():
            self._dispatch_now(reaction)
            return

        self.react.log.debug(f"Dispatcher: '{reaction.data.workflow_id}'.'{reaction.data.reactor_id}' scheduling reaction: {format_data(entity=reaction.data.reactor_entity, type=reaction.data.reactor_type, action=reaction.data.reactor_action, overwrite=reaction.data.overwrite, datetime=reaction.data.datetime)}")
        dt = reaction.data.datetime.astimezone(pytz.utc)
        reaction.schedule(self._dispatch_now, dt)


    def _dispatch_now(self, reaction: ReactReaction, delete_reaction: bool = True, *args):
        if reaction.data.reset_workflow:
            self._dispatch_reset(reaction)
        else:
            self._dispatch_event(reaction)
        if delete_reaction:
            self.react.reactions.delete(reaction)


    def _dispatch_reset(self, reaction: ReactReaction):
        self.react.log.debug(f"Dispatcher: '{reaction.data.workflow_id}'.'{reaction.data.reactor_id}' resetting workflow: '{reaction.data.reset_workflow}'")
        self.react.reactions.reset_workflow_reaction(reaction)


    def _dispatch_event(self, reaction: ReactReaction):
        self.react.log.debug(f"Dispatcher: '{reaction.data.workflow_id}'.'{reaction.data.reactor_id}' firing reaction: {format_data(entity=reaction.data.reactor_entity, type=reaction.data.reactor_type, action=reaction.data.reactor_action)}")
        self.react.hass.bus.async_fire(EVENT_REACT_REACTION, reaction.to_event_data())
