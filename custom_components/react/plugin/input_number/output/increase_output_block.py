from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_INCREASE, REACT_TYPE_INPUT_NUMBER
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.input_number.api import InputNumberApi
from custom_components.react.plugin.input_number.config import InputNumberConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class InputNumberIncreaseOutputBlock(OutputBlock[InputNumberConfig], ApiType[InputNumberApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, InputNumberIncreaseReactionEvent)
        
        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_INPUT_NUMBER, 
            REACT_ACTION_INCREASE,
        )]


    async def async_handle_event(self, react_event: InputNumberIncreaseReactionEvent):
        react_event.session.debug(self.logger, f"Input_number increase reaction caught: '{react_event.payload.entity}'")
        await self.api.async_input_number_increase(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.value, 
            react_event.payload.data.max, 
            react_event.payload.data.input_number_provider)
        

class InputNumberIncreaseReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.input_number_provider: str = None
        self.value: float = None
        self.max: float = None

        self.load(source)


class InputNumberIncreaseReactionEvent(ReactionEvent[InputNumberIncreaseReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, InputNumberIncreaseReactionEventData)
        

    @property
    def applies(self) -> bool:
        return self.payload.data is not None
