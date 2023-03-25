from __future__ import annotations
from typing import Any

import pytest
import yaml

from unittest.mock import Mock, patch
from yaml import SafeLoader

from homeassistant.components import template, input_boolean, input_button, input_number, input_text, light, notify, persistent_notification, switch, group, binary_sensor, sensor, device_tracker, person, alarm_control_panel
from homeassistant.components.input_number import SERVICE_SET_VALUE, ATTR_VALUE
from homeassistant.components.trace import DATA_TRACE
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON, SERVICE_RELOAD
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.virtual import SERVICE_AVAILABILE
from custom_components.virtual.binary_sensor import SERVICE_ON

from custom_components.virtual.const import (
    COMPONENT_DOMAIN as VIRTUAL_DOMAIN
)

from custom_components.react.const import (
    ATTR_REACTION_ID,
    ATTR_RUN_ID,
    CONF_PLUGINS,
    CONF_STENCIL,
    CONF_WORKFLOW,
    DOMAIN as REACT_DOMAIN,
    SERVICE_DELETE_REACTION,
    SERVICE_DELETE_RUN,
    SERVICE_REACT_NOW,
    SERVICE_RUN_NOW,
    SERVICE_TRIGGER_WORKFLOW
)
from custom_components.react.lib.config import Plugin
from custom_components.virtual.sensor import SERVICE_SET

from tests.common import (
    ALARM_CONFIG,
    BINARY_SENSOR_CONFIG,
    DEVICE_TRACKER_CONFIG,
    GROUP_CONFIG,
    INPUT_BOOLEAN_CONFIG,
    INPUT_BUTTON_CONFIG,
    INPUT_NUMBER_CONFIG,
    INPUT_TEXT_CONFIG,
    LIGHT_CONFIG,
    PERSON_CONFIG,
    REACT_CONFIG,
    SENSOR_CONFIG,
    SWITCH_CONFIG,
    TEMPLATE_CONFIG, 
    get_test_config_dir
)

WORKFLOW_ID_PREFIX = "workflow_"

@pytest.fixture()
def patch_config_dir():
    with patch("pytest_homeassistant_custom_component.common.get_test_config_dir", get_test_config_dir):
        yield


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(patch_config_dir, enable_custom_integrations):
    yield


@pytest.fixture
def hass_setup(hass: HomeAssistant):
    hass.data[DATA_TRACE] = {}
    hass.config.set_time_zone("Europe/Amsterdam")
    hass.config.units = METRIC_SYSTEM
    result = Mock()
    result.hass = hass
    return result


@pytest.fixture
async def virtual_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass

    assert await async_setup_component(hass, VIRTUAL_DOMAIN, { VIRTUAL_DOMAIN: {}} )
    await hass.async_block_till_done()

    async def async_turn_on(domain: str, name: str):
        await hass.services.async_call(
            VIRTUAL_DOMAIN,
            SERVICE_ON,
            {
                ATTR_ENTITY_ID: f"{domain}.{name}"
            }
        )
        await hass.async_block_till_done()

    async def async_set(domain: str, name: str, value: Any):
        await hass.services.async_call(
            VIRTUAL_DOMAIN,
            SERVICE_SET,
            {
                ATTR_ENTITY_ID: f"{domain}.{name}",
                ATTR_VALUE: value
            }
        )
        await hass.async_block_till_done()

    async def async_set_available(domain: str, name: str):
        await hass.services.async_call(
            VIRTUAL_DOMAIN,
            SERVICE_AVAILABILE,
            {
                ATTR_ENTITY_ID: f"{domain}.{name}",
                ATTR_VALUE: True
            }
        )
        await hass.async_block_till_done()

    async def async_set_unavailable(domain: str, name: str):
        await hass.services.async_call(
            VIRTUAL_DOMAIN,
            SERVICE_AVAILABILE,
            {
                ATTR_ENTITY_ID: f"{domain}.{name}",
                ATTR_VALUE: False
            }
        )
        await hass.async_block_till_done()
 

    result = Mock()
    result.async_turn_on = async_turn_on
    result.async_set = async_set
    result.async_set_available = async_set_available
    result.async_set_unavailable = async_set_unavailable
    return result


@pytest.fixture
async def notify_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass

    assert await async_setup_component(hass, notify.DOMAIN, { notify.DOMAIN: {}} )
    await hass.async_block_till_done()


@pytest.fixture
async def react_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass

    async def async_setup(workflow_name: str = None, additional_workflows: list[str] = [], plugins: list[dict] = [], process_workflow: callable(dict) = None):
        with open(get_test_config_dir(REACT_CONFIG)) as f:
            raw_data: dict = yaml.load(f, Loader=SafeLoader)

        data = {
            CONF_STENCIL: raw_data.get(CONF_STENCIL, {}),
            CONF_WORKFLOW: {},
            CONF_PLUGINS: plugins
        }

        if workflow_name:
            workflow_id = f"{WORKFLOW_ID_PREFIX}{workflow_name}"
            workflow_raw = raw_data.get(CONF_WORKFLOW, {}).get(workflow_id, {})
            if process_workflow:
                process_workflow(workflow_raw)
            data[CONF_WORKFLOW][workflow_id] = workflow_raw
          
        for additional_workflow in additional_workflows:
            additional_workflow_ID = f"{WORKFLOW_ID_PREFIX}{additional_workflow}"
            data[CONF_WORKFLOW][additional_workflow_ID] = raw_data.get(CONF_WORKFLOW, {}).get(additional_workflow_ID, {})
        
        assert await async_setup_component(
            hass,
            REACT_DOMAIN,
            {REACT_DOMAIN: data}
        )

        await hass.async_block_till_done()


    async def async_call_service_trigger_workflow(entity_id: str):
        data = { ATTR_ENTITY_ID: entity_id }
        await hass.services.async_call(REACT_DOMAIN, SERVICE_TRIGGER_WORKFLOW, data)


    async def async_call_service_delete_run(run_id: str):
        data = { ATTR_RUN_ID: run_id }
        await hass.services.async_call(REACT_DOMAIN, SERVICE_DELETE_RUN, data)


    async def async_call_service_delete_reaction(reaction_id: str):
        data = { ATTR_REACTION_ID: reaction_id }
        await hass.services.async_call(REACT_DOMAIN, SERVICE_DELETE_REACTION, data)


    async def async_call_service_run_now(run_id: str):
        data = { ATTR_RUN_ID: run_id }
        await hass.services.async_call(REACT_DOMAIN, SERVICE_RUN_NOW, data)


    async def async_call_service_react_now(reaction_id: str):
        data = { ATTR_REACTION_ID: reaction_id }
        await hass.services.async_call(REACT_DOMAIN, SERVICE_REACT_NOW, data)


    async def async_call_service_reload():
        await hass.services.async_call(REACT_DOMAIN, SERVICE_RELOAD)


    result = Mock()
    result.async_setup = async_setup
    result.async_call_service_trigger_workflow = async_call_service_trigger_workflow
    result.async_call_service_delete_run = async_call_service_delete_run
    result.async_call_service_delete_reaction = async_call_service_delete_reaction
    result.async_call_service_run_now = async_call_service_run_now
    result.async_call_service_react_now = async_call_service_react_now
    result.async_call_service_reload = async_call_service_reload
    # result.async
    return result


@pytest.fixture
async def template_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(TEMPLATE_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, template.DOMAIN, { template.DOMAIN: data })
    await hass.async_block_till_done()


@pytest.fixture
async def input_boolean_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(INPUT_BOOLEAN_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, input_boolean.DOMAIN, { input_boolean.DOMAIN: data })
    await hass.async_block_till_done()

    async def async_turn_on(name: str):
        await hass.services.async_call(
            input_boolean.DOMAIN,
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: f"input_boolean.{name}"
            }
        )
        await hass.async_block_till_done()

    async def async_turn_off(name: str):
        await hass.services.async_call(
            input_boolean.DOMAIN,
            SERVICE_TURN_OFF,
            {
                ATTR_ENTITY_ID: f"input_boolean.{name}"
            }
        )
        await hass.async_block_till_done()

    result = Mock()
    result.async_turn_on = async_turn_on
    result.async_turn_off = async_turn_off
    return result


@pytest.fixture
async def input_button_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(INPUT_BUTTON_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, input_button.DOMAIN, { input_button.DOMAIN: data })
    await hass.async_block_till_done()

    async def async_press(name: str):
        await hass.services.async_call(
            input_button.DOMAIN,
            input_button.SERVICE_PRESS,
            {
                ATTR_ENTITY_ID: f"input_button.{name}"
            }
        )
        await hass.async_block_till_done()

    result = Mock()
    result.async_press = async_press
    return result


@pytest.fixture
async def input_number_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(INPUT_NUMBER_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, input_number.DOMAIN, { input_number.DOMAIN: data })
    await hass.async_block_till_done()

    async def async_set_value(name: str, value: float):
        await hass.services.async_call(
            input_number.DOMAIN,
            SERVICE_SET_VALUE,
            {
                ATTR_ENTITY_ID: f"input_number.{name}",
                ATTR_VALUE: value
            }
        )
        await hass.async_block_till_done()

    result = Mock()
    result.async_set_value = async_set_value
    return result


@pytest.fixture
async def input_text_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(INPUT_TEXT_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, input_text.DOMAIN, { input_text.DOMAIN: data })
    await hass.async_block_till_done()

    async def async_set_value(name: str, value: str):
        await hass.services.async_call(
            input_text.DOMAIN,
            input_text.SERVICE_SET_VALUE,
            {
                ATTR_ENTITY_ID: f"input_text.{name}",
                input_text.ATTR_VALUE: value,
            }
        )
        await hass.async_block_till_done()

    result = Mock()
    result.async_set_value = async_set_value
    return result


@pytest.fixture
async def group_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(GROUP_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, group.DOMAIN, { group.DOMAIN: data })
    await hass.async_block_till_done()

    
@pytest.fixture
async def binary_sensor_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(BINARY_SENSOR_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, binary_sensor.DOMAIN, { binary_sensor.DOMAIN: data })
    await hass.async_block_till_done()

    
@pytest.fixture
async def sensor_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(SENSOR_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, sensor.DOMAIN, { sensor.DOMAIN: data })
    await hass.async_block_till_done()

    
@pytest.fixture
async def device_tracker_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(DEVICE_TRACKER_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, device_tracker.DOMAIN, { device_tracker.DOMAIN: data })
    await hass.async_block_till_done()
    
    async def async_see(dev_id: str, location: str):
        await hass.services.async_call(
            device_tracker.DOMAIN,
            device_tracker.SERVICE_SEE,
            {
                device_tracker.ATTR_DEV_ID: dev_id,
                device_tracker.ATTR_LOCATION_NAME: location,
                device_tracker.ATTR_SOURCE_TYPE: device_tracker.SOURCE_TYPE_ROUTER
            }
        )
        await hass.async_block_till_done()

    result = Mock()
    result.async_see = async_see
    return result


@pytest.fixture
async def person_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(PERSON_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, person.DOMAIN, { person.DOMAIN: data })
    await hass.async_block_till_done()


@pytest.fixture
async def light_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(LIGHT_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, light.DOMAIN, { light.DOMAIN: data })
    await hass.async_block_till_done()

    async def async_turn_on(name: str):
        await hass.services.async_call(
            light.DOMAIN,
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: f"light.{name}"
            }
        )
        await hass.async_block_till_done()

    async def async_turn_off(name: str):
        await hass.services.async_call(
            light.DOMAIN,
            SERVICE_TURN_OFF,
            {
                ATTR_ENTITY_ID: f"light.{name}"
            }
        )
        await hass.async_block_till_done()

    result = Mock()
    result.async_turn_on = async_turn_on
    result.async_turn_off = async_turn_off
    return result


@pytest.fixture
async def switch_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(SWITCH_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, switch.DOMAIN, { switch.DOMAIN: data })
    await hass.async_block_till_done()

    async def async_turn_on(name: str):
        await hass.services.async_call(
            switch.DOMAIN,
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: f"switch.{name}"
            }
        )
        await hass.async_block_till_done()

    async def async_turn_off(name: str):
        await hass.services.async_call(
            switch.DOMAIN,
            SERVICE_TURN_OFF,
            {
                ATTR_ENTITY_ID: f"switch.{name}"
            }
        )
        await hass.async_block_till_done()

    result = Mock()
    result.async_turn_on = async_turn_on
    result.async_turn_off = async_turn_off
    return result


@pytest.fixture
async def alarm_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass
    with open(get_test_config_dir(ALARM_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, alarm_control_panel.DOMAIN, { alarm_control_panel.DOMAIN: data })
    await hass.async_block_till_done()

    async def async_arm_away(name: str):
        await hass.services.async_call(
            alarm_control_panel.DOMAIN,
            alarm_control_panel.SERVICE_ALARM_ARM_AWAY,
            {
                ATTR_ENTITY_ID: f"alarm_control_panel.{name}",
                alarm_control_panel.ATTR_CODE: '1234',
            }
        )
        await hass.async_block_till_done()

    result = Mock()
    result.async_arm_away = async_arm_away
    return result
