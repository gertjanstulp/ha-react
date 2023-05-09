from typing import Any
from homeassistant.core import Context, HomeAssistant, SERVICE_CALL_LIMIT, State
from custom_components.react.const import ATTR_WAIT

from custom_components.react.plugin.api import HassApi
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


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
        limit: float | None = SERVICE_CALL_LIMIT,
        target: dict[str, Any] | None = None,
    ) -> bool | None:
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


    def hass_register_state(self, entity_id: str, state: str):
        self.states[entity_id] = State(entity_id, state)


    def hass_get_uid_str(self) -> str:
        return "0123456789"
    

    def hass_generate_media_source_id(self, message: str, engine: str | None = None, language: str | None = None, options: dict | None = None, cache: bool | None = None) -> str:
        return f"{message}|{engine}|{language}"
