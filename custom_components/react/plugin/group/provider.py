from homeassistant.components.group import DOMAIN as GROUP_DOMAIN
from homeassistant.components.group.notify import GroupNotifyPlatform
from homeassistant.const import ATTR_SERVICE
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.notify.const import NOTIFY_RESOLVER_KEY, FeedbackItem
from custom_components.react.plugin.notify.resolver import NotifyPluginResolver
from custom_components.react.plugin.notify.provider import NotifyProvider
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData


class GroupProvider(NotifyProvider[DynamicData]):

    async def async_notify(self, session: Session, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        session.debug(self.logger, f"Sending message to {entity_id}")
        resolver: NotifyPluginResolver = self.plugin.hass_api.hass_get_data(NOTIFY_RESOLVER_KEY)
        if not resolver:
            session.error(self.plugin.logger, f"Notify resolver not found, notify plugin is not configured")
            return

        group_notify_platform: GroupNotifyPlatform = resolver.get_notify_platform_item(GROUP_DOMAIN, entity_id)
        if not group_notify_platform:
            session.error(self.plugin.logger, f"Could not find notify platform for entity '{entity_id}'")
            return
        
        for child_entity in group_notify_platform.entities:
            if child_entity_id := child_entity.get(ATTR_SERVICE, None):
                if notify_provider := resolver.reverse_lookup_entity(child_entity_id):
                    if result:= self.plugin.get_provider(PROVIDER_TYPE_NOTIFY, notify_provider):
                        await result.async_notify(session, context, child_entity_id, message, feedback_items)
                    else:
                        session.warning(self.plugin.logger, f"Could not find notify provider for child entity '{child_entity_id}'")
                