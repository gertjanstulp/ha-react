import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.typing import ConfigType

from . import const as co
from .lib.domain_data import get as DomainData
from .lib.bootstrapper import get as Bootstrapper


CONFIG_SCHEMA = vol.Schema({
    vol.Optional(co.DOMAIN, default={}): vol.Schema({
        vol.Optional(co.CONF_WORKFLOW): co.WORKFLOW_SCHEMA,
        vol.Optional(co.CONF_STENCIL): co.STENCIL_SCHEMA,
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    co.LOGGER.info("Setting up react domain")
    
    Bootstrapper(hass).bootstrap(config)
    
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    co.LOGGER.info("Setting up react entry")
    
    # Initialize all domain data
    dd = DomainData(hass)
    await dd.init_config(config_entry)
    
    # Create device
    dr = device_registry.async_get(hass)
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
    
    await Bootstrapper(hass).async_load(config_entry)

    return True


async def async_unload_entry(hass, entry):
    co.LOGGER.info("Unloading react")
    return await Bootstrapper(hass).async_unload(entry)


async def async_remove_entry(hass, entry):
    co.LOGGER.info("Removing react")
    await Bootstrapper(hass).async_teardown()


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    co.LOGGER.debug("Migrating from version %s", config_entry.version)
    return True
