"""Allows the creation of generic react entities."""

from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ON,
)
from homeassistant.core import (
    HomeAssistant, 
    asyncio,
)
from homeassistant.helpers import device_registry
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import bind_hass

from . import const as co
from .lib import domain_data as dom

CONFIG_SCHEMA = vol.Schema({
    vol.Optional(co.DOMAIN, default={}): vol.Schema({
        vol.Optional(co.CONF_WORKFLOWS): co.WORKFLOW_SCHEMA,
        vol.Optional(co.CONF_TEMPLATES): co.TEMPLATE_SCHEMA,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    co.LOGGER.info("Setting up react domain")

    dd = dom.DomainData(hass)
    hass.data[co.DOMAIN] = dd
    dd.init_config(config)
    
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up react from config."""
    co.LOGGER.info("Setting up react entry")
    
    # Initialize all domain data
    dd = hass.data[co.DOMAIN]
    await dd.init_data(config_entry)
    
    # Create device
    dr = await device_registry.async_get_registry(hass)
    dr.async_get_or_create(
        config_entry_id = config_entry.entry_id,
        identifiers = {(co.DOMAIN, dd.device_id)},
        name = co.DEVICE_REACT_NAME,
        model = co.DEVICE_REACT_MODEL,
        sw_version = co.VERSION,
        manufacturer = co.DEVICE_REACT_MANUFACTURER,
    )
    if config_entry.unique_id is not None:
        hass.config_entries.async_update_entry(config_entry, unique_id=config_entry.unique_id)
    
    # Load entities
    await dd.workflow_entity_manager.load()
    
    # Setup sensor platform for reactions
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM)
    )
    
    # Start the reactor
    await dd.reactor.start()

    return True

async def async_unload_entry(hass, entry):
    """Unload React config entry."""
    co.LOGGER.info("Unloading react")

    dd = hass.data[co.DOMAIN]

    # Stop the reactor
    dd.reactor.stop()
    
    # Unload sensor platform, which will unload ll reaction entities
    unload_ok = all(
        await asyncio.gather(*[hass.config_entries.async_forward_entry_unload(entry, PLATFORM)])
    )
    
    # Unload all workflow entities
    await dd.workflow_entity_manager.unload()
    
    return unload_ok

async def async_remove_entry(hass, entry):
    """Remove React data."""
    co.LOGGER.info("Removing react")
    
    dd = hass.data[co.DOMAIN]
    
    # Delete internal store data (react.storage)
    await dd.coordinator.async_delete_config()

    # Reset all domain data
    dd.reset()
    
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    co.LOGGER.debug("Migrating from version %s", config_entry.version)
    return True

@bind_hass
def is_on(hass: HomeAssistant, entity_id: str) -> bool:
    """Return if the workflow is on based on the statemachine."""
    return hass.states.is_state(entity_id, STATE_ON)
