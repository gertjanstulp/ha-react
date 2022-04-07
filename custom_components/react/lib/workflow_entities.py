from typing import Any

from homeassistant.components.template.template_entity import TemplateEntity
from homeassistant.const import  SERVICE_TOGGLE, SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_ON
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.restore_state import RestoreEntity

from .. import const as co
from .config import get as ConfigManager, Workflow
from .listener import Listener
from .domain_data import get as DomainData


class WorkflowEntityManager:
    def __init__(self, hass: HomeAssistant, component: EntityComponent):
        self.hass = hass
        self.component = component
        self.config_manager = ConfigManager(hass)
        
        # workflow toggle handling
        self.component.async_register_entity_service(SERVICE_TOGGLE, {}, "async_toggle")
        self.component.async_register_entity_service(SERVICE_TURN_ON, {}, "async_turn_on")
        self.component.async_register_entity_service(SERVICE_TURN_OFF, {}, "async_turn_off")


    async def load(self):
        entities = []
        
        for workflow in self.config_manager.workflows.values():
            entities.append(WorkflowEntity(self.hass, DomainData(self.hass).device_id, workflow))
        
        if entities:
            await self.component.async_add_entities(entities)


    async def unload(self):
        for workflow in self.config_manager.workflows.values():
            await self.component.async_remove_entity(workflow.entity_id)


class WorkflowEntity(TemplateEntity, ToggleEntity, RestoreEntity):
    """Representation of a workflow."""

    def __init__(self, hass:HomeAssistant, device_id: str, workflow: Workflow):
        super().__init__(hass)

        """Initialize a workflow."""
        self.hass = hass
        self.entity_id = workflow.entity_id
        self.device_id = device_id
        self.workflow_config = workflow
        self.is_enabled = False

        self.listeners: list[Listener] = []
        for actor in self.workflow_config.actors.values():
            self.listeners.append(Listener(self.hass, self.workflow_config, actor))


    async def async_added_to_hass(self) -> None:
        """Startup with initial state or previous state."""
        co.LOGGER.info("Workflow entity '{}' added to hass".format(self.entity_id))

        await super().async_added_to_hass()

        if state := await self.async_get_last_state():
            enable_workflow = state.state == STATE_ON
            co.LOGGER.info("Loaded workflow '%s' with state '%s' from state, storage last state '%s'", self.entity_id, enable_workflow, state)
        else:
            enable_workflow = co.DEFAULT_INITIAL_STATE
            co.LOGGER.info("Workflow '%s' not in state storage, state '%s' from default is used", self.entity_id, enable_workflow)

        if enable_workflow:
            await self.async_enable()

        self.workflow_config.on_update(self.async_write_ha_state)
        self.async_on_remove(self.workflow_config.async_unload)


    # @callback
    # def _update_state(self, result):
    #     super()._update_state(result)


    async def async_will_remove_from_hass(self):
        co.LOGGER.info("Workflow entity '{}' being removed from hass".format(self.entity_id))
        await self.async_disable()


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
    def should_poll(self):
        """If entity should be polled."""
        return False


    @property
    def name(self):
        """Return the name of the variable."""
        return self.workflow_config.friendly_name
    

    @property
    def icon(self):
        """Return the icon to be used for this entity."""
        return self.workflow_config.icon


    @property
    def workflow(self):
        return self.workflow_config


    @property
    def extra_state_attributes(self):
        return self.workflow_config.as_dict()

    @property
    def is_on(self) -> bool:
        return self.is_enabled


    @callback
    def async_turn_on(self, **kwargs: Any) -> None:
        self.hass.loop.create_task(self.async_enable())


    @callback
    def async_turn_off(self, **kwargs: Any) -> None:
        self.hass.loop.create_task(self.async_disable())

    
    async def async_enable(self):
        if self.is_enabled:
            return

        self.is_enabled = True
        for listener in self.listeners:
            listener.enable()

        await self.async_update_ha_state()
    
    
    async def async_disable(self):
        if not self.is_enabled:
            return

        self.is_enabled = False
        for listener in self.listeners:
            listener.disable()

        await self.async_update_ha_state()

    
def get(hass: HomeAssistant) -> WorkflowEntityManager:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER].workflow_entity_manager
    return None
