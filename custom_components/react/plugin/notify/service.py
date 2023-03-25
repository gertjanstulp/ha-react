from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.notify.const import FeedbackItem


class NotifyService:
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        raise NotImplementedError()
    

    async def async_confirm_feedback(self, context: Context, conversation_id: str, message_id: str, text: str, acknowledgement: str):
        raise NotImplementedError()