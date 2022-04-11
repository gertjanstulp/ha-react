from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity, EntityCategory
from homeassistant.helpers.entity_registry import async_get as get_entity_registry
from homeassistant.components.sensor import DOMAIN as PLATFORM

from .. import const as co
from .config import get as ConfigManager, Reactor
from .domain_data import get as DomainData
from .store import ReactionEntry
from .coordinator import get as Coordinator
from .dispatcher import get as Dispatcher


def reaction_to_entity_id(reactor: str, type: str, action: str, id: str) -> str:
    return "{}.reaction_{}_{}_{}_{}".format(PLATFORM, reactor, type, action, id)


class ReactionEntity(Entity):

    def __init__(self, hass: HomeAssistant, device_id: str, reaction: ReactionEntry, reactor: Reactor) -> None:
        self.device_id = device_id
        self.hass = hass
        self.reaction = reaction
        self.reactor = reactor
        self._attr_available = reactor is not None

        if self._attr_available:
            self.entity_id = reaction_to_entity_id(self.reactor.entity, self.reactor.type, self.reaction.action, reaction.id)
            self.entity_state = reaction.datetime


    @property
    def device_info(self) -> dict:
        """Return info for device registry."""
        device = self.device_id
        return {
            "identifiers": {(co.DOMAIN, device)},
            "name": co.DEVICE_REACT_NAME,
            "model": co.DEVICE_REACT_MODEL,
            "sw_version": co.VERSION,
            "manufacturer": co.DEVICE_REACT_MANUFACTURER,
        }


    @property
    def name(self) -> str:
        if not self.available:
            return "unavailable"
        return "Reaction - {} {} {}".format(self.reactor.type, self.reaction.action, self.reactor.entity)


    @property
    def should_poll(self) -> bool:
        return False


    @property
    def state(self):
        return self.entity_state


    @property
    def icon(self):
        return "mdi:calendar-clock"


    @property
    def entity_category(self):
        return EntityCategory.CONFIG


    @property
    def state_attributes(self):
        output = {
            co.ATTR_REACTION_ID: self.reaction.id,
            co.ATTR_ENTITY: self.reactor.entity,
            co.ATTR_TYPE: self.reactor.type,
            co.ATTR_ACTION: self.reaction.action if self.reactor.forward_action else self.reactor.action,
            co.ATTR_WORKFLOW_ID: self.reaction.workflow_id
        }

        return output


    @property
    def unique_id(self):
        return f"{self.reaction.id}"


class ReactionEntityManager:
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.config_manager = ConfigManager(hass)
        self.entities: dict[str, ReactionEntity] = {}
        self.coordinator = Coordinator(hass)


    def setup(self, async_add_entities):
        self.async_add_entities = async_add_entities


    def load(self):
        Dispatcher(self.hass).connect_signal(co.SIGNAL_ITEM_CREATED, self.async_add_entity)
        Dispatcher(self.hass).connect_signal(co.SIGNAL_ITEM_REMOVED, self.async_delete_entity)
        Dispatcher(self.hass).connect_signal(co.SIGNAL_ITEM_UPDATED, self.async_update_entity)
        
        for entry in self.coordinator.get_reactions().values():
            co.LOGGER.info("Registry", "'{}' found reaction in store, adding: '{}'", entry.workflow_id, entry.id)
            self.async_add_entity(entry)


    def unload(self):
        for reaction_id in list(self.entities):
            self.async_delete_entity(reaction_id)


    @callback
    def async_add_entity(self, reaction: ReactionEntry):
        _,_,reactor = self.config_manager.get_workflow_metadata(reaction)
        entity = ReactionEntity(self.hass, DomainData(self.hass).device_id, reaction, reactor)
        
        co.LOGGER.info("Registry", "'{}' added reaction to registry: '{}'", reaction.workflow_id, entity.entity_id)
        
        if reaction.id in self.entities:
            co.LOGGER.warn("Registry: '{}' found existing reaction in registry while adding, overwriting: '{}'", reaction.workflow_id, entity.entity_id)
            self.entities.pop(reaction.id)
        self.entities[reaction.id] = entity
        self.async_add_entities([entity])


    @callback
    def async_delete_entity(self, reaction_id):
        if not reaction_id in self.entities:
            co.LOGGER.warn("Registry: reaction not found while deleting, ignoring: '{}'".format(reaction_id))
            return
        
        entity = self.entities.pop(reaction_id)
        entity_registry = get_entity_registry(self.hass)
        if entity_registry.async_is_registered(entity.entity_id):
            co.LOGGER.info("Registry", "'{}' removing reaction from registry: '{}'".format(entity.reaction.workflow_id, entity.entity_id))
            entity_registry.async_remove(entity.entity_id)
        else:
            co.LOGGER.warn("Registry: '{}' couldn't find reaction in registry while deleting: '{}'", entity.reaction.workflow_id, entity.entity_id)


    @callback
    def async_update_entity(self, reaction_id):
        if not reaction_id in self.entities:
            co.LOGGER.warn("Registry: reaction not found while updating, ignoring: '{}'", reaction_id)
            return

        entity = self.entities.get(reaction_id)
        entity.entity_state = entity.reaction.datetime
        self.hass.loop.create_task(entity.async_update_ha_state())
        co.LOGGER.info("Registry", "'{}' updated reaction in registry: '{}'", entity.reaction.workflow_id, entity.entity_id)


def get(hass: HomeAssistant) -> ReactionEntityManager:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER].reaction_entity_manager
    return None
