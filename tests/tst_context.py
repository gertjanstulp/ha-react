from __future__ import annotations

import yaml

from asyncio import sleep
from contextlib import asynccontextmanager
from deepdiff import DeepDiff
from typing import Any, Callable, Union
from yaml import SafeLoader

from homeassistant.components import (
    alarm_control_panel, 
    binary_sensor, 
    device_tracker,
    fan,
    group, 
    input_boolean, 
    input_button, 
    input_number, 
    input_text, 
    light, 
    media_player,
    person, 
    sensor,
    switch,
    template,
)
from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_DOMAIN
from homeassistant.components.trace.const import DATA_TRACE
from homeassistant.const import (
    ATTR_CODE,
    ATTR_ENTITY_ID, 
    ATTR_STATE, 
    SERVICE_ALARM_ARM_AWAY,
    STATE_ON,
)
from homeassistant.core import Event as HaEvent, HomeAssistant, State
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.setup import async_setup_component

from unittest.mock import Mock

from custom_components.react.base import ReactBase
from custom_components.react.config.config import Workflow
from custom_components.react.runtime.runtime import Reaction, WorkflowRun
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData, MultiItem
from custom_components.react.utils.trace import ReactTrace
from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_ACTOR,
    ATTR_CONDITION,
    ATTR_DATA,
    ATTR_DELAY,
    ATTR_DELAY_HOURS,
    ATTR_DELAY_MINUTES,
    ATTR_DELAY_SECONDS,
    ATTR_ENABLED,
    ATTR_ENTITY,
    ATTR_EVENT,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_ID,
    ATTR_INDEX,
    ATTR_REACTOR,
    ATTR_REACTOR_ID,
    ATTR_RESET_WORKFLOW,
    ATTR_SCHEDULE,
    ATTR_SCHEDULE_AT,
    ATTR_SCHEDULE_WEEKDAYS,
    ATTR_TEMPLATE,
    ATTR_THIS,
    ATTR_TRIGGER,
    ATTR_TYPE,
    ATTR_VARIABLES,
    ATTR_WAIT,
    ATTR_WAIT_CONDITION,
    DOMAIN, 
    EVENT_REACT_ACTION,
    EVENT_REACT_REACTION,
    MONIKER_DISPATCH,
    MONIKER_RESET,
    TRACE_PATH_ACTOR,
    TRACE_PATH_CONDITION,
    TRACE_PATH_DELAY,
    TRACE_PATH_DISPATCH,
    TRACE_PATH_REACTOR,
    TRACE_PATH_RESET,
    TRACE_PATH_SCHEDULE,
    TRACE_PATH_STATE,
)
from custom_components.virtual import SERVICE_AVAILABILE
from custom_components.virtual.binary_sensor import SERVICE_ON
from custom_components.virtual.const import COMPONENT_DOMAIN as VIRTUAL_DOMAIN
from custom_components.virtual.sensor import SERVICE_SET


from tests._mocks.mock_log_handler import MockLogHandler
from tests.common import (
    ALARM_CONFIG,
    BINARY_SENSOR_CONFIG,
    DEVICE_TRACKER_CONFIG,
    EVENT_TEST_CALLBACK,
    FAN_CONFIG,
    GROUP_CONFIG,
    INPUT_BOOLEAN_CONFIG,
    INPUT_BUTTON_CONFIG,
    INPUT_NUMBER_CONFIG,
    INPUT_TEXT_CONFIG,
    LIGHT_CONFIG,
    MEDIA_PLAYER_CONFIG,
    PERSON_CONFIG,
    SENSOR_CONFIG,
    SWITCH_CONFIG,
    TEMPLATE_CONFIG,
    TEST_CONTEXT,
    get_test_config_dir,
)
from tests.const import ALARM_CODE, ATTR_DOMAIN, ATTR_SERVICE_NAME

ACTOR_ID_PREFIX = "actor_"
ACTOR_ENTITY_PREFIX = "actor_entity_"
ACTOR_TYPE_PREFIX = "actor_type_"
ACTOR_ACTION_PREFIX = "actor_action_"

REACTOR_ID_PREFIX = "reactor_"
REACTOR_ENTITY_PREFIX = "reactor_entity_"
REACTOR_TYPE_PREFIX = "reactor_type_"
REACTOR_ACTION_PREFIX = "reactor_action_"

TRACE_CHANGED_VARIABLES = "changed_variables"
TRACE_CONTEXT = "context"
TRACE_RESULT = "result"
TRACE_PARALLEL = "parallel"
TRACE_PATH = "path"
TRACE_REACTION = "reaction"
TRACE_TRACE = "trace"
TRACE_CONFIG = "config"
TRACE_DOMAIN = "domain"
TRACE_ITEM_ID = "item_id"
TRACE_MESSAGE = "message"


class TstContext():
    
    def __init__(self, hass: HomeAssistant, react_component, workflow_name: str) -> None:
        self.hass = hass
        self.workflow_name = workflow_name
        self.react_component = react_component

        self.action_event_mock = Mock()
        self.reaction_event_mock = Mock()

        if workflow_name != None:
            self.workflow_id = f"workflow_{workflow_name}"

        self.plugin_data_register: list[dict] = []
        self.service_call_register: list[dict] = []
        self.notify_confirm_feedback_register: list[dict] = []
        self.plugin_task_unloaded_register: list[str] = []

        react_logger = get_react_logger()
        react_logger.setLevel("DEBUG")
        self.mock_log_handler = MockLogHandler()
        react_logger.addHandler(self.mock_log_handler)

        hass.data[TEST_CONTEXT] = self


    async def async_start_react(self, mock_plugins: list[dict] = [], additional_workflows: list[str] = [], process_workflow: callable(dict) = None, skip_setup: bool = False):
        if not skip_setup:
            await self.react_component.async_setup(
                workflow_name=self.workflow_name,
                additional_workflows=additional_workflows, 
                plugins=mock_plugins,
                process_workflow=process_workflow,
            )
        self.react: ReactBase = self.hass.data.get(DOMAIN, None)
        self.workflow_config = self.react.configuration.workflow_config.workflows.get(self.workflow_id)
        return self


    async def async_start_binary_sensor(self):
        hass: HomeAssistant = self.hass
        with open(get_test_config_dir(BINARY_SENSOR_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(hass, binary_sensor.DOMAIN, { binary_sensor.DOMAIN: data })
        await hass.async_block_till_done()


    async def async_start_virtual(self):
        assert await async_setup_component(self.hass, VIRTUAL_DOMAIN, { VIRTUAL_DOMAIN: { "yaml_config": True}} )
        await self.hass.async_block_till_done()

        async def async_turn_on(domain: str, name: str):
            await self.hass.services.async_call(
                VIRTUAL_DOMAIN,
                SERVICE_ON,
                {
                    ATTR_ENTITY_ID: f"{domain}.{name}"
                }
            )
            await self.hass.async_block_till_done()

        async def async_set(domain: str, name: str, value: Any):
            await self.hass.services.async_call(
                VIRTUAL_DOMAIN,
                SERVICE_SET,
                {
                    ATTR_ENTITY_ID: f"{domain}.{name}",
                    input_number.ATTR_VALUE: value
                }
            )
            await self.hass.async_block_till_done()

        async def async_set_available(domain: str, name: str):
            await self.hass.services.async_call(
                VIRTUAL_DOMAIN,
                SERVICE_AVAILABILE,
                {
                    ATTR_ENTITY_ID: f"{domain}.{name}",
                    input_number.ATTR_VALUE: True
                }
            )
            await self.hass.async_block_till_done()

        async def async_set_unavailable(domain: str, name: str):
            await self.hass.services.async_call(
                VIRTUAL_DOMAIN,
                SERVICE_AVAILABILE,
                {
                    ATTR_ENTITY_ID: f"{domain}.{name}",
                    input_number.ATTR_VALUE: False
                }
            )
            await self.hass.async_block_till_done()
    

        result = Mock()
        result.async_turn_on = async_turn_on
        result.async_set = async_set
        result.async_set_available = async_set_available
        result.async_set_unavailable = async_set_unavailable
        return result


    async def async_start_group(self):
        with open(get_test_config_dir(GROUP_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, group.DOMAIN, { group.DOMAIN: data })
        await self.hass.async_block_till_done()


    async def async_start_person(self):
        with open(get_test_config_dir(PERSON_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, person.DOMAIN, { person.DOMAIN: data })
        await self.hass.async_block_till_done()


    async def async_start_device_tracker(self):
        with open(get_test_config_dir(DEVICE_TRACKER_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, device_tracker.DOMAIN, { device_tracker.DOMAIN: data })
        await self.hass.async_block_till_done()
        
        async def async_see(dev_id: str, location: str):
            self.hass.async_create_task(self.hass.services.async_call(
                device_tracker.DOMAIN,
                device_tracker.SERVICE_SEE,
                {
                    device_tracker.ATTR_DEV_ID: dev_id,
                    device_tracker.ATTR_LOCATION_NAME: location,
                    device_tracker.ATTR_SOURCE_TYPE: SourceType.ROUTER,
                }
            ))
            await self.hass.async_block_till_done()

        result = Mock()
        result.async_see = async_see
        return result
    

    async def async_start_input_number(self):
        with open(get_test_config_dir(INPUT_NUMBER_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, input_number.DOMAIN, { input_number.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_set_value(name: str, value: float):
            await self.hass.services.async_call(
                input_number.DOMAIN,
                input_number.SERVICE_SET_VALUE,
                {
                    ATTR_ENTITY_ID: f"input_number.{name}",
                    input_number.ATTR_VALUE: value
                }
            )
            await self.hass.async_block_till_done()

        result = Mock()
        result.async_set_value = async_set_value
        return result
    

    async def async_start_input_text(self):
        with open(get_test_config_dir(INPUT_TEXT_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, input_text.DOMAIN, { input_text.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_set_value(name: str, value: str):
            await self.hass.services.async_call(
                input_text.DOMAIN,
                input_text.SERVICE_SET_VALUE,
                {
                    ATTR_ENTITY_ID: f"input_text.{name}",
                    input_text.ATTR_VALUE: value,
                }
            )
            await self.hass.async_block_till_done()

        result = Mock()
        result.async_set_value = async_set_value
        return result
    

    async def async_start_input_boolean(self):
        with open(get_test_config_dir(INPUT_BOOLEAN_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, input_boolean.DOMAIN, { input_boolean.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_turn_on(name: str):
            await self.hass.services.async_call(
                input_boolean.DOMAIN,
                input_boolean.SERVICE_TURN_ON,
                {
                    ATTR_ENTITY_ID: f"input_boolean.{name}"
                }
            )
            await self.hass.async_block_till_done()

        async def async_turn_off(name: str):
            await self.hass.services.async_call(
                input_boolean.DOMAIN,
                input_boolean.SERVICE_TURN_OFF,
                {
                    ATTR_ENTITY_ID: f"input_boolean.{name}"
                }
            )
            await self.hass.async_block_till_done()

        result = Mock()
        result.async_turn_on = async_turn_on
        result.async_turn_off = async_turn_off
        return result
    

    async def async_start_input_button(self):
        with open(get_test_config_dir(INPUT_BUTTON_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, input_button.DOMAIN, { input_button.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_press(name: str):
            await self.hass.services.async_call(
                input_button.DOMAIN,
                input_button.SERVICE_PRESS,
                {
                    ATTR_ENTITY_ID: f"input_button.{name}"
                }
            )
            await self.hass.async_block_till_done()

        result = Mock()
        result.async_press = async_press
        return result
    

    async def async_start_light(self):
        with open(get_test_config_dir(LIGHT_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, light.DOMAIN, { light.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_turn_on(name: str):
            await self.hass.services.async_call(
                light.DOMAIN,
                light.SERVICE_TURN_ON,
                {
                    ATTR_ENTITY_ID: f"light.{name}"
                }
            )
            await self.hass.async_block_till_done()

        async def async_turn_off(name: str):
            await self.hass.services.async_call(
                light.DOMAIN,
                light.SERVICE_TURN_OFF,
                {
                    ATTR_ENTITY_ID: f"light.{name}"
                }
            )
            await self.hass.async_block_till_done()

        result = Mock()
        result.async_turn_on = async_turn_on
        result.async_turn_off = async_turn_off
        return result
    

    async def async_start_alarm(self):
        with open(get_test_config_dir(ALARM_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, alarm_control_panel.DOMAIN, { alarm_control_panel.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_arm_home(name: str):
            await self.hass.services.async_call(
                alarm_control_panel.DOMAIN,
                alarm_control_panel.SERVICE_ALARM_ARM_HOME,
                {
                    ATTR_ENTITY_ID: f"{alarm_control_panel.DOMAIN}.{name}",
                    alarm_control_panel.ATTR_CODE: ALARM_CODE,
                }
            )
            await self.hass.async_block_till_done()

        async def async_arm_away(name: str):
            await self.hass.services.async_call(
                alarm_control_panel.DOMAIN,
                alarm_control_panel.SERVICE_ALARM_ARM_AWAY,
                {
                    ATTR_ENTITY_ID: f"{alarm_control_panel.DOMAIN}.{name}",
                    alarm_control_panel.ATTR_CODE: ALARM_CODE,
                }
            )
            await self.hass.async_block_till_done()

        result = Mock()
        result.async_arm_home = async_arm_home
        result.async_arm_away = async_arm_away
        return result
    

    async def async_start_switch(self):
        with open(get_test_config_dir(SWITCH_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, switch.DOMAIN, { switch.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_turn_on(name: str):
            await self.hass.services.async_call(
                switch.DOMAIN,
                switch.SERVICE_TURN_ON,
                {
                    ATTR_ENTITY_ID: f"switch.{name}"
                }
            )
            await self.hass.async_block_till_done()

        async def async_turn_off(name: str):
            await self.hass.services.async_call(
                switch.DOMAIN,
                switch.SERVICE_TURN_OFF,
                {
                    ATTR_ENTITY_ID: f"switch.{name}"
                }
            )
            await self.hass.async_block_till_done()

        result = Mock()
        result.async_turn_on = async_turn_on
        result.async_turn_off = async_turn_off
        return result


    async def async_start_sensor(self):
        with open(get_test_config_dir(SENSOR_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, sensor.DOMAIN, { sensor.DOMAIN: data })
        await self.hass.async_block_till_done()


    async def async_start_template(self):
        with open(get_test_config_dir(TEMPLATE_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, template.DOMAIN, { template.DOMAIN: data })
        await self.hass.async_block_till_done()


    async def async_start_media_player(self):
        with open(get_test_config_dir(MEDIA_PLAYER_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, media_player.DOMAIN, { media_player.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_play_media(name: str, media_content_id: str, media_content_type: str):
            await self.hass.services.async_call(
                media_player.DOMAIN,
                media_player.SERVICE_PLAY_MEDIA,
                {
                    ATTR_ENTITY_ID: f"media_player.{name}",
                    media_player.ATTR_MEDIA_CONTENT_ID: media_content_id,
                    media_player.ATTR_MEDIA_CONTENT_TYPE: media_content_type,
                }
            )

        result = Mock()
        result.async_play_media = async_play_media
        return result
    

    async def async_start_fan(self):
        with open(get_test_config_dir(FAN_CONFIG)) as f:
            data = yaml.load(f, Loader=SafeLoader) or {}
        assert await async_setup_component(self.hass, fan.DOMAIN, { fan.DOMAIN: data })
        await self.hass.async_block_till_done()

        async def async_set_percentage(name: str, percentage: int):
            await self.hass.services.async_call(
                fan.DOMAIN,
                fan.SERVICE_SET_PERCENTAGE,
                {
                    ATTR_ENTITY_ID: f"fan.{name}",
                    fan.ATTR_PERCENTAGE: percentage,
                }
            )
            await self.hass.async_block_till_done()


        async def async_increase(name: str, percentage_step: int = None):
            service_data = {
                ATTR_ENTITY_ID: f"fan.{name}",
            }
            if percentage_step:
                service_data[fan.ATTR_PERCENTAGE_STEP] = percentage_step,
            await self.hass.services.async_call(
                fan.DOMAIN,
                fan.SERVICE_INCREASE_SPEED,
                service_data,
            )
            await self.hass.async_block_till_done()


        async def async_decrease(name: str, percentage_step: int = None):
            service_data = {
                ATTR_ENTITY_ID: f"fan.{name}",
            }
            if percentage_step:
                service_data[fan.ATTR_PERCENTAGE_STEP] = percentage_step,
            await self.hass.services.async_call(
                fan.DOMAIN,
                fan.SERVICE_DECREASE_SPEED,
                service_data,
            )
            await self.hass.async_block_till_done()
            

        # async def async_turn_off(name: str):
        #     await self.hass.services.async_call(
        #         fan.DOMAIN,
        #         fan.SERVICE_TURN_OFF,
        #         {
        #             ATTR_ENTITY_ID: f"fan.{name}"
        #         }
        #     )
        #     await self.hass.async_block_till_done()

        result = Mock()
        result.async_set_percentage = async_set_percentage
        result.async_increase = async_increase
        result.async_decrease = async_decrease
        return result


    def verify_has_log_record(self, level_name: str, message: str):
        assert self.mock_log_handler.has_record(level_name, message), f"Could not find {level_name} record with message '{message}'"


    def verify_has_no_log_record(self, level_name: str, message: str):
        assert self.mock_log_handler.has_no_record(level_name, message), f"Found {level_name} record with message '{message}'"

    
    def verify_has_no_log_info(self, message: str):
        self.verify_has_no_log_record("INFO", message)


    def verify_has_no_log_debug(self, message: str):
        self.verify_has_no_log_record("DEBUG", message)


    def verify_has_log_info(self, message: str):
        self.verify_has_log_record("INFO", message)

        
    def verify_has_log_warning(self, message: str):
        self.verify_has_log_record("WARNING", message)


    def verify_has_log_error(self, message: str):
        self.verify_has_log_record("ERROR", message)


    def verify_has_no_log_issues(self):
        assert self.mock_log_handler.has_no_issues(), "One or more warnings and/or errors occured"        
    

    async def async_send_action_event(self, 
        entity: str = None, 
        type: str = None, 
        action: str = None, 
        data: dict = None, 
        actor_index: int = 0,
        entity_index: int = 0,
        type_index: int = 0,
        action_index: int = 0,
    ):
        workflow_config_actor = self.workflow_config.actors[actor_index]
        event_data = {
            ATTR_ENTITY: entity or workflow_config_actor.entity[entity_index],
            ATTR_TYPE: type or workflow_config_actor.type[type_index],
            ATTR_ACTION: action or workflow_config_actor.action[action_index],
            ATTR_DATA: data
        }
        self.hass.bus.async_fire(EVENT_REACT_ACTION, event_data)
        await self.hass.async_block_till_done()


    async def async_send_reaction_event(self,
        entity: str = None, 
        type: str = None, 
        action: str = None, 
        data: dict = None, 
        reactor_index: int = 0,
        entity_index: int = 0,
        type_index: int = 0,
        action_index: int = 0,
    ):
        workflow_config_reactor = self.workflow_config.reactors[reactor_index]
        event_data = {
            ATTR_ENTITY: entity or workflow_config_reactor.entity[entity_index],
            ATTR_TYPE: type or workflow_config_reactor.type[type_index],
            ATTR_ACTION: action or workflow_config_reactor.action[action_index],
            ATTR_DATA: data
        }
        self.hass.bus.async_fire(EVENT_REACT_REACTION, event_data)
        await self.hass.async_block_till_done()


    async def async_send_event(self, event_type: str, event_data: dict):
        self.hass.bus.async_fire(event_type, event_data)
        await self.hass.async_block_till_done()


    @asynccontextmanager
    async def async_listen_reaction_event(self):
        try:
            self.cancel_listen = self.hass.bus.async_listen(EVENT_REACT_REACTION, self.reaction_event_mock)
            yield
        finally:
            if self.cancel_listen:
                self.cancel_listen()


    @asynccontextmanager
    async def async_listen_action_event(self):
        try:
            self.cancel_listen = self.hass.bus.async_listen(EVENT_REACT_ACTION, self.action_event_mock)
            yield
        finally:
            if self.cancel_listen:
                self.cancel_listen()


    async def async_stop_all_runs(self, workflow_id: str = None):
        if not workflow_id:
            workflow_id = self.workflow_id
        await self.react.runtime.async_stop_workflow_runtime(workflow_id)


    def reset(self):
        self.action_event_mock.reset_mock()
        self.reaction_event_mock.reset_mock()
        self.plugin_data_register.clear()
        self.notify_confirm_feedback_register.clear()
        self.plugin_task_unloaded_register.clear()


    def retrieve_workflow_entity(self):
        states = [ state for state in self.hass.states.async_all(DOMAIN) if state.entity_id == f"react.{self.workflow_id}" ]
        return states[0]


    def retrieve_runs(self) -> list[WorkflowRun]:
        return list(self.react.runtime.run_registry.find())


    def verify_run_count(self, expected_count: int = 1):
        runs = self.retrieve_runs()
        got_count = len(runs)
        assert got_count == expected_count, f"Expected run count {expected_count}, got {got_count}"


    def verify_run_not_found(self) -> None:
        self.verify_run_count(0)


    def verify_run_found(self, expected_count: int = 1) -> None:
        self.verify_run_count(expected_count)


    def retrieve_run_id(self):
        run = self.retrieve_runs()[0]
        return run.id


    def retrieve_reactions(self) -> list[Reaction]:
        return list(self.react.runtime.reaction_registry.find())


    def verify_reaction_count(self, expected_count: int = 1):
        reactions = self.retrieve_reactions()
        got_count = len(reactions)
        assert got_count == expected_count, f"Expected reaction count {expected_count}, got {got_count}"


    def verify_reaction_not_found(self) -> None:
        self.verify_reaction_count(0)


    def verify_reaction_found(self, expected_count: int = 1) -> None:
        self.verify_reaction_count(expected_count)


    def verify_reaction_entity_data(self, 
        expected_entity: str = None, 
        expected_type: str = None, 
        expected_action: str = None, 
        reactor_index: int = 0,
        entity_index: int = 0,
        type_index: int = 0,
        action_index: int = 0,
    ):
        reaction_entity: State = self.retrieve_reactions()[0]

        workflow_config_reactor = self.workflow_config.reactors[reactor_index]

        self.verify_reaction_entity_data_item(ATTR_ENTITY, reaction_entity, workflow_config_reactor.entity, expected_entity, entity_index)
        self.verify_reaction_entity_data_item(ATTR_TYPE, reaction_entity, workflow_config_reactor.type, expected_type, type_index)
        self.verify_reaction_entity_data_item(ATTR_ACTION, reaction_entity, workflow_config_reactor.action, expected_action, action_index)

    
    def verify_reaction_entity_data_item(self, attr: str, reaction_entity: State, multi_item: MultiItem, expected_value: Any = None, item_index: int = 0):
        got_value = reaction_entity.attributes.get(attr, None)
        expected_value = expected_value or multi_item[item_index]
        assert got_value == expected_value, f"Expected reaction entity {attr} '{expected_value}', got '{got_value}'"


    def retrieve_reaction_id(self):
        reaction = self.retrieve_reactions()[0]
        return reaction.id


    def verify_action_event_count(self, expected_count: int = 1):
        got_count = self.action_event_mock.call_count
        assert got_count == expected_count, f"Expected event count {expected_count}, got {got_count}"


    async def async_verify_action_event_not_received(self) -> None:
        self.verify_action_event_count(0)


    async def async_verify_action_event_received(self, expected_count: int = 1) -> None:
        self.verify_action_event_count(expected_count)
        for i,call in enumerate(self.action_event_mock.mock_calls):
            assert len(call.args) > 0, f"Expected args for call {i}, got none"


    def verify_action_event_data(self, 
        expected_entity: str = None,
        expected_type: str = None,
        expected_action: str = None,
        expected_data: dict = None,
        event_index: int = 0, 
        entity_index: int = 0,
        type_index: int = 0,
        action_index: int = 0,
    ):
        ha_event: HaEvent = self.action_event_mock.mock_calls[event_index].args[0]
        
        self.verify_event_data_item(ATTR_ENTITY, ha_event, None, expected_entity, entity_index)
        self.verify_event_data_item(ATTR_TYPE, ha_event, [EVENT_REACT_ACTION], expected_type, type_index)
        self.verify_event_data_item(ATTR_ACTION, ha_event, None, expected_action, action_index)
        self.verify_event_data_item(ATTR_DATA, ha_event, None, expected_data, -1)


        # event_type_got = ha_event.event_type
        # event_type_expected = expected_type or EVENT_REACT_ACTION
        # assert event_type_got == event_type_expected, f"Expected eventtype '{event_type_expected}', got '{event_type_got}'"
        
        # data_got = ha_event.data
        # assert DeepDiff(data_got, expected_data) == {}, f"Expected event entity '{expected_data}', got '{data_got}'"


    def verify_reaction_event_count(self, expected_count: int = 1, at_least_count: bool = False):
        got_count = self.reaction_event_mock.call_count
        if at_least_count:
            assert got_count >= expected_count, f"Expected event count {expected_count}, got {got_count}"
        else:
            assert got_count == expected_count, f"Expected event count {expected_count}, got {got_count}"


    async def async_verify_reaction_event_not_received(self) -> None:
        self.verify_reaction_event_count(0)


    async def async_verify_reaction_event_received(self, expected_count: int = 1, at_least_count: bool = False) -> None:
        self.verify_reaction_event_count(expected_count, at_least_count)
        for i,call in enumerate(self.reaction_event_mock.mock_calls):
            assert len(call.args) > 0, f"Expected args for call {i}, got none"


    def verify_reaction_event_data(self,
        expected_entity: str = None, 
        expected_type: str = None, 
        expected_action: str = None, 
        expected_data: dict = None, 
        event_index: int = 0,
        reactor_index: int = 0,
        entity_index: int = 0,
        type_index: int = 0,
        action_index: int = 0,
    ):
        ha_event: HaEvent = self.reaction_event_mock.mock_calls[event_index].args[0]
        event_type_got = ha_event.event_type
        event_type_expected = EVENT_REACT_REACTION
        assert event_type_got == event_type_expected, f"Expected eventtype '{event_type_expected}', got '{event_type_got}'"

        workflow_config_reactor = self.workflow_config.reactors[reactor_index]

        self.verify_event_data_item(ATTR_ENTITY, ha_event, workflow_config_reactor.entity, expected_entity, entity_index)
        self.verify_event_data_item(ATTR_TYPE, ha_event, workflow_config_reactor.type, expected_type, type_index)
        self.verify_event_data_item(ATTR_ACTION, ha_event, workflow_config_reactor.action, expected_action, action_index)
        self.verify_event_data_item(ATTR_DATA, ha_event, workflow_config_reactor.data, expected_data, -1)


    def verify_event_data_item(self, attr: str, ha_event: HaEvent, multi_item_or_list: Union[MultiItem, list], expected_value: Any = None, item_index: int = 0):
        got_value = ha_event.data.get(attr, None)
        expected_value = expected_value or (multi_item_or_list[item_index] if multi_item_or_list else None)
        assert DeepDiff(got_value, expected_value) == {}, f"Expected event {attr} '{expected_value}', got '{got_value}'"


    def verify_trace_record(self, 
        actor_index: int = 0, 
        actor_entity_index = 0,
        actor_type_index = 0,
        actor_action_index = 0,
        actor_data_index = 0,
        expected_runtime_actor_entity: str = None, 
        expected_runtime_actor_type: str = None, 
        expected_runtime_actor_action: str = None, 
        expected_runtime_actor_data: dict = None,
        expected_runtime_reactor_entity: list[str] = None, 
        expected_runtime_reactor_type: list[str] = None, 
        expected_runtime_reactor_action: list[str] = None, 
        expected_runtime_reactor_data: list[dict] = None,
        expected_runtime_reactor_delay_seconds: int = None,
        expected_runtime_reactor_delay_minutes: int = None,
        expected_runtime_reactor_delay_hours: int = None,
        expected_result_message: str = None,
        expected_actor_condition_result: bool = True,
        expected_reactor_condition_results: list[bool] = None,
        expected_event_trace: bool = True,
    ):

        # Initialize expectation lists
        if not expected_reactor_condition_results:
            expected_reactor_condition_results = [True] * len(self.workflow_config.reactors)
        if not expected_runtime_reactor_entity:
            expected_runtime_reactor_entity = [None] * len(self.workflow_config.reactors)
        if not expected_runtime_reactor_type:
            expected_runtime_reactor_type = [None] * len(self.workflow_config.reactors)
        if not expected_runtime_reactor_action:
            expected_runtime_reactor_action = [None] * len(self.workflow_config.reactors)
        if not expected_runtime_reactor_data:
            expected_runtime_reactor_data = [None] * len(self.workflow_config.reactors)

        trace_data: dict = self.hass.data[DATA_TRACE]
        key = f"{DOMAIN}.{self.workflow_id}"
        test_traces: dict = assert_dict_property_value_not_none(trace_data, key)
        test_trace: ReactTrace = list(test_traces.values())[0]

        trace = TracePath(test_trace.as_extended_dict(), TRACE_TRACE)

        trace.assert_property_match(TRACE_DOMAIN, DOMAIN)
        trace.assert_property_match(TRACE_ITEM_ID, self.workflow_id)
        
        ########## Trace config ##########

        trace_config = trace.assert_property_not_none(TRACE_CONFIG)
        trace_config.assert_property_match(ATTR_ID, self.workflow_id)
        
        # Test for actor configuration in trace data
        for i in range(0, len(self.workflow_config.actors)):
            workflow_config_actor = self.workflow_config.actors[i]
            trace_config_actor = trace_config.assert_property_list_item(ATTR_ACTOR, i)
            trace_config_actor.assert_property_match(ATTR_INDEX, i)
            trace_config_trigger = trace_config_actor.assert_property_not_none(ATTR_TRIGGER)
            trace_config_trigger.assert_property_match(ATTR_ID, workflow_config_actor.id)
            if workflow_config_actor.entity:
                trace_config_trigger.assert_property_match(ATTR_ENTITY, workflow_config_actor.entity)
            if workflow_config_actor.type:
                trace_config_trigger.assert_property_match(ATTR_TYPE, workflow_config_actor.type)
            if workflow_config_actor.action:
                trace_config_trigger.assert_property_match(ATTR_ACTION, workflow_config_actor.action)
            if workflow_config_actor.data:
                trace_config_trigger.assert_property_match(ATTR_DATA, workflow_config_actor.data)
            if workflow_config_actor.condition:
                trace_config_actor_condition = trace_config_actor.assert_property_not_none(ATTR_CONDITION)
                trace_config_actor_condition.assert_property_match(ATTR_TEMPLATE, workflow_config_actor.condition)

        # Test for reactor configuration in trace data
        for i in range(0, len(self.workflow_config.reactors)):
            workflow_config_reactor = self.workflow_config.reactors[i]
            trace_config_reactor = trace_config.assert_property_list_item(ATTR_REACTOR, i)
            trace_config_reactor.assert_property_match(ATTR_INDEX, i)
            if workflow_config_reactor.wait:
                if workflow_config_reactor.wait.delay:
                    trace_config_reactor_delay = trace_config_reactor.assert_property_not_none(ATTR_DELAY)
                    if workflow_config_reactor.wait.delay.seconds:
                        trace_config_reactor_delay.assert_property_match(ATTR_DELAY_SECONDS,  workflow_config_reactor.wait.delay.seconds)
                    if workflow_config_reactor.wait.delay.minutes:
                        trace_config_reactor_delay.assert_property_match(ATTR_DELAY_MINUTES, workflow_config_reactor.wait.delay.minutes)
                    if workflow_config_reactor.wait.delay.hours:
                        trace_config_reactor_delay.assert_property_match(ATTR_DELAY_HOURS, workflow_config_reactor.wait.delay.hours)
                if workflow_config_reactor.wait.schedule:
                    trace_config_reactor_schedule = trace_config_reactor.assert_property_not_none(ATTR_SCHEDULE)
                    trace_config_reactor_schedule.assert_property_match(ATTR_SCHEDULE_AT, workflow_config_reactor.wait.schedule.at)
                    trace_config_reactor_schedule.assert_property_match(ATTR_SCHEDULE_WEEKDAYS, workflow_config_reactor.wait.schedule.weekdays)
                if workflow_config_reactor.wait.state:
                    trace_config_reactor_state = trace_config_reactor.assert_property_not_none(ATTR_STATE)
                    trace_config_reactor_state.assert_property_match(ATTR_WAIT_CONDITION, workflow_config_reactor.wait.state.condition)
            if workflow_config_reactor.reset_workflow:
                trace_config_reactor_reset = trace_config_reactor.assert_property_not_none(MONIKER_RESET)
                trace_config_reactor_reset.assert_property_match(ATTR_ID, workflow_config_reactor.id)
                trace_config_reactor_reset.assert_property_match(ATTR_ENABLED, True)
                trace_config_reactor_reset.assert_property_match(ATTR_RESET_WORKFLOW, workflow_config_reactor.reset_workflow)
            else:
                trace_config_reactor_event = trace_config_reactor.assert_property_not_none(MONIKER_DISPATCH)
                trace_config_reactor_event.assert_property_match(ATTR_ID, workflow_config_reactor.id)
                trace_config_reactor_event.assert_property_match(ATTR_ENABLED, True)
                trace_config_reactor_event.assert_property_match(ATTR_DATA, workflow_config_reactor.data)
                trace_config_reactor_event.assert_property_match(ATTR_ENTITY, workflow_config_reactor.entity)
                trace_config_reactor_event.assert_property_match(ATTR_TYPE, workflow_config_reactor.type)
                if not workflow_config_reactor.forward_action:
                    trace_config_reactor_event.assert_property_match(ATTR_ACTION, workflow_config_reactor.action)

        ########## Trace data ##########

        # Test for actor data and vars in trace data
        trace_trace = trace.assert_property_not_none(TRACE_TRACE)
        workflow_config_actor = self.workflow_config.actors[actor_index]

        trace_trace_actor_path = f"{ATTR_ACTOR}/{actor_index}/{ATTR_TRIGGER}"
        trace_trace_actor = trace_trace.assert_property_list_item(trace_trace_actor_path)
        trace_trace_actor.assert_property_match(TRACE_PATH, trace_trace_actor_path)

        trace_trace_actor_vars = trace_trace_actor.assert_property_not_none(TRACE_CHANGED_VARIABLES)
        
        trace_trace_actor_vars_this = trace_trace_actor_vars.assert_property_not_none(ATTR_THIS)
        trace_trace_actor_vars_this.assert_property_match(ATTR_ENTITY_ID, key)
        trace_trace_actor_vars_this.assert_property_match(ATTR_STATE, STATE_ON)

        # Test for actor variables in trace data
        trace_trace_actor_vars_variables = trace_trace_actor_vars.assert_property_not_none(ATTR_VARIABLES)
        trace_trace_actor_vars_variables_actor = trace_trace_actor_vars_variables.assert_property_not_none(ATTR_ACTOR)
        trace_trace_actor_vars_variables_actor.assert_property_match(ATTR_ID, workflow_config_actor.id)
        trace_trace_actor_vars_variables_event = trace_trace_actor_vars_variables.assert_property_not_none(ATTR_EVENT)
        if workflow_config_actor.entity:
            trace_trace_actor_vars_variables_event.assert_property_match(ATTR_ENTITY, expected_runtime_actor_entity or workflow_config_actor.entity[actor_entity_index])
        if workflow_config_actor.type:
            trace_trace_actor_vars_variables_event.assert_property_match(ATTR_TYPE, expected_runtime_actor_type or workflow_config_actor.type[actor_type_index])
        if workflow_config_actor.action:
            trace_trace_actor_vars_variables_event.assert_property_match(ATTR_ACTION, expected_runtime_actor_action or workflow_config_actor.action[actor_action_index])
        if workflow_config_actor.data:
            trace_trace_actor_vars_variables_event.assert_property_match(ATTR_DATA, expected_runtime_actor_data or workflow_config_actor.data[actor_data_index])

        trace_trace_actor_vars_actor = trace_trace_actor_vars.assert_property_not_none(ATTR_ACTOR)
        trace_trace_actor_vars_actor.assert_property_match(ATTR_ID, workflow_config_actor.id)

        # Test for actor condition in trace data
        if workflow_config_actor.condition:
            trace_trace_actor_condition_path = f"{TRACE_PATH_ACTOR}/{actor_index}/{ATTR_CONDITION}"
            trace_trace_actor_condition = trace_trace.assert_property_list_item(trace_trace_actor_condition_path)
            trace_trace_actor_condition.assert_property_match(TRACE_PATH, trace_trace_actor_condition_path)
            trace_trace_actor_condition_result = trace_trace_actor_condition.assert_property_not_none(TRACE_RESULT)
            trace_trace_actor_condition_result.assert_property_match(TRACE_RESULT, expected_actor_condition_result)
        
        # Skip reaction traces if actor condition was false
        if not expected_actor_condition_result: return

        # Test for parallel in trace data if multiple reactors configured
        multiple_reactors = len(self.workflow_config.reactors) > 1

        if multiple_reactors:
            trace_trace_parallel_path = TRACE_PARALLEL
            trace_trace_parallel = trace_trace.assert_property_list_item(trace_trace_parallel_path)
            trace_trace_parallel.assert_property_match(TRACE_PATH, trace_trace_parallel_path)
            trace_trace_parallel_variables = trace_trace_parallel.assert_property_not_none(TRACE_CHANGED_VARIABLES)
            trace_trace_parallel_variables.assert_property_not_none(TRACE_CONTEXT)

        # Test for reactor data in trace data
        for i in range(0, len(self.workflow_config.reactors)):
            workflow_config_reactor = self.workflow_config.reactors[i]

            if workflow_config_reactor.condition:
                # Test for reactor condition in trace data
                trace_trace_reactor_condition_path = f"{TRACE_PATH_REACTOR}/{i}/{TRACE_PATH_CONDITION}"
                trace_trace_reactor_condition = trace_trace.assert_property_list_item(trace_trace_reactor_condition_path)
                trace_trace_reactor_condition.assert_property_match(TRACE_PATH, trace_trace_reactor_condition_path)
                trace_trace_reactor_condition_result = trace_trace_reactor_condition.assert_property_not_none(TRACE_RESULT)
                trace_trace_reactor_condition_result.assert_property_match(TRACE_RESULT, expected_reactor_condition_results[i])
                
                # if there's one reactor with a condition the condition contains changed variables, test it
                if not multiple_reactors:
                    trace_trace_reactor_condition_variables = trace_trace_reactor_condition.assert_property_not_none(TRACE_CHANGED_VARIABLES)
                    trace_trace_reactor_condition_variables.assert_property_not_none(TRACE_CONTEXT)
            
            # If the reactor condition is false skip remaining reactor trace tests for this reactor as there is no trace data for it
            if not expected_reactor_condition_results[i]: continue

            if workflow_config_reactor.wait:
                if workflow_config_reactor.wait.state:
                    trace_trace_reactor_state_path = f"{TRACE_PATH_REACTOR}/{i}/{TRACE_PATH_STATE}"
                    trace_trace_reactor_state = trace_trace.assert_property_list_item(trace_trace_reactor_state_path)
                    trace_trace_reactor_state.assert_property_match(TRACE_PATH, trace_trace_reactor_state_path)
                    trace_trace_reactor_state_variables = trace_trace_reactor_state.assert_property_not_none(TRACE_CHANGED_VARIABLES)
                    trace_trace_reactor_state_variables.assert_property_not_none(TRACE_CONTEXT)

                # If the reactor is delayed check for delay trace data
                if workflow_config_reactor.wait.delay:
                    trace_trace_reactor_delay_path = f"{TRACE_PATH_REACTOR}/{i}/{TRACE_PATH_DELAY}"
                    trace_trace_reactor_delay = trace_trace.assert_property_list_item(trace_trace_reactor_delay_path)
                    trace_trace_reactor_delay.assert_property_match(TRACE_PATH, trace_trace_reactor_delay_path)
                    trace_trace_reactor_delay_result = trace_trace_reactor_delay.assert_property_not_none(TRACE_RESULT)
                    trace_trace_reactor_delay_result_wait = trace_trace_reactor_delay_result.assert_property_not_none(ATTR_WAIT)
                    trace_trace_reactor_delay_result_wait_delay = trace_trace_reactor_delay_result_wait.assert_property_not_none(ATTR_DELAY)
                    if expected_runtime_reactor_delay_seconds or workflow_config_reactor.wait.delay.seconds:
                        trace_trace_reactor_delay_result_wait_delay.assert_property_match(ATTR_DELAY_SECONDS, expected_runtime_reactor_delay_seconds or workflow_config_reactor.wait.delay.seconds)
                    if expected_runtime_reactor_delay_minutes or workflow_config_reactor.wait.delay.minutes:
                        trace_trace_reactor_delay_result_wait_delay.assert_property_match(ATTR_DELAY_MINUTES, expected_runtime_reactor_delay_minutes or workflow_config_reactor.wait.delay.minutes)
                    if expected_runtime_reactor_delay_hours or workflow_config_reactor.wait.delay.hours:
                        trace_trace_reactor_delay_result_wait_delay.assert_property_match(ATTR_DELAY_HOURS, expected_runtime_reactor_delay_hours or workflow_config_reactor.wait.delay.hours)
                    if not workflow_config_reactor.wait.state:
                        trace_trace_reactor_delay_variables = trace_trace_reactor_delay.assert_property_not_none(TRACE_CHANGED_VARIABLES)
                        trace_trace_reactor_delay_variables.assert_property_not_none(TRACE_CONTEXT)

                # If the reactor is scheduled check for schedule trace data
                if workflow_config_reactor.wait.schedule:
                    trace_trace_reactor_schedule_path = f"{TRACE_PATH_REACTOR}/{i}/{TRACE_PATH_SCHEDULE}"
                    trace_trace_reactor_schedule = trace_trace.assert_property_list_item(trace_trace_reactor_schedule_path)
                    trace_trace_reactor_schedule.assert_property_match(TRACE_PATH, trace_trace_reactor_schedule_path)
                    trace_trace_reactor_schedule_result = trace_trace_reactor_schedule.assert_property_not_none(TRACE_RESULT)
                    trace_trace_reactor_schedule_result.assert_property_not_none(ATTR_WAIT)
                    if not workflow_config_reactor.wait.state:
                        trace_trace_reactor_schedule_variables = trace_trace_reactor_schedule.assert_property_not_none(TRACE_CHANGED_VARIABLES)
                        trace_trace_reactor_schedule_variables.assert_property_not_none(TRACE_CONTEXT)

            if workflow_config_reactor.reset_workflow:
                trace_trace_reactor_reset_path = f"{TRACE_PATH_REACTOR}/{i}/{TRACE_PATH_RESET}"
                trace_trace_reactor_reset = trace_trace.assert_property_list_item(trace_trace_reactor_reset_path)
                trace_trace_reactor_reset.assert_property_match(TRACE_PATH, trace_trace_reactor_reset_path)
                trace_trace_reactor_reset_result = trace_trace_reactor_reset.assert_property_not_none(TRACE_RESULT)
                # trace_trace_reactor_reset.assert_property_match(ATTR_REACTOR_ID, workflow_config_reactor.id)
                trace_trace_reactor_reset_result.assert_property_not_none(ATTR_RESET_WORKFLOW, workflow_config_reactor.reset_workflow)
            else:
                if not expected_event_trace: continue

                trace_trace_reactor_event_path = f"{TRACE_PATH_REACTOR}/{i}/{TRACE_PATH_DISPATCH}"
                trace_trace_reactor_event = trace_trace.assert_property_list_item(trace_trace_reactor_event_path)
                trace_trace_reactor_event.assert_property_match(TRACE_PATH, trace_trace_reactor_event_path)

                trace_trace_reactor_event_result = trace_trace_reactor_event.assert_property_not_none(TRACE_RESULT)
                
                if expected_result_message:
                    # Test for message result in trace data
                    trace_trace_reactor_event_result.assert_property_match(TRACE_MESSAGE, expected_result_message)
                else:
                    # test for reaction result in trace data
                    trace_trace_reactor_event_result_reaction = trace_trace_reactor_event_result.assert_property_not_none(TRACE_REACTION)
                    trace_trace_reactor_event_result_reaction.assert_property_match(ATTR_REACTOR_ID, workflow_config_reactor.id)
                    trace_trace_reactor_event_result_reaction.assert_property_match(ATTR_ENTITY, expected_runtime_reactor_entity[i] or workflow_config_reactor.entity[0])
                    trace_trace_reactor_event_result_reaction.assert_property_match(ATTR_TYPE, expected_runtime_reactor_type[i] or workflow_config_reactor.type[0])
                    trace_trace_reactor_event_result_reaction.assert_property_match(ATTR_ACTION, expected_runtime_reactor_action[i] or (expected_runtime_actor_action if workflow_config_reactor.forward_action else workflow_config_reactor.action[0]))
                    trace_trace_reactor_event_result_reaction.assert_property_match(ATTR_DATA, expected_runtime_reactor_data[i] or (workflow_config_reactor.data[0] if workflow_config_reactor.data else None))

                # Test for variables in event section of trace data if only 1 reactor configured without condition and delay
                if (len(self.workflow_config.reactors) == 1 and 
                    not workflow_config_reactor.condition and 
                    not workflow_config_reactor.wait):
                    trace_trace_reactor_event_variables = trace_trace_reactor_event.assert_property_not_none(TRACE_CHANGED_VARIABLES)
                    trace_trace_reactor_event_variables.assert_property_not_none(TRACE_CONTEXT)
            

    async def async_send_notify_feedback_event(self, send_workflow: Workflow, send_reactor_index: int = 0, send_reactor_data_index: int = 0, send_feedback_item_index: int = 0):
        send_workflow_config_reactor = send_workflow.reactors[send_reactor_index]

        send_workflow_config_reactor_data = send_workflow_config_reactor.data[send_reactor_data_index].as_dict()
        send_feedback_items: list[dict] = send_workflow_config_reactor_data.get(ATTR_EVENT_FEEDBACK_ITEMS)
        send_feedback_item = send_feedback_items[send_feedback_item_index]

        event_data = {
            ATTR_ENTITY: send_workflow_config_reactor.entity[0],
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: send_feedback_item.get(ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK),
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: send_feedback_item.get(ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,)
        }
        self.hass.bus.async_fire(EVENT_TEST_CALLBACK, event_data)
        await self.hass.async_block_till_done()


    def register_plugin_data(self, plugin_data: dict):
        self.plugin_data_register.append(plugin_data)


    def verify_plugin_data_sent(self, expected_count: int = 1):
        got_count = len(self.plugin_data_register)
        assert got_count == expected_count, f"Expected plugin_data count {expected_count}, got {got_count}"


    def verify_plugin_data_not_sent(self):
        self.verify_plugin_data_sent(expected_count=0)


    def verify_plugin_data_content(self, expected_data: dict, data_index: int = 0):
        got_data = self.plugin_data_register[data_index]
        assert DeepDiff(got_data, expected_data) == {}, f"Expected plugin data '{expected_data}', got '{got_data}'"


    def register_service_call(self, domain: str, service_name: str, data: dict):
        self.service_call_register.append({
            ATTR_DOMAIN: domain,
            ATTR_SERVICE_NAME: service_name,
            ATTR_DATA: data
        })


    def verify_service_call_sent(self, expected_count: int = 1):
        got_count = len(self.service_call_register)
        assert got_count == expected_count, f"Expected service_call count {expected_count}, got {got_count}"


    def verify_service_call_not_sent(self):
        self.verify_service_call_sent(expected_count=0)


    def verify_service_call_content(self, domain: str, service_name: str, data: dict, data_index: int = 0):
        expected_data = {
            ATTR_DOMAIN: domain,
            ATTR_SERVICE_NAME: service_name,
            ATTR_DATA: data
        }
        got_data = self.service_call_register[data_index]
        assert DeepDiff(got_data, expected_data) == {}, f"Expected service_call '{expected_data}', got '{got_data}'"


    def register_plugin_task_unload(self, id: str):
        self.plugin_task_unloaded_register.append(id)


    def verify_plugin_task_unload_sent(self, expected_count: int = 1):
        got_count = len(self.plugin_task_unloaded_register)
        assert got_count == expected_count, f"Expected plugin_task_unload count {expected_count}, got {got_count}"

    
    def verify_state(self, entity_id: str, expected_state: Any, convert: Callable[[str], Any ] = lambda s: s):
        if state := self.hass.states.get(entity_id):
            assert convert(state.state) == expected_state, f"Expected '{entity_id}' state '{expected_state}', got '{state.state}'"
        else:
            assert False, f"State for entity '{entity_id}' not found"


    def assert_attribute(self, attr: str, expected: dict, got: dict):    
        value_expected = expected.get(attr, None)
        if isinstance(value_expected, MultiItem) and len(value_expected) == 1:
            value_expected = value_expected.first
        value_got = got.get(attr, None)
        assert value_got == value_expected, f"Expected notification value '{value_expected}', got '{value_got}'"


    async def async_arm_alarm(self, entity_id: str, code: str):
        await self.hass.services.async_call(
            ALARM_DOMAIN,
            SERVICE_ALARM_ARM_AWAY,
            {
                ATTR_ENTITY_ID: entity_id,
                ATTR_CODE: code,
            }
        )


class TracePath():
    def __init__(self, owner: dict, path: str, parent: str = None) -> None:
        self.owner = owner
        self.path = path
        self.parent = parent
    
    
    def assert_property_match(self, key: str, value_expected: Any, name: str = None):
        value_got = self.owner.get(key, None)
        if isinstance(value_got, DynamicData):
            value_got = value_got.as_dict()
        match = False
        used_value_expected = value_expected
        if isinstance(value_expected, str) and isinstance(value_got, MultiItem):
            match = used_value_expected == value_got.first and len(value_got) == 1
        elif isinstance(value_expected, MultiItem) and isinstance(value_got, str):
            used_value_expected = value_expected.first
            match = used_value_expected == value_got and len(value_expected) == 1
        elif isinstance(value_expected, list) and isinstance(value_got, dict):
            used_value_expected = value_expected[0]
            if isinstance(used_value_expected, DynamicData):
                used_value_expected = used_value_expected.as_dict()
            match = DeepDiff(used_value_expected, value_got) == {} and len(value_expected) == 1
        elif isinstance(value_expected, list) and isinstance(value_got, list):
            used_value_expected = [ x.as_dict() if isinstance(x, DynamicData) else x for x in value_expected ]
            match = DeepDiff(used_value_expected, value_got) == {}
        else:
            if isinstance(used_value_expected, DynamicData):
                used_value_expected = used_value_expected.as_dict()
            match = DeepDiff(used_value_expected, value_got) == {}
        assert match, self.assert_message_match(key, name, used_value_expected, value_got)

    
    def assert_property_not_none(self, key: str, name: str = None) -> TracePath:
        value_got = self._assert_property_not_none_bare(key, name)
        return self.child_path(value_got, key)


    def _assert_property_not_none_bare(self, key: str, name: str = None) -> Any:
        value_got = self.owner.get(key, None)
        assert value_got, self.assert_message_not_none(key, name)
        return value_got


    def assert_property_list_item(self, key: str, index: int = 0, name: str = None) -> TracePath:
        item_list: list = self._assert_property_not_none_bare(key, name)
        assert len(item_list) > index, self.assert_message_list_item(key, name, index+1, item_list)
        return self.child_path(item_list[index], f"{key}[{index}]")


    def child_path(self, owner: dict, child_path: str) -> TracePath:
        return TracePath(owner, child_path, self.path)
    

    @property
    def full_path(self):
        if self.parent:
            return f"{self.parent}.{self.path}"
        return self.path


    def full_property(self, key: str, name: str):
        return f"{self.full_path}.{name if name else key}"


    def assert_message_match(self, key: str, name: str, value_expected: Any, value_got: Any):
        return f"Expected {self.full_property(key, name)} '{value_expected}', got '{value_got}'"


    def assert_message_not_none(self, key: str, name: str):
        return f"Expected a value for {self.full_property(key, name)}, got none"

    
    def assert_message_list_item(self, key: str, name: str, count: int, item_list: list):
        f"Expected {count} items in list {self.full_property(key, name)}, got {len(item_list)}"


def assert_dict_property_value_not_none(owner: dict, key: str, name: str = None) -> Any:
    value_got = owner.get(key, None)
    assert value_got, f"Expected a value for {name if name else key}, got none"
    return value_got
