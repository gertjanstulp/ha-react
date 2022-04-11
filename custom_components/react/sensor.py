from homeassistant.core import HomeAssistant

from . import const as co
from .lib.reaction_entities import get as ReactionEntityManager


def entity_exists_in_hass(hass, entity_id):
    return hass.states.get(entity_id) is not None


async def async_setup(hass, config):
    return True


async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    rm = ReactionEntityManager(hass)
    rm.setup(async_add_entities)
    rm.load()