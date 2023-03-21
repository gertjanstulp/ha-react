from homeassistant.const import (
    ATTR_ENTITY_ID, 
)

from homeassistant.components.alarm_control_panel.const import (
    DOMAIN as ALARM_DOMAIN
)
from homeassistant.const import (
    ATTR_CODE,
    SERVICE_ALARM_ARM_AWAY,
    SERVICE_ALARM_DISARM,
    SERVICE_ALARM_TRIGGER,
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class ApiConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.code: str = None
        self.load(source)


class Api():
    def __init__(self, react: ReactBase, config: ApiConfig) -> None:
        self.react = react
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Alarm plugin: Api - {message}")


    def verify_config(self) -> bool:
        if not self.config.code:
            _LOGGER.error("Alarm - No code configured")
            return False
        return True


    async def async_alarm_arm_away(self, context: Context, entity_id: str):
        self._debug(f"Arming away '{entity_id}'")
        try:
            arm_data = {
                ATTR_ENTITY_ID: f"alarm_control_panel.{entity_id}",
                ATTR_CODE: self.config.code,
            }
            await self.react.hass.services.async_call(
                ALARM_DOMAIN,
                SERVICE_ALARM_ARM_AWAY,
                arm_data,
                context,
            )
        except:
            _LOGGER.exception("Arming away failed")


    async def async_alarm_disarm(self, context: Context, entity_id: str):
        self._debug(f"Disarming '{entity_id}'")
        try:
            arm_data = {
                ATTR_ENTITY_ID: f"alarm_control_panel.{entity_id}",
                ATTR_CODE: self.config.code,
            }
            await self.react.hass.services.async_call(
                ALARM_DOMAIN,
                SERVICE_ALARM_DISARM,
                arm_data,
                context,
            )
        except:
            _LOGGER.exception("Disarming failed")


    async def async_alarm_trigger(self, context: Context, entity_id: str):
        self._debug(f"Triggering '{entity_id}'")
        try:
            arm_data = {
                ATTR_ENTITY_ID: f"alarm_control_panel.{entity_id}",
            }
            await self.react.hass.services.async_call(
                ALARM_DOMAIN,
                SERVICE_ALARM_TRIGGER,
                arm_data,
                context,
            )
        except:
            _LOGGER.exception("Triggering failed")