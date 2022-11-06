from __future__ import annotations

from telegram.utils.helpers import escape_markdown

from homeassistant.core import Event
from homeassistant.components.telegram_bot import (
    ATTR_CHAT_ID,
    ATTR_KEYBOARD_INLINE,
    ATTR_MESSAGE,
    DOMAIN,
    ATTR_MESSAGEID,
    SERVICE_EDIT_MESSAGE
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_EVENT_PLUGIN_PAYLOAD, REACT_ACTION_FEEDBACK, REACT_TYPE_NOTIFY
from custom_components.react.plugin.telegram.const import PLUGIN_NAME
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import ReactEvent, ReactionEventData
from custom_components.react.utils.struct import DynamicData


class TelegramNotifyFeedbackTask(DefaultReactionTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, TelegramNotifyFeedbackReactionEvent)


    async def async_execute_default(self, action_event: TelegramNotifyFeedbackReactionEvent):
        self.react.log.debug("TelegramNotifyPlugin: acknowledging feedback to telegram")
        await self.react.hass.services.async_call(
            DOMAIN,
            SERVICE_EDIT_MESSAGE,
            action_event.data.create_feedback_data(), 
            context=action_event.context)


class TelegramNotifyFeedbackEventProviderPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.chat_id: str = None
        self.message_id: str = None
        self.text: str = None

        self.load(source)


class TelegramNotifyFeedbackReactionEventFeedbackData(DynamicData):
    type_hints: dict = { ATTR_EVENT_PLUGIN_PAYLOAD: TelegramNotifyFeedbackEventProviderPayload }

    def __init__(self, source: dict = None) -> None:
        super().__init__(source)

        self.plugin: str = None
        self.feedback: str = None
        self.acknowledgement: str = None
        self.plugin_payload: TelegramNotifyFeedbackEventProviderPayload = None


class TelegramNotifyFeedbackReactionEventData(ReactionEventData[TelegramNotifyFeedbackReactionEventFeedbackData]):

    def __init__(self) -> None:
        super().__init__(TelegramNotifyFeedbackReactionEventFeedbackData)
    

    def create_feedback_data(self) -> dict:
        return {
            ATTR_MESSAGEID: self.data.plugin_payload.message_id,
            ATTR_CHAT_ID: self.data.plugin_payload.chat_id,
            ATTR_MESSAGE: escape_markdown(f"{self.data.plugin_payload.text} - {self.data.acknowledgement}"),
            ATTR_KEYBOARD_INLINE: None
        }

    #     self.args: list = None
    #     self.command: str = None
    #     self.user_id: str = None
    #     self.chat_id: str = None
    #     self.message: TelegramNotifyFeedbackEventDataMessage = None


    # def load(self, source: dict) -> None:
    #     super().load(source)
    #     if self.args:
    #         self.feedback = self.args[0] if len(self.args) > 0 else None
    #         self.acknowledgement = self.args[1] if len(self.args) > 1 else None


class TelegramNotifyFeedbackReactionEvent(ReactEvent[TelegramNotifyFeedbackReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, TelegramNotifyFeedbackReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.data.type == REACT_TYPE_NOTIFY and
            self.data.action == REACT_ACTION_FEEDBACK and 
            self.data.data.plugin == PLUGIN_NAME
        )

    # def __init__(self, event: Event) -> None:
    #     super().__init__(event, TelegramNotifyFeedbackEventData)
        
    #     self.event_type = event.event_type
    #     if self.data.user_id:
    #         self.data.entity = self.data.user_id
    #     if not self.data.entity and self.data.chat_id:
    #         self.data.entity = self.data.chat_id
    #     if not self.data.entity:
    #         self.data.entity = "unknown"
        

    # @property
    # def applies(self) -> bool:
    #     return (
    #         self.event_type == EVENT_TELEGRAM_CALLBACK and
    #         self.data.command == EVENTDATA_COMMAND_REACT
    #     )

    
    # def create_action_event_data(self, react: ReactBase) -> dict:
    #     entity_maps = react.configuration.workflow_config.entity_maps_config
    #     return {
    #         ATTR_ENTITY: entity_maps.get(self.data.entity, None),
    #         ATTR_TYPE: REACT_TYPE_NOTIFY,
    #         ATTR_ACTION: REACT_ACTION_FEEDBACK,
    #         ATTR_DATA: {
    #             ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: self.data.feedback
    #         }
    #     }


    # def create_feedback_data(self, react: ReactBase) -> dict:
    #     return {
    #         ATTR_MESSAGEID: self.data.message.message_id,
    #         ATTR_CHAT_ID: self.data.chat_id,
    #         ATTR_MESSAGE: escape_markdown(f"{self.data.message.text} - {self.data.acknowledgement}"),
    #         ATTR_KEYBOARD_INLINE: None
    #     }