from datetime import datetime
from typing import Dict
from homeassistant.core import (
    EVENT_HOMEASSISTANT_STARTED,
    HomeAssistant, 
    CoreState,
    callback,
)
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .. import const as co
from .config import get as ConfigManager, Reactor
from .dispatcher import get as Dispatcher
from .store import ReactionEntry, async_get_store


class Coordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.config_manager = ConfigManager(hass)
        self.state = co.STATE_INIT

        super().__init__(hass, co.LOGGER, name=co.DOMAIN)

        # wait for 10 seconds after HA startup to allow entities to be initialized
        @callback
        def handle_startup(_event):
            @callback
            def async_timer_finished(_now):
                self.state = co.STATE_READY

            async_call_later(hass, co.HA_STARTUP_DELAY, async_timer_finished)

        hass.loop.create_task(self.async_init_store())

        if hass.state == CoreState.running:
            handle_startup(None)
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_startup)


    async def async_init_store(self) -> None:
        self.store = await async_get_store(self.hass)


    def add_reaction(self, reactor: Reactor, reaction: ReactionEntry):
        add = True
        if reactor.overwrite:
            existing_reactions = self.store.get_reactions_by_workflow_id(reaction.workflow_id)
            if len(existing_reactions) == 1:
                existing_reaction = existing_reactions[0]
                existing_reaction.datetime = reaction.datetime
                existing_reaction.sync(True)
                if reactor.forward_action:
                    existing_reaction.action = reaction.action
                self.update_reaction(existing_reaction)
                add = False
            elif len(existing_reactions) > 1:
                for existing_reaction in existing_reactions:
                    self.delete_reaction(existing_reaction)

        if add and self.store.add_reaction(reaction):
            Dispatcher(self.hass).send_signal(co.SIGNAL_ITEM_CREATED, reaction)


    def reset_workflow_reaction(self, reactor: Reactor):
        existing_reactions = self.store.get_reactions_by_workflow_id(reactor.reset_workflow)
        if existing_reactions:
            for existing_reaction in existing_reactions:
                self.delete_reaction(existing_reaction)


    def get_reactions(self, before_datetime: datetime = None) -> Dict[str, ReactionEntry]:
        return self.store.get_reactions(before_datetime)


    def get_reaction_by_id(self, id: str):
        return self.store.get_reaction_by_id(id)


    def update_reaction(self, reaction: ReactionEntry):
        if not self.store.has_reaction(reaction.id):
            return
        self.store.update_reaction(reaction)
        Dispatcher(self.hass).send_signal(co.SIGNAL_ITEM_UPDATED, reaction.id)


    def delete_reaction(self, reaction: ReactionEntry):
        if not self.store.has_reaction(reaction.id):
            return
        self.store.delete_reaction(reaction.id)
        Dispatcher(self.hass).send_signal(co.SIGNAL_ITEM_REMOVED, reaction.id)


    async def async_delete_config(self):
        await self.store.async_delete()


    def cleanup_store(self):
        for id,reaction in self.get_reactions().items():
            workflow, actor, reactor = self.config_manager.get_workflow_metadata(reaction)
            if not(workflow and actor and reactor): 
                co.LOGGER.warn("Reaction {} has invalid metadata and will be removed".format(id))
                self.delete_reaction(reaction)


def get(hass: HomeAssistant) -> Coordinator:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER].coordinator
    return None
