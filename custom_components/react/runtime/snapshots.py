from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant

from custom_components.react.utils.context import ActorTemplateContextDataProvider
from custom_components.react.utils.events import ActionEvent
from custom_components.react.utils.jit import ObjectJitter
from custom_components.react.utils.struct import ActorRuntime, DynamicData, ReactorRuntime
from custom_components.react.utils.track import ObjectTracker


class WorkflowSnapshot:
    def __init__(self,
        variables: DynamicData = None,
        actor: ActorRuntime = None,
        reactors: list[ReactorRuntime] = None,
        action_event: ActionEvent = None,
    ) -> None:
        self.variables = variables
        self.actor = actor
        self.reactors = reactors
        self.action_event = action_event


def create_snapshot(
    hass: HomeAssistant, 
    variables_tracker: ObjectTracker[DynamicData],
    actor_tracker: ObjectTracker[ActorRuntime],
    reactor_jitters: list[ObjectJitter[ReactorRuntime]], 
    action_event: ActionEvent
):
    template_context_data_provider = ActorTemplateContextDataProvider(hass, action_event.payload, actor_tracker.value_container.id)

    result = WorkflowSnapshot(
        action_event = action_event,
        variables = variables_tracker.value_container,
        actor = actor_tracker.value_container,
        reactors = [ jitter.render(template_context_data_provider) for jitter in reactor_jitters ]
    )
    return result