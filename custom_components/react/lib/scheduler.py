from datetime import datetime
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import (
    CoreState,
    HomeAssistant, 
    callback
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later

from .. import const as co
from . import store as st
from . import config as cf
from . import domain_data as dom

class Scheduler():
    def __init__(self, hass: HomeAssistant):
        self._hass = hass
        self.dd = dom.get_domain_data(hass)
        self.state = co.STATE_INIT

        @callback
        def handle_startup(_event):
            @callback
            def async_timer_finished(_now):
                self.state = co.STATE_READY
                async_dispatcher_send(self._hass, co.EVENT_STARTED)

            async_call_later(hass, 5, async_timer_finished)

        if hass.state == CoreState.running:
            handle_startup(None)
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_startup)


    async def start(self):
        async def async_delay_loop(_now):
            await self.delay_run()
            self._cancel_delay_loop = async_call_later(
                self._hass,
                co.REACTOR_SCAN_INTERVAL,
                async_delay_loop,
            )

        await async_delay_loop(None)


    def stop(self):
        self.state = co.STATE_STOPPED
        if self._cancel_delay_loop:
            self._cancel_delay_loop()


    async def async_react(self, reaction: st.ReactionEntry):
        workflow, actor, reactor = self.dd.get_workflow_metadata(reaction)
        if not(workflow and actor and reactor): 
            co.LOGGER.warn("Reaction has invalid metadata and will be removed")
            self.dd.coordinator.async_delete_reaction(reaction)
            return

        if (reactor.reset_workflow):
            await self.async_unreact(reactor, reaction)
        elif reaction.datetime:
            await self.react_later(reactor, reaction)
        else:
            self.react_now(reactor, reaction)


    async def async_unreact(self, reactor: cf.Reactor, reaction: st.ReactionEntry):
        co.LOGGER.info("Workflow '{}' resetting delayed reactions for workflow '{}'".format(reaction.workflow_id, reactor.reset_workflow))
        await self.dd.coordinator.async_reset_workflow_reaction(reactor)


    def react_now(self, reactor: cf.Reactor, reaction: st.ReactionEntry):
        co.LOGGER.info("Workflow '{}' firing immediate reaction with entity = '{}', type = '{}', action = '{}', reactor = '{}'".format(reaction.workflow_id, reactor.entity, reactor.type, reactor.action if reactor.action else reaction.action, reactor.id))
        self.send_event(reactor, reaction)


    async def react_later(self, reactor: cf.Reactor, reaction: st.ReactionEntry):
        co.LOGGER.info("Workflow '{}' scheduling delayed reaction with entity = '{}', type = '{}', action = '{}', overwrite = '{}', reactor = '{}'".format(reaction.workflow_id, reactor.entity, reactor.type, reactor.action, reactor.overwrite, reactor.id))
        await self.dd.coordinator.async_add_reaction(reactor, reaction)
        

    async def delay_run(self):
        if not self.state == co.STATE_READY: return

        delayed_reactions = self.dd.coordinator.get_reactions(datetime.now())
        if not delayed_reactions: return
        
        for id,reaction in delayed_reactions.items():
            workflow, actor, reactor = self.dd.get_workflow_metadata(reaction)
            if not(workflow and actor and reactor): 
                co.LOGGER.warn("Reaction has invalid metadata and will be removed")
                await self.dd.coordinator.async_delete_reaction(reaction)
                continue

            co.LOGGER.info("Workflow '{}' firing delayed reaction with reaction_id = '{}', entity = '{}', type = '{}', action = '{}'".format(reaction.workflow_id, id, reactor.entity, reactor.type, reactor.action if reactor.action else reaction.action ))
            await self.dd.coordinator.async_delete_reaction(reaction)
            self.send_event(reactor, reaction)


    def send_event(self, reactor: cf.Reactor, reaction: st.ReactionEntry):
        self._hass.bus.async_fire(co.EVENT_REACT_REACTION, reaction.to_event_data(reactor))
