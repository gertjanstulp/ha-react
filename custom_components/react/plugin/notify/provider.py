from typing import Generic, TypeVar
from homeassistant.core import Context

from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData

T_config = TypeVar("T_config", bound=DynamicData)


class NotifyProvider(Generic[T_config], PluginProviderBase[T_config]):

    async def async_notify(self, 
        session: Session,
        context: Context, 
        entity_id: str, 
        message: str, 
        feedback_items: list[FeedbackItem]
    ):
        raise NotImplementedError()
    

    async def async_confirm_feedback(self, 
        session: Session,
        context: Context, 
        conversation_id: str, 
        message_id: str, 
        text: str, 
        feedback: str,
        acknowledgement: str
    ):
        raise NotImplementedError()