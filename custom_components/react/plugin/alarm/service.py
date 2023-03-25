from homeassistant.components.alarm_control_panel.const import (
    DOMAIN as ALARM_DOMAIN
)
from homeassistant.const import (
    ATTR_CODE,
    ATTR_ENTITY_ID, 
    SERVICE_ALARM_ARM_AWAY,
    SERVICE_ALARM_ARM_HOME,
    SERVICE_ALARM_ARM_NIGHT,
    SERVICE_ALARM_ARM_VACATION,
    SERVICE_ALARM_DISARM,
    SERVICE_ALARM_TRIGGER,
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.alarm.const import ArmMode


class AlarmService():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_arm(self, context: Context, entity_id: str, code: str, arm_mode: ArmMode):
        await self.react.hass.services.async_call(
            ALARM_DOMAIN,
            SERVICE_ALARM_ARM_HOME if arm_mode == ArmMode.HOME else 
            SERVICE_ALARM_ARM_AWAY if arm_mode == ArmMode.AWAY else 
            SERVICE_ALARM_ARM_NIGHT if arm_mode == ArmMode.NIGHT else 
            SERVICE_ALARM_ARM_VACATION if arm_mode == ArmMode.VACATION else
            None,
            {
                ATTR_ENTITY_ID: entity_id,
                ATTR_CODE: code,
            },
            context,
        )

    async def async_disarm(self, context: Context, entity_id: str, code: str):
        await self.react.hass.services.async_call(
            ALARM_DOMAIN,
            SERVICE_ALARM_DISARM,
            {
                ATTR_ENTITY_ID: entity_id,
                ATTR_CODE: code,
            },
            context,
        )

    
    async def async_trigger(self, context: Context, entity_id: str):
        await self.react.hass.services.async_call(
            ALARM_DOMAIN,
            SERVICE_ALARM_TRIGGER,
            {
                ATTR_ENTITY_ID: entity_id,
            },
            context,
        )