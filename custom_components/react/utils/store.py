from homeassistant.helpers.json import JSONEncoder
from homeassistant.helpers.storage import Store
from homeassistant.util import json as json_util

from ..const import VERSION_STORAGE
from ..exceptions import ReactException
from .logger import get_react_logger

_LOGGER = get_react_logger()

class ReactStore(Store):
    def load(self):
        try:
            data = json_util.load_json(self.path)
        except BaseException as exception: 
            _LOGGER.critical(
                "Could not load '%s', restore it from a backup or delete the file: %s",
                self.path,
                exception,
            )
            raise ReactException(exception) from exception
        if data == {} or data["version"] != self.version:
            return None
        return data["data"]


def get_store_key(key):
    return key if "/" in key else f"react.{key}"


def _get_store_for_key(hass, key, encoder):
    return ReactStore(hass, VERSION_STORAGE, get_store_key(key), encoder=encoder)


def get_store_for_key(hass, key):
    return _get_store_for_key(hass, key, JSONEncoder)


async def async_load_from_store(hass, key):
    return await get_store_for_key(hass, key).async_load() or {}


async def async_save_to_store_default_encoder(hass, key, data):
    """Generate store json safe data to the filesystem.

    The data is expected to be encodable with the default
    python json encoder. It should have already been passed through
    JSONEncoder if needed.
    """
    await _get_store_for_key(hass, key, None).async_save(data)


async def async_save_to_store(hass, key, data):
    """Generate dynamic data to store and save it to the filesystem.

    The data is only written if the content on the disk has changed
    by reading the existing content and comparing it.

    If the data has changed this will generate two executor jobs

    If the data has not changed this will generate one executor job
    """
    current = await async_load_from_store(hass, key)
    if current is None or current != data:
        await get_store_for_key(hass, key).async_save(data)
        return
    _LOGGER.debug(
        "<ReactStore async_save_to_store> Did not store data for '%s'. Content did not change",
        get_store_key(key),
    )
