from datetime import datetime
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

class ReactionStoreCoordinator(DataUpdateCoordinator):
    """Define an object to hold reaction data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize."""

        self.hass = hass
        self.dd = hass.data[co.DOMAIN]
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
    async def async_add_reaction(self, reaction: st.ReactionEntry, overwrite: bool):
        """add a new reaction"""

        add = True
        if overwrite:
            existing_reactions = self.dd.store.async_get_reactions_by_workflow_id(reaction.workflow_id)
            if len(existing_reactions) == 1:
                existing_reaction = existing_reactions[0]
                existing_reaction.reaction_datetime = reaction.reaction_datetime
                existing_reaction.sync(True)
                await self.async_update_reaction(existing_reaction)
                add = False
            elif len(existing_reactions) > 1:
                for existing_reaction in existing_reactions:
                    await self.async_delete_reaction(existing_reaction)

        if add and self.dd.store.async_add_reaction(reaction):
            async_dispatcher_send(self.hass, co.EVENT_ITEM_CREATED, reaction)

    @callback
    async def async_reset_workflow_reaction(self, reset_workflow_id: str):
        """Reset the reaction for a given workflow"""

        existing_reactions = self.dd.store.async_get_reactions_by_workflow_id(reset_workflow_id)
        if existing_reactions:
            for existing_reaction in existing_reactions:
                await self.async_delete_reaction(existing_reaction)

    @callback
    def get_reactions(self, before_datetime: datetime):
        """Get all reactions before a specific datetime"""

        return self.dd.store.async_get_reactions(before_datetime)

    async def async_update_reaction(self, reaction: st.ReactionEntry):
        """Update an existing reaction"""

        if not self.dd.store.has_reaction(reaction.reaction_id):
            return
        self.dd.store.async_update_reaction(reaction)
        async_dispatcher_send(self.hass, co.EVENT_ITEM_UPDATED, reaction.reaction_id)

    async def async_delete_reaction(self, reaction: st.ReactionEntry):
        """Delete an existing reaction"""

        if not self.dd.store.has_reaction(reaction.reaction_id):
            return
        self.dd.store.async_delete_reaction(reaction.reaction_id)
        async_dispatcher_send(self.hass, co.EVENT_ITEM_REMOVED, reaction.reaction_id)

    async def async_delete_config(self):
        """Delete all stored configuration"""

        await self.dd.store.async_delete()


