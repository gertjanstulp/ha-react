from homeassistant.components.group import DOMAIN as GROUP_DOMAIN
from homeassistant.components.group.notify import GroupNotifyPlatform
from homeassistant.const import ATTR_SERVICE
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.notify.const import NOTIFY_RESOLVER_KEY, FeedbackItem
from custom_components.react.plugin.notify.resolver import NotifyPluginResolver
from custom_components.react.plugin.notify.provider import NotifyProvider
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger

_LOGGER = get_react_logger()


class GroupNotifyProvider(NotifyProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        resolver: NotifyPluginResolver = self.hass_api.hass_get_data(NOTIFY_RESOLVER_KEY)
        if not resolver:
            _LOGGER.error(f"Group plugin: Provider - Notify resolver not found, notify plugin is not configured")
            return

        group_notify_platform: GroupNotifyPlatform = resolver.get_notify_platform_item(GROUP_DOMAIN, entity_id)
        if not group_notify_platform:
            _LOGGER.error(f"Group plugin: Provider - Could not find notify platform for entity '{entity_id}'")
            return
        
        for child_entity in group_notify_platform.entities:
            if child_entity_id := child_entity.get(ATTR_SERVICE, None):
                if notify_provider_name := resolver.reverse_lookup_entity(child_entity_id):
                    if result:= self.plugin_api.get_provider(PROVIDER_TYPE_NOTIFY, notify_provider_name):
                        await result.async_notify(context, child_entity_id, message, feedback_items)
                    else:
                        _LOGGER.warn(f"Group plugin: Provider - Could not find notify provider for child entity '{child_entity_id}'")
