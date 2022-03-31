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
        vol.Optional(co.CONF_WORKFLOW): co.WORKFLOW_SCHEMA,
        vol.Optional(co.CONF_STENCIL): co.STENCIL_SCHEMA,
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    co.LOGGER.info("Setting up react domain")

    dd = dom.set_domain_data(hass)
    dd.init_config(config)
    
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    co.LOGGER.info("Setting up react entry")
    
    # Initialize all domain data
    dd = dom.get_domain_data(hass)
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
    
    # Everything is started (except for the scheduler/transformers), so cleanup abandoned reaction entities which
    # were left behind in the store
    await dd.coordinator.async_cleanup_store()

    # Setup sensor platform for reactions
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM)
    )
    
    # Start the scheduler and transformers
    await dd.scheduler.start()
    dd.transformer_manager.start()

    return True


async def async_unload_entry(hass, entry):
    co.LOGGER.info("Unloading react")

    dd = dom.get_domain_data(hass)

    # Stop the scheduler and transformers
    dd.transformer_manager.stop()
    dd.scheduler.stop()

    # Unload sensor platform, which will unload ll reaction entities
    unload_ok = all(
        await asyncio.gather(*[hass.config_entries.async_forward_entry_unload(entry, PLATFORM)])
    )
    
    # Unload all workflow entities
    await dd.workflow_entity_manager.unload()
    
    return unload_ok


async def async_remove_entry(hass, entry):
    co.LOGGER.info("Removing react")
    
    dd = dom.get_domain_data(hass)
    
    # Delete internal store data (react.storage)
    await dd.coordinator.async_delete_config()

    # Reset all domain data
    dd.reset()


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    co.LOGGER.debug("Migrating from version %s", config_entry.version)
    return True


@bind_hass
def is_on(hass: HomeAssistant, entity_id: str) -> bool:
    return hass.states.is_state(entity_id, STATE_ON)

