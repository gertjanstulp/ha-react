from threading import Lock
from typing import Any

from homeassistant.components.notify.legacy import NOTIFY_SERVICES

from custom_components.react.plugin.api import HassApi, PluginApi


class NotifyPluginResolver():
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        self.plugin_api = plugin_api
        self.hass_api = hass_api
        self._notify_entity_reverse_lookup: dict[str, str] = {}
        self._notification_platforms: dict[str, dict[str, list]] = {}

        self._lock = Lock()
        self._resolved: bool = False

    def load(self):
        if not self._resolved:
            with self._lock:
                if not self._resolved:
                    notify_services_dict: dict = self.hass_api.hass_get_data(NOTIFY_SERVICES)
                    if not notify_services_dict: return
                    
                    for domain,domain_services in notify_services_dict.items():
                        for domain_service in domain_services:
                            if hasattr(domain_service, "registered_targets") and domain_service.registered_targets:
                                for registered_target in domain_service.registered_targets:
                                    self._notify_entity_reverse_lookup[registered_target] = domain
                            else:
                                self._notify_entity_reverse_lookup[domain_service._service_name] = domain
                        self._notification_platforms[domain] = { item._service_name: item for item in domain_services }

                    self._resolved = True


    def reverse_lookup_entity(self, entity_id: str, default: Any = None) -> Any:
        return self._notify_entity_reverse_lookup.get(entity_id, default)


    def get_notify_platform_item(self, domain: str, entity_id: str):
        result = None
        domain_items = self._notification_platforms.get(domain, None)
        if domain_items:
            result = domain_items.get(entity_id, None)
        return result
