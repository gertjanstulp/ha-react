from __future__ import annotations

import asyncio
import logging
from re import L
import threading
import pytest
import yaml
import pytest_socket

from unittest.mock import Mock, patch
from yaml import SafeLoader

from homeassistant import runner, loader
from homeassistant.components import template, input_boolean, input_text, group, binary_sensor, device_tracker, person
from homeassistant.components.network.models import Adapter, IPv4ConfiguredAddress
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util, location

from tests.ignore_uncaught_exceptions import IGNORE_UNCAUGHT_EXCEPTIONS

pytest.register_assert_rewrite("tests.common")

from tests.common import (
    INSTANCES,
    async_test_home_assistant,
    get_test_config_dir,
    mock_storage,
)

from custom_components.react.const import (
    ATTR_NOTIFY,
    CONF_PLUGIN,
    CONF_STENCIL,
    CONF_WORKFLOW,
    DOMAIN as REACT_DOMAIN
)

REACT_CONFIG = "react.yaml"
TEMPLATE_CONFIG = "template.yaml"
INPUT_BOOLEAN_CONFIG = "input_boolean.yaml"
INPUT_TEXT_CONFIG = "input_text.yaml"
GROUP_CONFIG = "group.yaml"
PERSON_CONFIG = "person.yaml"

# Set default logger
logging.basicConfig(level=logging.DEBUG)

asyncio.set_event_loop_policy(runner.HassEventLoopPolicy(False))
# Disable fixtures overriding our beautiful policy
asyncio.set_event_loop_policy = lambda policy: None


def pytest_configure(config):
    """Register marker for tests that log exceptions."""
    config.addinivalue_line(
        "markers", "no_fail_on_log_exception: mark test to not fail on logged exception"
    )


def pytest_runtest_setup():
    pytest_socket.socket_allow_hosts(["127.0.0.1"])
    pytest_socket.disable_socket(allow_unix_socket=True)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield

# @pytest.fixture(autouse=True)
# def enable_custom_integrations(hass):
#     """Enable custom integrations defined in the test dir."""
#     hass.data.pop(loader.DATA_CUSTOM_COMPONENTS)


@pytest.fixture(autouse=True)
def verify_cleanup():
    """Verify that the test has cleaned up resources correctly."""
    threads_before = frozenset(threading.enumerate())

    yield

    if len(INSTANCES) >= 2:
        count = len(INSTANCES)
        for inst in INSTANCES:
            inst.stop()
        pytest.exit(f"Detected non stopped instances ({count}), aborting test run")

    threads = frozenset(threading.enumerate()) - threads_before
    for thread in threads:
        assert isinstance(thread, threading._DummyThread)


@pytest.fixture
def hass_storage():
    """Fixture to mock storage."""
    with mock_storage() as stored_data:
        yield stored_data


@pytest.fixture
def load_registries():
    """Fixture to control the loading of registries when setting up the hass fixture.

    To avoid loading the registries, tests can be marked with:
    @pytest.mark.parametrize("load_registries", [False])
    """
    return True


@pytest.fixture
def hass(loop, load_registries, hass_storage, request):
    """Fixture to provide a test instance of Home Assistant."""

    orig_tz = dt_util.DEFAULT_TIME_ZONE

    def exc_handle(loop, context):
        """Handle exceptions by rethrowing them, which will fail the test."""
        # Most of these contexts will contain an exception, but not all.
        # The docs note the key as "optional"
        # See https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.call_exception_handler
        if "exception" in context:
            exceptions.append(context["exception"])
        else:
            exceptions.append(
                Exception(
                    "Received exception handler without exception, but with message: %s"
                    % context["message"]
                )
            )
        orig_exception_handler(loop, context)

    exceptions = []
    hass = loop.run_until_complete(async_test_home_assistant(loop, load_registries))
    orig_exception_handler = loop.get_exception_handler()
    loop.set_exception_handler(exc_handle)

    yield hass

    loop.run_until_complete(hass.async_stop(force=True))

    # Restore timezone, it is set when creating the hass object
    dt_util.DEFAULT_TIME_ZONE = orig_tz

    for ex in exceptions:
        if (
            request.module.__name__,
            request.function.__name__,
        ) in IGNORE_UNCAUGHT_EXCEPTIONS:
            continue
        raise ex


@pytest.fixture(autouse=True)
def fail_on_log_exception(request, monkeypatch):
    """Fixture to fail if a callback wrapped by catch_log_exception or coroutine wrapped by async_create_catching_coro throws."""
    if "no_fail_on_log_exception" in request.keywords:
        return

    def log_exception(format_err, *args):
        raise

    monkeypatch.setattr("homeassistant.util.logging.log_exception", log_exception)


@pytest.fixture(autouse=True)
def mock_network():
    """Mock network."""
    mock_adapter = Adapter(
        name="eth0",
        index=0,
        enabled=True,
        auto=True,
        default=True,
        ipv4=[IPv4ConfiguredAddress(address="10.10.10.10", network_prefix=24)],
        ipv6=[],
    )
    with patch(
        "homeassistant.components.network.network.async_load_adapters",
        return_value=[mock_adapter],
    ):
        yield


@pytest.fixture(autouse=True)
def mock_get_source_ip():
    """Mock network util's async_get_source_ip."""
    with patch(
        "homeassistant.components.network.util.async_get_source_ip",
        return_value="10.10.10.10",
    ):
        yield
        

@pytest.fixture
async def react_component(hass):
    async def async_setup(test_name: str, additional_workflows: list[str] = [], init_notify_plugin: bool = False):
        data = None
        workflow_name = f"workflow_{test_name}"
        with open(get_test_config_dir(REACT_CONFIG)) as f:
            raw_data: dict = yaml.load(f, Loader=SafeLoader)
            data = {
                CONF_STENCIL: raw_data.get(CONF_STENCIL, {}),
                CONF_WORKFLOW: {
                    workflow_name : raw_data.get(CONF_WORKFLOW, {}).get(workflow_name, {}),
                }
            }

            if init_notify_plugin:
                data[CONF_PLUGIN] = {
                    ATTR_NOTIFY: "tests.plugins.test_notify_plugin"
                }
                    
        for workflow in additional_workflows:
            additional_workflow_name = workflow_name = f"workflow_{workflow}"
            data[CONF_WORKFLOW][additional_workflow_name] = raw_data.get(CONF_WORKFLOW, {}).get(workflow_name, {})
        
        assert await async_setup_component(
            hass,
            REACT_DOMAIN,
            {REACT_DOMAIN: data}
        )

        await hass.async_block_till_done()
        await hass.async_start()
        await hass.async_block_till_done()

    result = Mock()
    result.async_setup = async_setup
    return result


@pytest.fixture
async def template_component(hass: HomeAssistant):
    data = None
    with open(get_test_config_dir(TEMPLATE_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader)
    assert await async_setup_component(
        hass,
        template.DOMAIN,
        { template.DOMAIN: data },
    )
    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()


@pytest.fixture
async def input_boolean_component(hass: HomeAssistant):
    data = None
    with open(get_test_config_dir(INPUT_BOOLEAN_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader)
    assert await async_setup_component(
        hass,
        input_boolean.DOMAIN,
        { input_boolean.DOMAIN: data },
    )
    await hass.async_block_till_done()
    await hass.async_start()
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
async def input_text_component(hass: HomeAssistant):
    data = None
    with open(get_test_config_dir(INPUT_TEXT_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader)
    assert await async_setup_component(
        hass,
        input_text.DOMAIN,
        { input_text.DOMAIN: data },
    )
    await hass.async_block_till_done()
    await hass.async_start()
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
    data = None
    with open(get_test_config_dir(GROUP_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(
        hass,
        group.DOMAIN,
        { group.DOMAIN: data },
    )
    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()

    
@pytest.fixture
async def binary_sensor_component(hass: HomeAssistant):
    assert await async_setup_component(
        hass,
        binary_sensor.DOMAIN,
        {},
    )
    # assert await async_setup_platform
    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()

    
@pytest.fixture
async def device_tracker_component(hass: HomeAssistant):
    assert await async_setup_component(
        hass,
        device_tracker.DOMAIN,
        {},
    )
    # assert await async_setup_platform
    await hass.async_block_till_done()
    await hass.async_start()
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
    data = None
    with open(get_test_config_dir(PERSON_CONFIG)) as f:
        data = yaml.load(f, Loader=SafeLoader) or {}
    assert await async_setup_component(
        hass,
        person.DOMAIN,
        { person.DOMAIN: data },
    )
    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()

# @pytest.fixture
# def notify_plugin():
#     with patch(
#         "homeassistant.components.network.network.async_load_adapters",
#         return_value=[mock_adapter],
#     ):
#         yield