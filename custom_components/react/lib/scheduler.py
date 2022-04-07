from datetime import datetime
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import (
    CoreState,
    HomeAssistant, 
    callback
)
from homeassistant.helpers.event import async_call_later

from .. import const as co
from .config import get as ConfigManager, Reactor
from .coordinator import get as Coordinator
from .store import ReactionEntry
from .dispatcher import get as Dispatcher


class Scheduler():
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.dispatcher = Dispatcher(hass)
        self.config_manager = ConfigManager(hass)
        self.coordinator = Coordinator(hass)
        self.state = co.STATE_INIT

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


    def start(self):
        if self.state != co.STATE_INIT:
            self.state = co.STATE_READY
            
        @callback
        def async_schedule_loop(_now):
            self.run()
            self._cancel_delay_loop = async_call_later(
                self.hass,
                co.REACTOR_SCAN_INTERVAL,
                async_schedule_loop,
            )

        self.dispatcher.connect_signal(co.SIGNAL_REACTION_READY, self.async_react)
        async_schedule_loop(None)


    def stop(self):
        self.state = co.STATE_STOPPED
        if self._cancel_delay_loop:
            self._cancel_delay_loop()


    @callback
    def async_react(self, reaction: ReactionEntry):
        _,_,reactor = self.config_manager.get_workflow_metadata(reaction)
        if not reactor: 
            co.LOGGER.warn("Reaction has invalid metadata and will be removed")
            self.coordinator.delete_reaction(reaction)
            return
        
        pass_condition = reactor.condition if hasattr(reactor, co.ATTR_CONDITION) else True
        if not pass_condition:
            co.LOGGER.info("Workflow '{}' skipping reactor '{}' because its' condition evaluates to False".format(reaction.workflow_id, reactor.id))
            return

        if (reactor.reset_workflow):
            self.unreact(reactor, reaction)
        elif reaction.datetime:
            self.react_later(reactor, reaction)
        else:
            self.react_now(reactor, reaction)


    def unreact(self, reactor: Reactor, reaction: ReactionEntry):
        co.LOGGER.info("Workflow '{}' resetting delayed reactions for workflow '{}'".format(reaction.workflow_id, reactor.reset_workflow))
        self.coordinator.reset_workflow_reaction(reactor)


    def react_now(self, reactor: Reactor, reaction: ReactionEntry):
        co.LOGGER.info("Workflow '{}' firing immediate reaction with entity = '{}', type = '{}', action = '{}', reactor = '{}'".format(reaction.workflow_id, reactor.entity, reactor.type, reactor.action if reactor.action else reaction.action, reactor.id))
        self.send_event(reactor, reaction)


    def react_later(self, reactor: Reactor, reaction: ReactionEntry):
        co.LOGGER.info("Workflow '{}' scheduling delayed reaction with entity = '{}', type = '{}', action = '{}', overwrite = '{}', reactor = '{}'".format(reaction.workflow_id, reactor.entity, reactor.type, reactor.action, reactor.overwrite, reactor.id))
        self.coordinator.add_reaction(reactor, reaction)
        

    def run(self):
        if not self.state == co.STATE_READY: return

        delayed_reactions = self.coordinator.get_reactions(datetime.now())
        if not delayed_reactions: return
        
        for id,reaction in delayed_reactions.items():
            _,_,reactor = self.config_manager.get_workflow_metadata(reaction)
            if not reactor: 
                co.LOGGER.warn("Reaction has invalid metadata and will be removed")
                self.coordinator.delete_reaction(reaction)
                continue

            co.LOGGER.info("Workflow '{}' firing and removing delayed reaction with reaction_id = '{}', entity = '{}', type = '{}', action = '{}'".format(reaction.workflow_id, id, reactor.entity, reactor.type, reactor.action if reactor.action else reaction.action ))
            self.coordinator.delete_reaction(reaction)
            self.send_event(reactor, reaction)


    def send_event(self, reactor: Reactor, reaction: ReactionEntry):
        Dispatcher(self.hass).send_event(co.EVENT_REACT_REACTION, self.to_event_data(reactor, reaction))


    def to_event_data(self, reactor: Reactor, reaction: ReactionEntry) -> dict:
        result = {
            co.ATTR_ENTITY: reactor.entity,
            co.ATTR_TYPE: reactor.type,
        }
        if reactor.forward_action:
            result[co.ATTR_ACTION] = reaction.action
        else:
            result[co.ATTR_ACTION] = reactor.action
        return result


def get(hass: HomeAssistant) -> Scheduler:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER].scheduler
    return None
