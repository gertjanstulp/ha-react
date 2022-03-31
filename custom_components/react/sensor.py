from homeassistant.core import HomeAssistant, callback

from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
)
from . import const as co
from .lib import store as st
from .lib import domain_data as dom


def entity_exists_in_hass(hass, entity_id):
    return hass.states.get(entity_id) is not None


async def async_setup(hass, config):
    return True


async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    dd = dom.get_domain_data(hass)

    @callback
    def async_add_entity(reaction: st.ReactionEntry):
        """Add reaction for React."""
        dd.reaction_entity_manager.create_reaction_entity(dd.device_id, reaction, async_add_entities)

    @callback
    def async_delete_entity(reaction_id):
        dd.reaction_entity_manager.delete_reaction_entity(reaction_id)
        

    for entry in dd.store.reactions.values():
        async_add_entity(entry)

    async_dispatcher_connect(hass, co.EVENT_ITEM_CREATED, async_add_entity)
    async_dispatcher_connect(hass, co.EVENT_ITEM_REMOVED, async_delete_entity)

async def async_unload_entry(hass, entry):
    co.LOGGER("Unload react sensor platform")

async def async_remove_entry(hass, entry):
    co.LOGGER("Remove react sensor platform")