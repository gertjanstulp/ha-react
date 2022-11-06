from __future__ import annotations

import pytest
import yaml

from unittest.mock import Mock, patch
from yaml import SafeLoader

from homeassistant.components import template, input_boolean, input_text, group, binary_sensor, device_tracker, person
from homeassistant.components.trace import DATA_TRACE
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.react.const import (
    ATTR_NOTIFY,
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
    SERVICE_TRIGGER_REACTION,
    SERVICE_TRIGGER_WORKFLOW
)

from tests.common import (
    GROUP_CONFIG,
    INPUT_BOOLEAN_CONFIG,
    INPUT_TEXT_CONFIG,
    PERSON_CONFIG,
    REACT_CONFIG,
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
async def react_component(hass: HomeAssistant):
    hass.data[DATA_TRACE] = {}

    async def async_setup(workflow_name: str, additional_workflows: list[str] = [], init_notify_plugin: bool = False):
        data = None
        workflow_id = f"{WORKFLOW_ID_PREFIX}{workflow_name}"
        with open(get_test_config_dir(REACT_CONFIG)) as f:
            raw_data: dict = yaml.load(f, Loader=SafeLoader)
            data = {
                CONF_STENCIL: raw_data.get(CONF_STENCIL, {}),
                CONF_WORKFLOW: {
                    workflow_id : raw_data.get(CONF_WORKFLOW, {}).get(workflow_id, {}),
                }
            }

            if init_notify_plugin:
                data[CONF_PLUGINS] = [
                    "tests.plugins.test_notify_plugin"
                ]
                    
        for additional_workflow in additional_workflows:
            additional_workflow_ID = f"{WORKFLOW_ID_PREFIX}{additional_workflow}"
            data[CONF_WORKFLOW][additional_workflow_ID] = raw_data.get(CONF_WORKFLOW, {}).get(additional_workflow_ID, {})
        
        assert await async_setup_component(
            hass,
            REACT_DOMAIN,
            {REACT_DOMAIN: data}
        )

        await hass.async_block_till_done()
        test = 1

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

    result = Mock()
    result.async_setup = async_setup
    result.async_call_service_trigger_workflow = async_call_service_trigger_workflow
    result.async_call_service_delete_run = async_call_service_delete_run
    result.async_call_service_delete_reaction = async_call_service_delete_reaction
    result.async_call_service_run_now = async_call_service_run_now
    result.async_call_service_react_now = async_call_service_react_now
    return result


@pytest.fixture
async def template_component(hass: HomeAssistant):
    with open(get_test_config_dir(TEMPLATE_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, template.DOMAIN, { template.DOMAIN: data })
    await hass.async_block_till_done()


@pytest.fixture
async def input_boolean_component(hass: HomeAssistant):
    with open(get_test_config_dir(INPUT_BOOLEAN_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, input_boolean.DOMAIN, { input_boolean.DOMAIN: data })
    await hass.async_block_till_done()

    async def async_turn_on(name: str, ):
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
async def input_text_component(hass: HomeAssistant):
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
async def group_component(hass: HomeAssistant):
    with open(get_test_config_dir(GROUP_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, group.DOMAIN, { group.DOMAIN: data })
    await hass.async_block_till_done()

    
@pytest.fixture
async def binary_sensor_component(hass: HomeAssistant):
    assert await async_setup_component(hass, binary_sensor.DOMAIN, {})
    await hass.async_block_till_done()

    
@pytest.fixture
async def device_tracker_component(hass: HomeAssistant):
    assert await async_setup_component(hass, device_tracker.DOMAIN, {})
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
async def person_component(hass: HomeAssistant):
    with open(get_test_config_dir(PERSON_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(hass, person.DOMAIN, { person.DOMAIN: data })
    await hass.async_block_till_done()
