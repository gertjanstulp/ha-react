from typing import Any

from homeassistant.components.template.template_entity import TemplateEntity
from homeassistant.const import SERVICE_RELOAD, SERVICE_TOGGLE, SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_ON
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.service import async_register_admin_service

from .. import const as co
from . import config as cf
from . import listener as li
from . import domain_data as dom


class WorkflowEntityManager:
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.component = EntityComponent(co.LOGGER, co.DOMAIN, hass)
        self.dd = dom.get_domain_data(hass)
        
        # reload handling
        async def reload_service_handler(service_call: ServiceCall) -> None:
            await self.reset()

        async_register_admin_service(
            hass,
            co.DOMAIN,
            SERVICE_RELOAD,
            reload_service_handler
        )

        # workflow toggle handling
        self.component.async_register_entity_service(SERVICE_TOGGLE, {}, "async_toggle")
        self.component.async_register_entity_service(SERVICE_TURN_ON, {}, "async_turn_on")
        self.component.async_register_entity_service(SERVICE_TURN_OFF, {}, "async_turn_off")


    async def load(self):
        workflows = await cf.load_from_config(self.hass, self.dd.domain_config)
        self.dd.init_workflows(workflows)

        entities = []
        
        for workflow in self.dd.workflows.values():
            entities.append(WorkflowEntity(self.hass, self.dd.device_id, workflow))
        
        if entities:
            await self.component.async_add_entities(entities)


    async def reset(self): 
        """Reload yaml entities."""
        conf = await self.component.async_prepare_reload()
        if conf is None:
            conf = {co.DOMAIN: {}}

        self.dd.init_config(conf)

        await self.load()


    async def unload(self):
        for workflow in self.dd.workflows.values():
            await self.component.async_remove_entity(workflow.entity_id)


class WorkflowEntity(TemplateEntity, ToggleEntity, RestoreEntity):
    """Representation of a workflow."""

    def __init__(self, hass:HomeAssistant, device_id: str, workflow: cf.Workflow):
        super().__init__(hass)

        """Initialize a workflow."""
        self.hass = hass
        self.entity_id = workflow.entity_id
        self.device_id = device_id
        self._workflow = workflow
        self.is_enabled = False

        self.listeners = []
        for actor in self._workflow.actors.values():
            self.listeners.append(li.Listener(self.hass, self._workflow, actor))


    async def async_added_to_hass(self) -> None:
        """Startup with initial state or previous state."""
        co.LOGGER.info("Workflow entity '{}' added to hass".format(self.entity_id))

        await super().async_added_to_hass()

        if state := await self.async_get_last_state():
            enable_workflow = state.state == STATE_ON
            co.LOGGER.debug("Loaded workflow '%s' with state '%s' from state, storage last state '%s'", self.entity_id, enable_workflow, state)
        else:
            enable_workflow = co.DEFAULT_INITIAL_STATE
            co.LOGGER.debug("Automation '%s' not in state storage, state '%s' from default is used", self.entity_id, enable_workflow)

        if enable_workflow:
            await self.async_enable()

        for actor in self._workflow.actors.values():
            actor.register_entity(self)
        for reactor in self._workflow.reactors.values():
            reactor.register_entity(self)


    @callback
    def _update_state(self, result):
        super()._update_state(result)


    async def async_will_remove_from_hass(self):
        co.LOGGER.info("Workflow entity '{}' being removed from hass".format(self.entity_id))

        await super().async_will_remove_from_hass()
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
        return self._workflow.friendly_name
    

    @property
    def icon(self):
        """Return the icon to be used for this entity."""
        return self._workflow.icon


    @property
    def workflow(self):
        return self._workflow


    @property
    def extra_state_attributes(self):
        return self._workflow.as_dict()

    @property
    def is_on(self) -> bool:
        return self.is_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_enable()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_disable()

    async def async_enable(self):
        if self.is_enabled:
            return

        self.is_enabled = True
        for listener in self.listeners:
            listener.start()

        self.async_write_ha_state()
       
    async def async_disable(self):
        if not self.is_enabled:
            return

        self.is_enabled = False
        for listener in self.listeners:
            listener.stop()

        self.async_write_ha_state()

    
    async def async_update(self) -> None:
        """Call for forced update."""
        if self._async_update:
            self._async_update()
