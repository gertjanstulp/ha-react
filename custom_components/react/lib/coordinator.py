from datetime import datetime
from typing import Dict
from homeassistant.core import (
    EVENT_HOMEASSISTANT_STARTED,
    HomeAssistant, 
    CoreState,
    callback,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .. import const as co
from . import store as st
from . import domain_data as dom
from . import config as cf

class ReactionStoreCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.dd = dom.get_domain_data(hass)
        self.state = co.STATE_INIT

        super().__init__(hass, co.LOGGER, name=co.DOMAIN)

        # wait for 10 seconds after HA startup to allow entities to be initialized
        @callback
        def handle_startup(_event):
            @callback
            def async_timer_finished(_now):
                self.state = co.STATE_READY
                async_dispatcher_send(self.hass, co.EVENT_STARTED)

            async_call_later(hass, 10, async_timer_finished)

        if hass.state == CoreState.running:
            handle_startup(None)
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_startup)


    @callback
    async def async_add_reaction(self, reactor: cf.Reactor, reaction: st.ReactionEntry):
        add = True
        if reactor.overwrite:
            existing_reactions = self.dd.store.async_get_reactions_by_workflow_id(reaction.workflow_id)
            if len(existing_reactions) == 1:
                existing_reaction = existing_reactions[0]
                existing_reaction.datetime = reaction.datetime
                existing_reaction.sync(True)
                if reactor.forward_action:
                    existing_reaction.action = reaction.action
                await self.async_update_reaction(existing_reaction)
                add = False
            elif len(existing_reactions) > 1:
                for existing_reaction in existing_reactions:
                    await self.async_delete_reaction(existing_reaction)

        if add and self.dd.store.async_add_reaction(reaction):
            async_dispatcher_send(self.hass, co.EVENT_ITEM_CREATED, reaction)


    @callback
    async def async_reset_workflow_reaction(self, reactor: cf.Reactor):
        existing_reactions = self.dd.store.async_get_reactions_by_workflow_id(reactor.reset_workflow)
        if existing_reactions:
            for existing_reaction in existing_reactions:
                await self.async_delete_reaction(existing_reaction)


    @callback
    def get_reactions(self, before_datetime: datetime) -> Dict[str, st.ReactionEntry]:
        return self.dd.store.async_get_reactions(before_datetime)


    async def async_update_reaction(self, reaction: st.ReactionEntry):
        if not self.dd.store.has_reaction(reaction.id):
            return
        self.dd.store.async_update_reaction(reaction)
        async_dispatcher_send(self.hass, co.EVENT_ITEM_UPDATED, reaction.id)


    async def async_delete_reaction(self, reaction: st.ReactionEntry):
        if not self.dd.store.has_reaction(reaction.id):
            return
        self.dd.store.async_delete_reaction(reaction.id)
        async_dispatcher_send(self.hass, co.EVENT_ITEM_REMOVED, reaction.id)


    async def async_delete_config(self):
        await self.dd.store.async_delete()


    async def async_cleanup_store(self):
        for reaction in self.dd.store.reactions.values():
            workflow, actor, reactor = self.dd.get_workflow_metadata(reaction)
            if not(workflow and actor and reactor): 
                co.LOGGER.warn("Reaction {} has invalid metadata and will be removed".format(reaction.id))
                await self.async_delete_reaction(reaction)