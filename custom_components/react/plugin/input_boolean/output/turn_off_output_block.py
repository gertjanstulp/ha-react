from __future__ import annotations

from homeassistant.core import Event as HaEvent
from homeassistant.const import STATE_OFF

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_INPUT_BOOLEAN
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.input_boolean.api import InputBooleanApi
from custom_components.react.plugin.input_boolean.config import InputBooleanConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class InputBooleanTurnOffOutputBlock(OutputBlock[InputBooleanConfig], ApiType[InputBooleanApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, InputBooleanTurnOffReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_INPUT_BOOLEAN, 
            STATE_OFF
        )]


    async def async_handle_event(self, react_event: InputBooleanTurnOffReactionEvent):
        react_event.session.debug(self.logger, f"Input_boolean turn off reaction caught: '{react_event.payload.entity}'")
        await self.api.async_input_boolean_turn_off(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.input_boolean_provider if react_event.payload.data else None)
        

class InputBooleanTurnOffReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.input_boolean_provider: str = None

        self.load(source)


class InputBooleanTurnOffReactionEvent(ReactionEvent[InputBooleanTurnOffReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, InputBooleanTurnOffReactionEventData)
