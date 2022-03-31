from typing import Any

from anyio import create_event
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later

from .. import const as co
from . import config as cf
from . import store as st
from . import domain_data as dom

 
class ActionEventData:
    def __init__(self, event_data: dict[str, Any] ):
        self.entity = event_data.get(co.ATTR_ENTITY, None)
        self.type = event_data.get(co.ATTR_TYPE, None)
        self.action = event_data.get(co.ATTR_ACTION, None)


    def is_match(self, actor: cf.Actor):
        if (self.entity == actor.entity and self.type == actor.type):
            if actor.action is None:
                return True   
            else:
                return self.action == actor.action


class Listener:
    def __init__(self, hass: HomeAssistant, workflow: cf.Workflow, actor: cf.Actor):
        self.hass = hass
        self.dd = dom.get_domain_data(hass)
        self.state = co.STATE_INIT
        self.workflow = workflow
        self.actor = actor

        @callback
        def handle_startup(_event):
            @callback
            def async_timer_finished(_now):
                self.state = co.STATE_READY
                async_dispatcher_send(hass, co.EVENT_STARTED)

            async_call_later(hass, 5, async_timer_finished)

        if hass.state == CoreState.running:
            handle_startup(None)
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_startup)


    def start(self):
        self.cancel_event_listen = self.hass.bus.async_listen(co.EVENT_REACT_ACTION, self.handle_react_action)


    def stop(self):
        if self.cancel_event_listen:
            self.cancel_event_listen()


    async def handle_react_action(self, event: Event):
        if not self.state == co.STATE_READY: return
        event_data = ActionEventData(event.data)
        if not event_data.is_match(self.actor): return
        
        co.LOGGER.info("Workflow '{}' reacting to action event with entity = '{}', type = '{}', action = '{}'".format(self.workflow.id, event_data.entity, event_data.type, event_data.action))

        for reactor in self.workflow.reactors.values():
            reaction = self.create_reaction(self.actor.id, event_data.action, reactor)
            await self.dd.scheduler.async_react(reaction)


    def create_reaction(self, actor_id: str, action: str, reactor: cf.Reactor):
        reaction = st.ReactionEntry(
            workflow_id = self.workflow.id,
            actor_id = actor_id,
            reactor_id = reactor.id,
            action = action,
        )
        reaction.datetime = reactor.calculate_reaction_datetime()
        reaction.sync()

        return reaction
   