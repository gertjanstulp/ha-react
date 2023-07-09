from __future__ import annotations

from typing import Any, Coroutine, Mapping
from homeassistant.core import Context, HomeAssistant, State
from custom_components.react.const import ATTR_WAIT

from custom_components.react.plugin.hass_api import HassApi
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


class HassApiMockExtend():
    @property
    def hass_api_mock(self) -> HassApiMock:
        return self.plugin.hass_api


class HassApiMock(HassApi):
    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)
        self.available_services: dict[str, list[str]] = {}
        self.states: dict[str, State] = {}


    async def async_hass_call_service(
        self, 
        domain: str, 
        service: str, 
        service_data: dict[str, Any] | None = None, 
        blocking: bool = False, 
        context: Context | None = None, 
    ) -> Coroutine[Any, Any, bool | None]:
        test_context: TstContext = self.hass_get_data(TEST_CONTEXT)
        test_context.register_service_call(domain, service, service_data)
        return None
    

    async def async_hass_wait(self, seconds: int):
        context: TstContext = self.hass_get_data(TEST_CONTEXT)
        context.register_plugin_data({
            ATTR_WAIT: seconds
        })


    def hass_service_available(self, domain: str, entity_id: str) -> bool:
        return domain in self.available_services and entity_id in self.available_services[domain]
    

    def hass_get_state(self, entity_id: str) -> State | None:
        if state := self.states.get(entity_id, None):
            return state
        return super().hass_get_state(entity_id)
    

    def hass_register_service(self, domain: str, entity_id: str):
        if not domain in self.available_services:
            self.available_services[domain] = []
        return self.available_services[domain].append(entity_id)


    def hass_register_state(self, entity_id: str, state: str, attributes: Mapping[str, Any] | None = None):
        self.states[entity_id] = State(entity_id, state, attributes)


    def hass_get_uid_str(self) -> str:
        return "0123456789"
    

    def hass_generate_media_source_id(self, 
        message: str, 
        engine: str | None = None, 
        language: str | None = None, 
        options: dict | None = None, 
        cache: bool | None = None
    ) -> str:
        result = f"{message}|{engine}|{language}"
        if options:
            result = f"{result}|{str(options)}"
        return result

