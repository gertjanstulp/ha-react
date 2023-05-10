from asyncio import sleep
from typing import Any
from uuid import uuid4

from homeassistant.components.tts.media_source import generate_media_source_id
from homeassistant.core import Context, HomeAssistant, SERVICE_CALL_LIMIT, State
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import RegistryEntry



class HassApi:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.entity_registry = er.async_get(self.hass)


    async def async_hass_call_service(
        self,
        domain: str,
        service: str,
        service_data: dict[str, Any] | None = None,
        blocking: bool = False,
        context: Context | None = None,
        limit: float | None = SERVICE_CALL_LIMIT,
        target: dict[str, Any] | None = None,
    ) -> bool | None:
        return await self.hass.services.async_call(
            domain,
            service,
            service_data,
            blocking,
            context,
            limit,
            target,
        )
    

    def hass_get_state(self, entity_id: str) -> State | None:
        return self.hass.states.get(entity_id)
    

    def hass_get_data(self, key: str, default: Any = None) -> Any:
        return self.hass.data.get(key, default)
    

    def hass_set_data(self, key: str, data: Any) -> Any:
        self.hass.data[key] = data
        return data
    
    
    def hass_get_entity(self, entity_id: str) -> RegistryEntry | None:
        return self.entity_registry.async_get(entity_id) 
    

    def hass_service_available(self, domain: str, entity_id: str) -> bool:
        return self.hass.services.has_service(domain, entity_id)
    

    async def async_hass_wait(self, seconds: int):
        await sleep(seconds)


    def hass_get_uid_str(self) -> str:
        return uuid4().hex
    
    
    def hass_generate_media_source_id(self, message: str, engine: str | None = None, language: str | None = None, options: dict | None = None, cache: bool | None = None) -> str:
        return generate_media_source_id(self.hass, message, engine, language, options, cache)