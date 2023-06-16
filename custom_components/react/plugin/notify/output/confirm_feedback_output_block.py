from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.notify.config import NotifyConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD, 
    REACT_ACTION_CONFIRM_FEEDBACK, 
    REACT_TYPE_NOTIFY
)

from custom_components.react.plugin.notify.api import NotifyApi


class NotifyConfirmFeedbackOutputBlock(OutputBlock[NotifyConfig], ApiType[NotifyApi]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, NotifyConfirmFeedbackReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_NOTIFY, 
            REACT_ACTION_CONFIRM_FEEDBACK
        )]


    async def async_handle_event(self, react_event: NotifyConfirmFeedbackReactionEvent):
        react_event.session.debug(self.logger, f"Notify confirm feedback reaction caught: '{react_event.payload.entity}'")
        await self.api.async_confirm_feedback(
            react_event.session,
            react_event.context, 
            react_event.payload.data.provider_payload.conversation_id if react_event.payload.data.provider_payload else None,
            react_event.payload.data.provider_payload.message_id if react_event.payload.data.provider_payload else None,
            react_event.payload.data.provider_payload.text if react_event.payload.data.provider_payload else None,
            react_event.payload.data.feedback,
            react_event.payload.data.acknowledgement,
            react_event.payload.data.notify_provider,
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
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, NotifyConfirmFeedbackReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_CONFIRM_FEEDBACK and
            self.payload.data
        )