from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity, EntityCategory
from homeassistant.helpers.entity_registry import async_get as get_entity_registry

from homeassistant.components.sensor import DOMAIN as PLATFORM

from . import store as st
from .. import const as co
from . import domain_data as dom


def reaction_to_entity_id(reactor: str, type: str, action: str, id: str) -> str:
    return "{}.reaction_{}_{}_{}_{}".format(PLATFORM, reactor, type, action, id)


class ReactionEntity(Entity):

    def __init__(self, hass: HomeAssistant, device_id: str, reaction: st.ReactionEntry) -> None:
        self.device_id = device_id
        self.hass = hass
        self.reaction = reaction
        self.dd = dom.get_domain_data(hass)

        self.workflow,self.actor,self.reactor = self.dd.get_workflow_metadata(reaction)
        self._attr_available = self.workflow and self.actor and self.reactor

        if self._attr_available:
            self.entity_id = reaction_to_entity_id(self.reactor.entity, self.reactor.type, self.reaction.action, reaction.id)
            self.entity_state = reaction.datetime
            self.listeners = [
                async_dispatcher_connect(self.hass, co.EVENT_ITEM_UPDATED, self.async_item_updated),
        ]


    async def async_added_to_hass(self) -> None:
        co.LOGGER.info("Workflow '{}' added reaction entity '{}' to hass".format(self.reaction.workflow_id, self.entity_id))


    @callback
    async def async_item_updated(self, reaction_id: str):
        co.LOGGER.info("Workflow '{}' updated reaction entity '{}'".format(self.reaction.workflow_id, self.entity_id))
        if reaction_id != self.reaction.id:
            return

        store = await st.async_get_store(self.hass)
        self.reaction = store.async_get_reaction_by_id(reaction_id)
        self.entity_state = self.reaction.datetime

        await self.async_update_ha_state()
    

    async def async_will_remove_from_hass(self):
        co.LOGGER.info("Workflow '{}' removing reaction entity '{}' from hass".format(self.reaction.workflow_id, self.entity_id))
        await super().async_will_remove_from_hass()

        if self.listeners:
            while len(self.listeners):
                self.listeners.pop()()


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
        self.entities = {}


    def create_reaction_entity(self, device_id: str, reaction: st.ReactionEntry, async_add_entities):
        entity = ReactionEntity(self.hass, device_id, reaction)
        if reaction.id in self.entities:
            co.LOGGER.warn("Entity '{}' already found in entity registry while adding, will overwrite".format(entity.entity_id))
            self.entities.pop(reaction.id)
        self.entities[reaction.id] = entity
        async_add_entities([entity])


    def delete_reaction_entity(self, reaction_id):
        if not reaction_id in self.entities:
            co.LOGGER.warn("Entity for reaction '{}' not found".format(reaction_id))
            return
        
        entity = self.entities[reaction_id]
        entity_registry = get_entity_registry(self.hass)
        if entity_registry.async_is_registered(entity.entity_id):
            entity_registry.async_remove(entity.entity_id)
        else:
            co.LOGGER.warn("Entity '{}' not found in entity registry while deleting".format(entity.entity_id))
