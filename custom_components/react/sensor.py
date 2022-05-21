from datetime import datetime
from typing import Union
from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as get_entity_registry

from .base import ReactBase
from .reactions.base import ReactReaction
from .utils.logger import get_react_logger

from .const import (
    ATTR_ACTION,
    ATTR_ENTITY,
    ATTR_TYPE,
    ATTR_WORKFLOW_ID,
    DOMAIN,
    SIGNAL_ITEM_CREATED,
    SIGNAL_ITEM_REMOVED,
    SIGNAL_ITEM_UPDATED,
)

_LOGGER = get_react_logger()


async def async_setup_platform(hass: HomeAssistant, config, async_add_entities: AddEntitiesCallback, discovery_info=None):
    react: ReactBase = hass.data[DOMAIN]
    reaction_entities: Union[dict[str, ReactionEntity], None] = {}

    @callback
    def async_add_entity(reaction: ReactReaction):
        if not reaction.needs_sensor(): return

        if reaction.data.id in reaction_entities:
            _LOGGER.warn(f"Registry: '{reaction.data.workflow_id}' found existing reaction in registry while adding, overwriting: '{entity.entity_id}'")
            reaction_entities.pop(reaction.data.id)

        entity = ReactionEntity(reaction)
        reaction_entities[reaction.data.id] = entity
        async_add_entities([entity])

        _LOGGER.debug(f"Registry: '{reaction.data.workflow_id}' added reaction to registry: '{entity.entity_id}'")

    @callback
    def async_update_entity(reaction: ReactReaction):
        if not reaction.needs_sensor(): return
        if not reaction.data.id in reaction_entities:
            _LOGGER.warn(f"Registry: reaction not found while updating, ignoring: '{reaction.data.id}'", )
            return

        entity = reaction_entities.get(reaction.data.id)
        entity.entity_state = entity.reaction.data.datetime
        hass.loop.create_task(entity.async_update_ha_state())
        _LOGGER.debug(f"Registry: '{entity.reaction.data.workflow_id}' updated reaction in registry: '{entity.entity_id}'")
   
    @callback
    def async_delete_entity(reaction: ReactReaction):
        if not reaction.needs_sensor(): return
        if not reaction.data.id in reaction_entities:
            _LOGGER.warn(f"Registry: reaction not found while deleting, ignoring: '{reaction.data.id}'")
            return
        
        entity = reaction_entities.pop(reaction.data.id)
        entity_registry = get_entity_registry(hass)
        if entity_registry.async_is_registered(entity.entity_id):
            _LOGGER.debug(f"Registry: '{entity.reaction.data.workflow_id}' removing reaction from registry: '{entity.entity_id}'")
            entity_registry.async_remove(entity.entity_id)
        else:
            _LOGGER.warn(f"Registry: '{entity.reaction.data.workflow_id}' couldn't find reaction in registry while deleting: '{entity.entity_id}'")


    async_dispatcher_connect(hass, SIGNAL_ITEM_CREATED, async_add_entity)
    async_dispatcher_connect(hass, SIGNAL_ITEM_REMOVED, async_delete_entity)
    async_dispatcher_connect(hass, SIGNAL_ITEM_UPDATED, async_update_entity)

    return True


def reaction_to_entity_id(entity: str, type: str, action: str, id: str) -> str:
    return f"{PLATFORM}.reaction_{entity}_{type}_{action}_{id}"


class ReactionEntity(Entity):

    def __init__(self, reaction: ReactReaction) -> None:
        self.reaction = reaction

        if self._attr_available:
            self.entity_id = reaction_to_entity_id(reaction.data.reactor_entity, reaction.data.reactor_type, reaction.data.reactor_action, reaction.data.id)
            self.entity_state = reaction.data.datetime


    @property
    def name(self) -> str:
        if not self.available:
            return "unavailable"
        return f"Reaction - {self.reaction.data.reactor_type} {self.reaction.data.reactor_action} {self.reaction.data.reactor_entity}"


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
            ATTR_ENTITY: self.reaction.data.reactor_entity,
            ATTR_TYPE: self.reaction.data.reactor_type,
            ATTR_ACTION: self.reaction.data.reactor_action,
            ATTR_WORKFLOW_ID: self.reaction.data.workflow_id
        }

        return output


    @property
    def unique_id(self):
        return f"{self.reaction.data.id}"