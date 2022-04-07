from typing import Any, Tuple

from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later

from .. import const as co
from .store import ReactionEntry
from .config import Actor, Reactor, Workflow
from .dispatcher import get as Dispatcher

 
def extract_action_event_data(event: Event) -> Tuple[str, str, str]:
    entity = event.data.get(co.ATTR_ENTITY, None)
    type = event.data.get(co.ATTR_TYPE, None)
    action = event.data.get(co.ATTR_ACTION, None)
    return entity, type, action


class ActionEventFilter:
    def __init__(self, hass: HomeAssistant, workflow_id: str, actor: Actor):
        self.hass = hass
        self.workflow_id = workflow_id
        self.actor = actor
        self.enabled = False


    @callback
    def async_is_match(self, event: Event) -> bool:
        entity, type, action = extract_action_event_data(event)

        if not self.enabled:
            co.LOGGER.info("Workflow '{}' skipping actor '{}' because the workflow is disabled".format(self.workflow_id, self.actor.id))
            return False

        result = False
        if (entity == self.actor.entity and type == self.actor.type):
            if self.actor.action is None:
                result = True   
            else:
                result = action == self.actor.action
        
        if result:
            pass_condition = self.actor.condition if hasattr(self.actor, co.ATTR_CONDITION) else True
            if not pass_condition:
                result = False
                co.LOGGER.info("Workflow '{}' skipping actor '{}' because its' condition evaluates to False".format(self.workflow_id, self.actor.id))

        return result


    def enable(self) -> None:
        self.enabled = True


    def disable(self) -> None:
        self.enabled = False


class Listener:
    def __init__(self, hass: HomeAssistant, workflow: Workflow, actor: Actor):
        self.hass = hass
        self.state = co.STATE_INIT
        self.workflow = workflow
        self.actor = actor
        self.filter = ActionEventFilter(hass, workflow.id, actor)

        @callback
        def handle_startup(_event):
            @callback
            def async_timer_finished(_now):
                self.state = co.STATE_READY

            async_call_later(hass, co.HA_STARTUP_DELAY, async_timer_finished)

        if hass.state == CoreState.running:
            handle_startup(None)
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_startup)

        Dispatcher(self.hass).connect_event(co.EVENT_REACT_ACTION, self.async_handle_react_action, self.filter.async_is_match, co.DISCONNECT_EVENT_TAG_CONFIG)


    def enable(self):
        self.filter.enable()

    
    def disable(self):
        self.filter.disable()


    @callback
    def async_handle_react_action(self, event: Event):
        if not self.state == co.STATE_READY: return
        entity, type, action = extract_action_event_data(event)
        
        co.LOGGER.info("Workflow '{}' reacting to action event with entity = '{}', type = '{}', action = '{}'".format(self.workflow.id, entity, type, action))

        for reactor in self.workflow.reactors.values():
            # Toggle action should not be forwarded, otherwise double-triggering
            # could occur (toggle and on/off actions are generated simultaneously)
            if action == co.ACTION_TOGGLE and reactor.forward_action:
                co.LOGGER.info("Workflow '{}' skipping reactor '{}' because action is 'toggle' and 'forward_action' is True".format(self.workflow.id, reactor.id))
                continue
            reaction = self.create_reaction(self.actor.id, action, reactor)
            Dispatcher(self.hass).send_signal(co.SIGNAL_REACTION_READY, reaction)


    def create_reaction(self, actor_id: str, action: str, reactor: Reactor):
        reaction = ReactionEntry(
            workflow_id = self.workflow.id,
            actor_id = actor_id,
            reactor_id = reactor.id,
            action = action,
        )
        reaction.datetime = reactor.calculate_reaction_datetime()
        reaction.sync()

        return reaction
   