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

from custom_components.react.plugin.alarm_control_panel.config import AlarmConfig
from custom_components.react.plugin.alarm_control_panel.const import ArmMode
from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session


class AlarmProvider(PluginProviderBase[AlarmConfig]):

    async def async_arm(self, session: Session, context: Context, entity_id: str, code: str, arm_mode: ArmMode):
        await self.plugin.hass_api.async_hass_call_service(
            ALARM_DOMAIN,
            SERVICE_ALARM_ARM_HOME if arm_mode == ArmMode.HOME else 
            SERVICE_ALARM_ARM_AWAY if arm_mode == ArmMode.AWAY else 
            SERVICE_ALARM_ARM_NIGHT if arm_mode == ArmMode.NIGHT else 
            SERVICE_ALARM_ARM_VACATION if arm_mode == ArmMode.VACATION else
            None,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_CODE: code,
            },
            context=context,
        )

    async def async_disarm(self, session: Session, context: Context, entity_id: str, code: str):
        await self.plugin.hass_api.async_hass_call_service(
            ALARM_DOMAIN,
            SERVICE_ALARM_DISARM,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_CODE: code,
            },
            context=context,
        )

    
    async def async_trigger(self, session: Session, context: Context, entity_id: str):
        await self.plugin.hass_api.async_hass_call_service(
            ALARM_DOMAIN,
            SERVICE_ALARM_TRIGGER,
            service_data={
                ATTR_ENTITY_ID: entity_id,
            },
            context=context,
        )
