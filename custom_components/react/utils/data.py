
from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_DATA,
    ATTR_REACTOR_ACTION,
    ATTR_REACTOR_ENTITY, 
    ATTR_REACTOR_ID, 
    ATTR_REACTOR_TYPE, 
)
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.store import async_load_from_store, async_save_to_store

DEFAULT_REACTION_DATA = (
    (ATTR_REACTOR_ID, None),
    (ATTR_REACTOR_ENTITY, None),
    (ATTR_REACTOR_TYPE, None),
    (ATTR_REACTOR_ACTION, None),
    (ATTR_DATA, None),
)

_LOGGER = get_react_logger()


class ReactData:
    def __init__(self, react: ReactBase):
        self.react = react
        self.content = {}


    async def async_write(self, force: bool = False) -> None:
        if not force and self.react.system.disabled:
            return

        _LOGGER.debug("<ReactData async_write> Saving data")
        await async_save_to_store(
            self.react.hass,
            "react",
            {
                "view": self.react.configuration.frontend_mode,
                "compact": self.react.configuration.frontend_compact,
            },
        )
        await self._async_store_reaction_data()

    
    async def _async_store_reaction_data(self):
        self.content = {}
        await async_save_to_store(self.react.hass, "reactions", self.content)


    async def async_restore(self):
        self.react.status.new = False
        react = await async_load_from_store(self.react.hass, "react") or {}
        reactions = await async_load_from_store(self.react.hass, "reactions") or {}

        if not react and not reactions:
            # Assume new install
            self.react.status.new = True
            _LOGGER.debug("<ReactData restore> Loading base reaction information")
            reactions = {}

        _LOGGER.debug("<ReactData restore> Restore started")

        # React
        self.react.configuration.frontend_mode = react.get("view", "Grid")
        self.react.configuration.frontend_compact = react.get("compact", False)

        try:
            for entry, reaction_data in reactions.items():
                if entry == "0":
                    # Ignore repositories with ID 0
                    _LOGGER.debug("<ReactData restore> Found reaction with ID %s - %s", entry, reaction_data)
                    continue
            _LOGGER.debug("<ReactData restore> Restore done")
        except BaseException as exception:
            _LOGGER.critical("<ReactData restore> [%s] Restore Failed!", exception, exc_info=exception)
            return False

        return True
