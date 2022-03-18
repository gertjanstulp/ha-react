import attr
from datetime import timedelta, datetime
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import (
    CoreState,
    HomeAssistant, 
    Event,
    callback
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later
from homeassistant.util.dt import as_timestamp

from .. import const as co
from . import workflow_entities as we
from . import coordinator as cord
from . import store as st
from . import config as cf

class Reactor():
    def __init__(self, hass: HomeAssistant):
        self._hass = hass
        self.dd = hass.data[co.DOMAIN]
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
            await self._delay_run()
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

    async def async_react(self, workflow: cf.Workflow, reaction: st.ReactionEntry):
        if workflow.reactor_timing == co.REACTOR_TIMING_IMMEDIATE:
            self._react_now(workflow, reaction)
        else:
            await self._react_later(workflow, reaction)

    async def async_unreact(self, workflow: cf.Workflow):
        co.LOGGER.info("Workflow '{}' resetting delayed reactions for workflow '{}'".format(workflow.id, workflow.reset_workflow))

        await self.dd.coordinator.async_reset_workflow_reaction(workflow.reset_workflow)

    def _react_now(self, workflow: cf.Workflow, reaction: st.ReactionEntry):
        co.LOGGER.info("Workflow '{}' firing immediate reaction with reactor = '{}', reactor_type = '{}', reactor_action = '{}', action_forwarded = {}".format(workflow.id, reaction.reactor, reaction.reactor_type, reaction.reactor_action, workflow.action_forward))

        self._send_event(reaction)

    async def _react_later(self, workflow: cf.Workflow, reaction: st.ReactionEntry):
        co.LOGGER.info("Workflow '{}' scheduling delayed reaction with reactor = '{}', reactor_type = '{}', reactor_action = '{}', reactor_delay = '{}', reactor_overwrite = '{}', action_forwarded = {}".format(workflow.id, reaction.reactor, reaction.reactor_type, reaction.reactor_action, workflow.reactor_delay, workflow.reactor_overwrite, workflow.action_forward))

        await self.dd.coordinator.async_add_reaction(reaction, workflow.reactor_overwrite)
        
    async def _delay_run(self):
        if not self.state == co.STATE_READY: return

        delayed_reactions = self.dd.coordinator.get_reactions(datetime.now())
        if not delayed_reactions: return
        
        for id,reaction in delayed_reactions.items():
            co.LOGGER.info("Workflow '{}' firing delayed reaction with reaction_id = '{}', reactor = '{}', reactor_type = '{}', reactor_action = '{}'".format(reaction.workflow_id, reaction.reaction_id, reaction.reactor, reaction.reactor_type, reaction.reactor_action))
            await self.dd.coordinator.async_delete_reaction(id)
            self._send_event(reaction)

    def _send_event(self, reaction):
        self._hass.bus.async_fire(co.EVENT_REACT_REACTION, attr.asdict(reaction, filter=lambda attr, value: attr.name not in ["reaction_timestamp"]))