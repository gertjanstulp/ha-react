from datetime import datetime, timedelta
# from config.custom_components.react.lib.domain_data import DomainData
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers.config_validation import entity_id
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later

from .. import const as co
from . import config as cf
from . import events as ev
from . import store as st

class Listener:
    def __init__(self, hass: HomeAssistant, workflow: cf.Workflow):
        self.hass = hass
        self.dd = hass.data[co.DOMAIN]
        self.state = co.STATE_INIT
        self.workflow = workflow

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

    async def async_react(self):
        if (self.workflow.reset_workflow):
            await self.dd.reactor.async_unreact(self.workflow)
        else:
            for reaction in self.create_reactions():
                await self.dd.reactor.async_react(self.workflow, reaction)

    def create_reactions(self):
        result = []
        for reactor in self.workflow.reactor:
            reaction = st.ReactionEntry(
                reactor = reactor,
                reactor_type = self.workflow.reactor_type,
                reactor_action = self.workflow.reactor_action,
                workflow_id = self.workflow.id,
            )
            
            if self.workflow.reactor_timing == co.REACTOR_TIMING_IMMEDIATE:
                reaction.reaction_datetime = datetime.now()
            else:
                reaction.reaction_datetime = datetime.now() + timedelta(seconds = self.workflow.reactor_delay)
            reaction.sync()
            result.append(reaction)

        return result

class BinarySensorListener(Listener):
    def __init__(self, hass: HomeAssistant, workflow: cf.Workflow) -> None:
        super().__init__(hass, workflow)

        entity_ids = []
        for actor in workflow.actor:
            entity_ids.append('binary_sensor.{}'.format(actor))

        if workflow.actor_action == 'toggle':
            self.state_filter = StateFilterToggle(entity_ids)
        elif workflow.actor_action == 'on':
            self.state_filter = StateFilterOn(entity_ids)
        elif workflow.actor_action == 'off':
            self.state_filter = StateFilterOff(entity_ids)
        else:
            raise Exception('Invalid actor_action for workflow {}'.format(workflow.id))

    def start(self):
        self.cancel_event_listen = self.hass.bus.async_listen(EVENT_STATE_CHANGED, self.state_changed, self.state_changed_filter)
        if self.state != co.STATE_INIT:
            self.state = co.STATE_READY

    def stop(self):
        self.state = co.STATE_STOPPED
        if self.cancel_event_listen:
            self.cancel_event_listen()

    @callback
    def state_changed_filter(self, event: Event) -> bool:
        """Handle entity_id changed filter."""
        if not self.state == co.STATE_READY: return False
        return self.state_filter.is_match(event)

    async def state_changed(self, event: Event) -> None:
        if not self.state == co.STATE_READY: return
        
        co.LOGGER.info("Workflow '{}' reacting to change in binary_sensor {}".format(self.workflow.id, self.workflow.actor))
        
        await self.async_react()
        return

class StateFilter:
    def __init__(self, entity_ids: list[str]) -> None:
        self.entity_ids = entity_ids

    def is_match(self, event: Event):
        return (
            'entity_id' in event.data and 
            event.data["entity_id"] in self.entity_ids
        )

class StateFilterToggle(StateFilter):
    def __init__(self, entity_ids: list[str]):
        super().__init__(entity_ids)

    def is_match(self, event: Event):
        return (
            super().is_match(event) and
            event.data["old_state"].state != event.data["new_state"].state
        )

class StateFilterOn(StateFilter):
    def __init__(self, entity_ids: list[str]):
        super().__init__(entity_ids)

    def is_match(self, event: Event):
        return (
            super().is_match(event) and
            event.data["old_state"].state == 'off' and
            event.data["new_state"].state == 'on'
        )

class StateFilterOff(StateFilter):
    def __init__(self, entity_ids: list[str]):
        super().__init__(entity_ids)

    def is_match(self, event: Event):
        return (
            super().is_match(event) and
            event.data["old_state"].state == 'on' and
            event.data["new_state"].state == 'off'
        )

class ActionEventListener(Listener):
    def __init__(self, hass: HomeAssistant, workflow: cf.Workflow) -> None:
        super().__init__(hass, workflow)

    def start(self):
        self.cancel_event_listen = self.hass.bus.async_listen(co.EVENT_REACT_ACTION, self.handle_react_action)

    def stop(self):
        if self.cancel_event_listen:
            self.cancel_event_listen()

    async def handle_react_action(self, event: Event):
        event_data = ev.ActionEvent(**event.data)
        if not event_data.is_match(self.workflow): return

        co.LOGGER.info("Workflow '{}' reacting to action event {}".format(self.workflow.id, event_data))
        
        await self.async_react()