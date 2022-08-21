from typing import Union
from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback, async_get_current_platform
from homeassistant.helpers.entity_registry import async_get as get_entity_registry

from .base import ReactBase
from .reactions.base import ReactReaction
from .utils.logger import get_react_logger

from .const import (
    ATTR_ACTION,
    ATTR_ENTITY,
    ATTR_FORWARD_ACTION,
    ATTR_ID,
    ATTR_OVERWRITE,
    ATTR_RESET_WORKFLOW,
    ATTR_TYPE,
    ATTR_WORKFLOW_ID,
    DOMAIN,
    SERVICE_DELETE_REACTION,
    SERVICE_REACT_NOW,
    SERVICE_TRIGGER_REACTION,
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

        entity = ReactionEntity(react, reaction)
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

    @callback
    async def trigger_reaction_service_handler(entity: ReactionEntity, service_call: ServiceCall):
        entity.trigger(False)

    @callback
    async def delete_reaction_service_handler(entity: ReactionEntity, service_call: ServiceCall):
        react.reactions.delete(entity.reaction)

    @callback
    async def react_now_service_handler(entity: ReactionEntity, service_call: ServiceCall):
        entity.trigger(True)

    
    platform = async_get_current_platform()
    platform.async_register_entity_service(SERVICE_TRIGGER_REACTION, {}, trigger_reaction_service_handler)
    platform.async_register_entity_service(SERVICE_DELETE_REACTION, {}, delete_reaction_service_handler)
    platform.async_register_entity_service(SERVICE_REACT_NOW, {}, react_now_service_handler)

    return True


class ReactionEntity(Entity):

    def __init__(self, react: ReactBase, reaction: ReactReaction) -> None:
        self.react = react
        self.reaction = reaction

        if self._attr_available:
            self.entity_id = f"{PLATFORM}.reaction_{reaction.data.workflow_id}_{reaction.data.reactor_id}_{reaction.data.id}"
            self.entity_state = reaction.data.datetime


    @property
    def name(self) -> str:
        if not self.available:
            return "unavailable"
        return f"Reaction - {self.reaction.data.workflow_id} {self.reaction.data.reactor_id}"


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
            ATTR_ID: self.reaction.data.id,
            ATTR_WORKFLOW_ID: self.reaction.data.workflow_id,
            ATTR_ENTITY: self.reaction.data.reactor_entity,
            ATTR_TYPE: self.reaction.data.reactor_type,
            ATTR_ACTION: self.reaction.data.reactor_action,
            ATTR_RESET_WORKFLOW: self.reaction.data.reset_workflow,
            ATTR_OVERWRITE: self.reaction.data.overwrite,
            ATTR_FORWARD_ACTION: self.reaction.data.forward_action,
        }

        return output


    @property
    def unique_id(self):
        return f"{self.reaction.data.id}"


    def trigger(self, delete_reaction: bool) -> None:
        self.react.dispatcher.force_dispatch(self.reaction.data.id, delete_reaction)