from __future__ import annotations

from homeassistant.components.input_text import SERVICE_SET_VALUE
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_INPUT_TEXT
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.input_text.api import InputTextApi
from custom_components.react.plugin.input_text.config import InputTextConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class InputTextSetInputBlock(OutputBlock[InputTextConfig], ApiType[InputTextApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, InputTextSetReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_INPUT_TEXT, 
            SERVICE_SET_VALUE,
        )]


    def log_event_caught(self, react_event: InputTextSetReactionEvent) -> None:
        react_event.session.debug(self.logger, f"Input_text set reaction caught: '{react_event.payload.entity}'")


    async def async_handle_event(self, react_event: InputTextSetReactionEvent):
        await self.api.async_input_text_set(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.value, 
            react_event.payload.data.input_text_provider)
        

class InputTextSetReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.input_text_provider: str = None
        self.value: float = None

        self.load(source)


class InputTextSetReactionEvent(ReactionEvent[InputTextSetReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, InputTextSetReactionEventData)
        

    @property
    def applies(self) -> bool:
        return self.payload.data is not None
