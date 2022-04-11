from datetime import datetime

from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later

from .. import const as co
from .config import RuntimeReactor, get as ConfigManager
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
                co.LOGGER.info("Runtime", "{} ready", self.__class__.__name__)

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
        _,actor,reactor = self.config_manager.get_workflow_metadata(reaction)
        if not reactor: 
            co.LOGGER.warn("Reaction has invalid metadata and will be removed")
            self.coordinator.delete_reaction(reaction)
            return
        
        runtime_actor = actor.to_runtime(reaction)
        runtime_reactor = reactor.to_runtime(runtime_actor)

        pass_condition = runtime_reactor.condition if hasattr(runtime_reactor, co.ATTR_CONDITION) else True
        if not pass_condition:
            co.LOGGER.info("Scheduler", "'{}'.'{}' skipping (condition false)", reaction.workflow_id, runtime_reactor.id)
            return

        if (runtime_reactor.reset_workflow):
            self.unreact(runtime_reactor, reaction)
        elif reaction.datetime:
            self.react_later(runtime_reactor, reaction)
        else:
            self.react_now(runtime_reactor, reaction)


    def unreact(self, runtime_reactor: RuntimeReactor, reaction: ReactionEntry):
        co.LOGGER.info("Scheduler", "'{}'.'{}' resetting workflow: '{}'", reaction.workflow_id, runtime_reactor.id, runtime_reactor.reset_workflow)
        self.coordinator.reset_workflow_reaction(runtime_reactor)


    def react_now(self, runtime_reactor: RuntimeReactor, reaction: ReactionEntry):
        co.LOGGER.info("Scheduler", "'{}'.'{}' firing immediate reaction: {}", reaction.workflow_id, runtime_reactor.id, co.LOGGER.format_data(entity=runtime_reactor.entity, type=runtime_reactor.type, action=runtime_reactor.action if runtime_reactor.action else reaction.action))
        self.send_event(runtime_reactor, reaction)


    def react_later(self, runtime_reactor: RuntimeReactor, reaction: ReactionEntry):
        co.LOGGER.info("Scheduler", "'{}'.'{}' scheduling reaction: {}", reaction.workflow_id, runtime_reactor.id, co.LOGGER.format_data(entity=runtime_reactor.entity, type=runtime_reactor.type, action=runtime_reactor.action, overwrite=runtime_reactor.overwrite))
        self.coordinator.add_reaction(runtime_reactor, reaction)
        

    def run(self):
        if not self.state == co.STATE_READY: return

        delayed_reactions = self.coordinator.get_reactions(datetime.now())
        if not delayed_reactions: return
        
        for id,reaction in delayed_reactions.items():
            _,actor,reactor = self.config_manager.get_workflow_metadata(reaction)
            if not reactor: 
                co.LOGGER.warn("Reaction has invalid metadata and will be removed")
                self.coordinator.delete_reaction(reaction)
                continue

            runtime_actor = actor.to_runtime(reaction)
            runtime_reactor = reactor.to_runtime(runtime_actor)

            co.LOGGER.info("Scheduler", "'{}'.'{}' firing scheduled reaction: {}", reaction.workflow_id, runtime_reactor.id, co.LOGGER.format_data(id=id, entity=runtime_reactor.entity, type=runtime_reactor.type, action=runtime_reactor.action if runtime_reactor.action else reaction.action))
            self.coordinator.delete_reaction(reaction)
            self.send_event(runtime_reactor, reaction)


    def send_event(self, runtime_reactor: RuntimeReactor, reaction: ReactionEntry):
        Dispatcher(self.hass).send_event(co.EVENT_REACT_REACTION, self.to_event_data(runtime_reactor, reaction))


    def to_event_data(self, runtime_reactor: RuntimeReactor, reaction: ReactionEntry) -> dict:
        result = {
            co.ATTR_ENTITY: runtime_reactor.entity,
            co.ATTR_TYPE: runtime_reactor.type,
        }
        if runtime_reactor.forward_action:
            result[co.ATTR_ACTION] = reaction.action
        else:
            result[co.ATTR_ACTION] = runtime_reactor.action
        return result


def get(hass: HomeAssistant) -> Scheduler:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER].scheduler
    return None
