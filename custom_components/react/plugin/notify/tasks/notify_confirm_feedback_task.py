from __future__ import annotations

from homeassistant.core import Event as HassEvent

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD, 
    REACT_ACTION_CONFIRM_FEEDBACK, 
    REACT_TYPE_NOTIFY
)

from custom_components.react.plugin.notify.api import NotifyApi

_LOGGER = get_react_logger()


class NotifyConfirmFeedbackTask(PluginReactionTask):
    def __init__(self, react: ReactBase, api: NotifyApi) -> None:
        super().__init__(react, NotifyConfirmFeedbackReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Notify plugin: NotifyConfirmFeedbackTask - {message}")


    async def async_execute_plugin(self, event: NotifyConfirmFeedbackReactionEvent):
        self._debug("Confirming feedback")
        await self.api.async_confirm_feedback(
            event.context, 
            event.payload.data.provider_payload.conversation_id if event.payload.data.provider_payload else None,
            event.payload.data.provider_payload.message_id if event.payload.data.provider_payload else None,
            event.payload.data.provider_payload.text if event.payload.data.provider_payload else None,
            event.payload.data.feedback,
            event.payload.data.acknowledgement,
            event.payload.data.notify_provider,
        )


class NotifyConfirmFeedbackReactionEventProviderPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.conversation_id: str = None
        self.message_id: str = None
        self.text: str = None

        self.load(source)


class NotifyConfirmFeedbackReactionEventData(DynamicData):
    type_hints: dict = { ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: NotifyConfirmFeedbackReactionEventProviderPayload }

    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.feedback: str = None
        self.acknowledgement: str = None
        self.provider_payload: NotifyConfirmFeedbackReactionEventProviderPayload = None
        self.notify_provider: str = None

        self.load(source)
        

class NotifyConfirmFeedbackReactionEvent(ReactionEvent[NotifyConfirmFeedbackReactionEventData]):
    
    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event, NotifyConfirmFeedbackReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_CONFIRM_FEEDBACK and
            self.payload.data
        )