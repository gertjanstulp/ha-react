from __future__ import annotations

from homeassistant.core import Event as HassEvent

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_EVENT_PLUGIN_PAYLOAD, 
    REACT_ACTION_CONFIRM_FEEDBACK, 
    REACT_TYPE_NOTIFY
)

from custom_components.react.plugin.notify.const import PLUGIN_NAME
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
            event.payload.data.service_type,
            event.payload.data.plugin_payload.conversation_id,
            event.payload.data.plugin_payload.message_id,
            event.payload.data.plugin_payload.text,
            event.payload.data.acknowledgement)


class NotifyConfirmFeedbackReactionEventPluginPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.conversation_id: str = None
        self.message_id: str = None
        self.text: str = None

        self.load(source)


class NotifyConfirmFeedbackReactionEventData(DynamicData):
    type_hints: dict = { ATTR_EVENT_PLUGIN_PAYLOAD: NotifyConfirmFeedbackReactionEventPluginPayload }

    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.plugin: str = None
        self.service_type: str = None
        self.feedback: str = None
        self.acknowledgement: str = None
        self.plugin_payload: NotifyConfirmFeedbackReactionEventPluginPayload = None

        self.load(source)
        

class NotifyConfirmFeedbackReactionEvent(ReactionEvent[NotifyConfirmFeedbackReactionEventData]):
    
    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event, NotifyConfirmFeedbackReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_CONFIRM_FEEDBACK and 
            self.payload.data and
            (not self.payload.data.plugin or self.payload.data.plugin == PLUGIN_NAME)
        )