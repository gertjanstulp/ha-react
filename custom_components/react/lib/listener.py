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
from . import event_filters as ef

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

    async def async_react(self, event: ev.BaseEvent):
        if (self.workflow.reset_workflow):
            await self.dd.reactor.async_unreact(self.workflow)
        else:
            for reaction in self.create_reactions(event):
                await self.dd.reactor.async_react(self.workflow, reaction)

    def create_reactions(self, event: ev.BaseEvent):
        result = []
        for reactor in self.workflow.reactor:
            reaction = st.ReactionEntry(
                reactor = reactor,
                reactor_type = self.workflow.reactor_type,
                workflow_id = self.workflow.id,
            )

            if self.workflow.action_forward:
                reaction.reactor_action = event.actor_action
            else:
                reaction.reactor_action = self.workflow.reactor_action
            
            reaction.reaction_datetime = self.workflow.calculate_reaction_datetime()
            
            reaction.sync()
            result.append(reaction)

        return result

class BinarySensorListener(Listener):
    def __init__(self, hass: HomeAssistant, workflow: cf.Workflow):
        super().__init__(hass, workflow)

        entity_ids = []
        for actor in workflow.actor:
            entity_ids.append('binary_sensor.{}'.format(actor))

        if workflow.actor_action == 'toggle':
            self.state_filter = ef.StateFilterToggle(entity_ids)
        elif workflow.actor_action == 'on':
            self.state_filter = ef.StateFilterOn(entity_ids)
        elif workflow.actor_action == 'off':
            self.state_filter = ef.StateFilterOff(entity_ids)
        elif workflow.action_forward:
            self.state_filter = ef.StateFilterForward(entity_ids)
        else:
            raise Exception("Invalid actor_action for workflow '{}'".format(workflow.id))

    def start(self):
        self.cancel_event_listen = self.hass.bus.async_listen(EVENT_STATE_CHANGED, self.state_changed, self.event_pre_filter)
        if self.state != co.STATE_INIT:
            self.state = co.STATE_READY

    def stop(self):
        self.state = co.STATE_STOPPED
        if self.cancel_event_listen:
            self.cancel_event_listen()

    @callback
    def event_pre_filter(self, event: Event):
        return "entity_id" in event.data and event.data["entity_id"].startswith("binary_sensor.")

    async def state_changed(self, event: Event):
        if not self.state == co.STATE_READY: return

        event_data = ev.BinarySensorEvent(event)
        if not self.state_filter.is_match(event_data): return
        
        co.LOGGER.info("Workflow '{}' reacting to change in binary_sensor '{}' from '{}' to '{}'".format(self.workflow.id, event_data.entity_id, event_data.old_state, event_data.new_state))
        
        await self.async_react(event_data)

class ActionEventListener(Listener):
    def __init__(self, hass: HomeAssistant, workflow: cf.Workflow):
        super().__init__(hass, workflow)
        self._filter = ef.ActionEventFilter(workflow)

    def start(self):
        self.cancel_event_listen = self.hass.bus.async_listen(co.EVENT_REACT_ACTION, self.handle_react_action)

    def stop(self):
        if self.cancel_event_listen:
            self.cancel_event_listen()

    async def handle_react_action(self, event: Event):
        if not self.state == co.STATE_READY: return
        
        event_data = ev.ActionEvent(**event.data)
        if not self._filter.is_match(event_data): return

        co.LOGGER.info("Workflow '{}' reacting to action event with actor = '{}', actor_type = '{}', actor_action = '{}'".format(self.workflow.id, event_data.actor, event_data.actor_type, event_data.actor_action))
        
        await self.async_react(event_data)