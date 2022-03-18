from datetime import datetime, timedelta
import logging
from typing import Any
from homeassistant.const import SERVICE_RELOAD, SERVICE_TOGGLE, SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_ON
from homeassistant.core import Event, HomeAssistant, ServiceCall, split_entity_id
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.util.dt import as_timestamp

from .. import const as co
from . import config as cf
from . import store as st
from . import events as ev
from . import listener as li

class WorkflowEntityManager:
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.component = EntityComponent(co.LOGGER, co.DOMAIN, hass)
        self.dd = self.hass.data[co.DOMAIN]
        
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
        
        for workflow in self.dd.workflows:
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
        for workflow in self.dd.workflows:
            await self.component.async_remove_entity(workflow.entity_id)

class WorkflowEntity(ToggleEntity, RestoreEntity):
    """Representation of a workflow."""

    def __init__(self, hass:HomeAssistant, device_id: str, workflow: cf.Workflow):
        """Initialize a workflow."""
        self.hass = hass
        self.dd = hass.data[co.DOMAIN]
        self.entity_id = workflow.entity_id
        self.device_id = device_id
        self._workflow = workflow
        self.is_enabled = False
        self.listener = self.create_listener()

    def create_listener(self) -> li.Listener:
        if self._workflow.actor_type == 'binary_sensor':
            return li.BinarySensorListener(self.hass, self._workflow)
        else:
            return li.ActionEventListener(self.hass, self._workflow)

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
    
    async def async_will_remove_from_hass(self):
        """Remove listeners when removing workflow from Home Assistant."""
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
        """Return the state attributes."""
        return {
            co.ATTR_ACTOR: self._workflow.actor,
            co.ATTR_ACTOR_TYPE: self._workflow.actor_type,
            co.ATTR_ACTOR_ACTION: self._workflow.actor_action,
            co.ATTR_REACTOR: self._workflow.reactor,
            co.ATTR_REACTOR_TYPE: self._workflow.reactor_type,
            co.ATTR_REACTOR_ACTION: self._workflow.reactor_action,
            co.ATTR_REACTOR_TIMING: self._workflow.reactor_timing,
            co.ATTR_REACTOR_DELAY: self._workflow.reactor_delay,
            co.ATTR_REACTOR_OVERWRITE: self._workflow.reactor_overwrite,
            co.ATTR_RESET_WORKFLOW: self._workflow.reset_workflow,
            co.ATTR_ACTION_FORWARD: self._workflow.action_forward,
        }

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self.is_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on and update the state."""
        await self.async_enable()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.async_disable()

    async def async_enable(self):
        """Enable the workflow entity."""
        if self.is_enabled:
            return

        self.is_enabled = True
        self.listener.start()

        self.async_write_ha_state()
       
    async def async_disable(self):
        """Disable the workflow entity."""
        if not self.is_enabled:
            return

        self.is_enabled = False
        self.listener.stop()

        self.async_write_ha_state()

    