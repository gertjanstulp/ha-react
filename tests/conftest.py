from __future__ import annotations
from typing import Generator

import pytest
# import pytest_asyncio

import yaml
from unittest.mock import Mock, patch
from yaml import SafeLoader

from homeassistant.components.trace import DATA_TRACE
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_RELOAD
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util.unit_system import METRIC_SYSTEM


from custom_components.react.const import (
    ATTR_REACTION_ID,
    ATTR_RUN_ID,
    CONF_ENTITY_GROUPS,
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
from tests._plugins.common import HassApiMock

from tests.common import (
    REACT_CONFIG,
    get_test_config_dir
)
from tests.tst_context import TstContext

WORKFLOW_ID_PREFIX = "workflow_"




@pytest.fixture()
def patch_config_dir():
    with patch("pytest_homeassistant_custom_component.common.get_test_config_dir", get_test_config_dir):
        yield


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(patch_config_dir, enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def verify_cleanup() -> Generator[None, None, None]:
    # Homeassistant conftest.py contains a verify_cleanup fixture that fails our tests,
    # so we define our own one that does nothing to override Homeassistant
    yield


@pytest.fixture
async def hass_setup(hass: HomeAssistant, hass_api_mock):
    hass.data[DATA_TRACE] = {}
    hass.data[HASS_API_MOCK] = HassApiMock(hass)
    await hass.config.async_set_time_zone("Europe/Amsterdam")
    hass.config.units = METRIC_SYSTEM
    result = Mock()
    result.hass = hass
    return result


HASS_API_MOCK = "hass_api_mock"
def set_hass_api(self, hass: HomeAssistant):
    self.hass_api = hass.data[HASS_API_MOCK]


@pytest.fixture
def hass_api_mock(hass: HomeAssistant):
    with patch("custom_components.react.plugin.factory.PluginFactory.set_hass_api", set_hass_api):
        yield


@pytest.fixture
async def react_component(hass_setup):
    hass: HomeAssistant = hass_setup.hass

    async def async_setup(workflow_name: str = None, additional_workflows: list[str] = [], plugins: list[dict] = [], process_workflow: callable(dict) = None):
        with open(get_test_config_dir(REACT_CONFIG)) as f:
            raw_data: dict = yaml.load(f, Loader=SafeLoader)

        data = {
            CONF_STENCIL: raw_data.get(CONF_STENCIL, {}),
            CONF_ENTITY_GROUPS: raw_data.get(CONF_ENTITY_GROUPS, {}),
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

    return result


@pytest.fixture
def test_context(hass: HomeAssistant, react_component, workflow_name: str) -> TstContext:
    return TstContext(hass, react_component, workflow_name)
