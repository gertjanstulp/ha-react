from atexit import register
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity, EntityCategory
from homeassistant.helpers.entity_registry import async_get as get_entity_registry

from homeassistant.components.sensor import DOMAIN as PLATFORM

from . import store as st
from .. import const as co

def reaction_to_entity_id(reactor: str, reactor_type: str, reactor_action: str, reaction_id: str) -> str:
    return "{}.reaction_{}_{}_{}_{}".format(PLATFORM, reactor, reactor_type, reactor_action, reaction_id)

class ReactionEntity(Entity):
    """Defines a base reaction entity."""

    def __init__(self, device_id: str, hass: HomeAssistant, reaction: st.ReactionEntry) -> None:
        """Initialize the reaction entity."""
        self._device_id = device_id
        self._hass = hass
        self._reaction = reaction
        self.entity_id = reaction_to_entity_id(reaction.reactor, reaction.reactor_type, reaction.reactor_action, reaction.reaction_id)

        self._state = reaction.reaction_datetime

        self._listeners = [
            async_dispatcher_connect(self._hass, co.EVENT_ITEM_UPDATED, self.async_item_updated),
        ]

    async def async_added_to_hass(self) -> None:
        co.LOGGER.info("Workflow '{}' added reaction entity '{}' to hass".format(self._reaction.workflow_id, self.entity_id))


    @callback
    async def async_item_updated(self, reaction_id: str):
        co.LOGGER.info("Workflow '{}' updated reaction entity '{}'".format(self._reaction.workflow_id, self.entity_id))
        if reaction_id != self._reaction.reaction_id:
            return

        store = await st.async_get_store(self.hass)
        self._reaction = store.async_get_reaction_by_id(reaction_id)
        self._state = self._reaction.reaction_datetime

        await self.async_update_ha_state()
    
    async def async_will_remove_from_hass(self):
        co.LOGGER.info("Workflow '{}' removing reaction entity '{}' from hass".format(self._reaction.workflow_id, self.entity_id))
        await super().async_will_remove_from_hass()

        while len(self._listeners):
            self._listeners.pop()()

    @property
    def device_info(self) -> dict:
        """Return info for device registry."""
        device = self._device_id
        return {
            "identifiers": {(co.DOMAIN, device)},
            "name": co.DEVICE_REACT_NAME,
            "model": co.DEVICE_REACT_MODEL,
            "sw_version": co.VERSION,
            "manufacturer": co.DEVICE_REACT_MANUFACTURER,
        }

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "Reaction - {} {} {}".format(self._reaction.reactor_type, self._reaction.reactor_action, self._reaction.reactor)

    @property
    def should_poll(self) -> bool:
        """Return the polling requirement of the entity."""
        return False

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def icon(self):
        """Return icon."""
        return "mdi:calendar-clock"

    @property
    def entity_category(self):
        """Return entity_category."""
        return EntityCategory.CONFIG

    @property
    def state_attributes(self):
        """Return the data of the entity."""
        output = {
            co.ATTR_REACTION_ID: self._reaction.reaction_id,
            co.ATTR_REACTOR: self._reaction.reactor,
            co.ATTR_REACTOR_TYPE: self._reaction.reactor_type,
            co.ATTR_REACTOR_ACTION: self._reaction.reactor_action,
            co.ATTR_WORKFLOW_ID: self._reaction.workflow_id
        }

        return output

    @property
    def available(self):
        """Return True if entity is available."""
        return True

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self._reaction.reaction_id}"

class ReactionEntityManager:
    def __init__(self, hass: HomeAssistant):
        self._hass = hass
        self._entities = {}

    def create_reaction_entity(self, device_id: str, reaction: st.ReactionEntry, async_add_entities):
        entity = ReactionEntity(device_id, self._hass, reaction)
        if reaction.reaction_id in self._entities:
            co.LOGGER.warn("Entity '{}' already found in entity registry while adding, will overwrite".format(entity.entity_id))
            self._entities.pop(reaction.reaction_id)
        self._entities[reaction.reaction_id] = entity
        async_add_entities([entity])

    def delete_reaction_entity(self, reaction_id):
        if not reaction_id in self._entities:
            co.LOGGER.warn("Entity for reaction '{}' not found".format(reaction_id))
            return
        
        entity = self._entities[reaction_id]
        entity_registry = get_entity_registry(self._hass)
        if entity_registry.async_is_registered(entity.entity_id):
            entity_registry.async_remove(entity.entity_id)
        else:
            co.LOGGER.warn("Entity '{}' not found in entity registry while deleting".format(entity.entity_id))
