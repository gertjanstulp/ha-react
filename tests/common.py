from __future__ import annotations

import asyncio
import functools as ft
import json
import logging
import os
import types
import yaml
import custom_components.react as react

from contextlib import contextmanager
from time import monotonic
from typing import Any, Awaitable, Collection
from yaml.loader import SafeLoader

from unittest.mock import AsyncMock, Mock, patch

from homeassistant import auth, config_entries, core as ha, loader, bootstrap, runner
from homeassistant.auth import auth_store
from homeassistant.components.trace import DATA_TRACE
from homeassistant.config import async_process_component_config
from homeassistant.core import BLOCK_LOG_TIMEOUT
from homeassistant.helpers import area_registry, device_registry, entity_registry, storage
from homeassistant.setup import async_setup_component
from homeassistant.util.unit_system import METRIC_SYSTEM

from homeassistant.const import (
    EVENT_HOMEASSISTANT_CLOSE,
)

DOMAIN_SENSOR = "sensor"

INSTANCES = []
_LOGGER = logging.getLogger(__name__)


@ha.callback
def ensure_auth_manager_loaded(auth_mgr):
    """Ensure an auth manager is considered loaded."""
    store = auth_mgr._store
    if store._users is None:
        store._set_defaults()


def get_test_config_dir(*add_path):
    """Return a path to a test config dir."""
    return os.path.join(os.path.dirname(__file__), "testing_config", *add_path)


# pylint: disable=protected-access
async def async_test_home_assistant(loop, load_registries=True):
    """Return a Home Assistant object pointing at test config dir."""
    hass = ha.HomeAssistant()
    
    store = auth_store.AuthStore(hass)
    hass.auth = auth.AuthManager(hass, store, {}, {})
    ensure_auth_manager_loaded(hass.auth)
    INSTANCES.append(hass)

    orig_async_add_job = hass.async_add_job
    orig_async_add_executor_job = hass.async_add_executor_job
    orig_async_create_task = hass.async_create_task

    def async_add_job(target, *args):
        """Add job."""
        check_target = target
        while isinstance(check_target, ft.partial):
            check_target = check_target.func

        if isinstance(check_target, Mock) and not isinstance(target, AsyncMock):
            fut = asyncio.Future()
            fut.set_result(target(*args))
            return fut

        return orig_async_add_job(target, *args)

    def async_add_executor_job(target, *args):
        """Add executor job."""
        check_target = target
        while isinstance(check_target, ft.partial):
            check_target = check_target.func

        if isinstance(check_target, Mock):
            fut = asyncio.Future()
            fut.set_result(target(*args))
            return fut

        return orig_async_add_executor_job(target, *args)

    def async_create_task(coroutine):
        """Create task."""
        if isinstance(coroutine, Mock) and not isinstance(coroutine, AsyncMock):
            fut = asyncio.Future()
            fut.set_result(None)
            return fut

        return orig_async_create_task(coroutine)

    async def async_wait_for_task_count(self, max_remaining_tasks: int = 0) -> None:
        """Block until at most max_remaining_tasks remain.

        Based on HomeAssistant.async_block_till_done
        """
        # To flush out any call_soon_threadsafe
        await asyncio.sleep(0)
        start_time: float | None = None

        while len(self._pending_tasks) > max_remaining_tasks:
            pending: Collection[Awaitable[Any]] = [
                task for task in self._pending_tasks if not task.done()
            ]
            self._pending_tasks.clear()
            if len(pending) > max_remaining_tasks:
                remaining_pending = await self._await_count_and_log_pending(
                    pending, max_remaining_tasks=max_remaining_tasks
                )
                self._pending_tasks.extend(remaining_pending)

                if start_time is None:
                    # Avoid calling monotonic() until we know
                    # we may need to start logging blocked tasks.
                    start_time = 0
                elif start_time == 0:
                    # If we have waited twice then we set the start
                    # time
                    start_time = monotonic()
                elif monotonic() - start_time > BLOCK_LOG_TIMEOUT:
                    # We have waited at least three loops and new tasks
                    # continue to block. At this point we start
                    # logging all waiting tasks.
                    for task in pending:
                        _LOGGER.debug("Waiting for task: %s", task)
            else:
                self._pending_tasks.extend(pending)
                await asyncio.sleep(0)

    async def _await_count_and_log_pending(
        self, pending: Collection[Awaitable[Any]], max_remaining_tasks: int = 0
    ) -> Collection[Awaitable[Any]]:
        """Block at most max_remaining_tasks remain and log tasks that take a long time.

        Based on HomeAssistant._await_and_log_pending
        """
        wait_time = 0

        return_when = asyncio.ALL_COMPLETED
        if max_remaining_tasks:
            return_when = asyncio.FIRST_COMPLETED

        while len(pending) > max_remaining_tasks:
            _, pending = await asyncio.wait(
                pending, timeout=BLOCK_LOG_TIMEOUT, return_when=return_when
            )
            if not pending or max_remaining_tasks:
                return pending
            wait_time += BLOCK_LOG_TIMEOUT
            for task in pending:
                _LOGGER.debug("Waited %s seconds for task: %s", wait_time, task)

        return []

    hass.async_add_job = async_add_job
    hass.async_add_executor_job = async_add_executor_job
    hass.async_create_task = async_create_task
    hass.async_wait_for_task_count = types.MethodType(async_wait_for_task_count, hass)
    hass._await_count_and_log_pending = types.MethodType(
        _await_count_and_log_pending, hass
    )

    hass.data[loader.DATA_CUSTOM_COMPONENTS] = {}
    hass.data[DATA_TRACE] = {}

    hass.config.location_name = "test home"
    hass.config.config_dir = get_test_config_dir()
    hass.config.latitude = 52.3676
    hass.config.longitude = 4.9041
    hass.config.elevation = 0
    hass.config.set_time_zone("Europe/Amsterdam")
    hass.config.units = METRIC_SYSTEM
    hass.config.media_dirs = {"local": get_test_config_dir("media")}
    hass.config.skip_pip = True

    hass.config_entries = config_entries.ConfigEntries(
        hass,
        {
            "_": "Not empty or else some bad checks for hass config in discovery.py breaks"
        },
    )

    # Load the registries
    if load_registries:
        await asyncio.gather(
            device_registry.async_load(hass),
            entity_registry.async_load(hass),
            area_registry.async_load(hass),
        )
        await hass.async_block_till_done()

    hass.state = ha.CoreState.running

    # Mock async_start
    orig_start = hass.async_start

    async def mock_async_start():
        """Start the mocking."""
        # We only mock time during tests and we want to track tasks
        with patch.object(hass, "async_stop_track_tasks"):
            await orig_start()

    hass.async_start = mock_async_start

    @ha.callback
    def clear_instance(event):
        """Clear global instance."""
        INSTANCES.remove(hass)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_CLOSE, clear_instance)
    
    return hass


async def async_setup_react(hass):
    # Set up React
    react_data = None
    with open(get_test_config_dir("react.yaml")) as f:
        react_data = yaml.load(f, Loader=SafeLoader)

    assert await async_setup_component(
        hass,
        react.DOMAIN,
        {
            react.DOMAIN : react_data
        }
    )
    # await hass.async_block_till_done()


@contextmanager
def assert_setup_component(count, domain=None):
    """Collect valid configuration from setup_component.

    - count: The amount of valid platforms that should be setup
    - domain: The domain to count is optional. It can be automatically
              determined most of the time

    Use as a context manager around setup.setup_component
        with assert_setup_component(0) as result_config:
            setup_component(hass, domain, start_config)
            # using result_config is optional
    """
    config = {}

    async def mock_psc(hass, config_input, integration):
        """Mock the prepare_setup_component to capture config."""
        domain_input = integration.domain
        res = await async_process_component_config(hass, config_input, integration)
        config[domain_input] = None if res is None else res.get(domain_input)
        _LOGGER.debug(
            "Configuration for %s, Validated: %s, Original %s",
            domain_input,
            config[domain_input],
            config_input.get(domain_input),
        )
        return res

    assert isinstance(config, dict)
    with patch("homeassistant.config.async_process_component_config", mock_psc):
        yield config

    if domain is None:
        assert len(config) == 1, "assert_setup_component requires DOMAIN: {}".format(
            list(config.keys())
        )
        domain = list(config.keys())[0]

    res = config.get(domain)
    res_len = 0 if res is None else len(res)
    assert (
        res_len == count
    ), f"setup_component failed, expected {count} got {res_len}: {res}"


@contextmanager
def mock_storage(data=None):
    """Mock storage.

    Data is a dict {'key': {'version': version, 'data': data}}

    Written data will be converted to JSON to ensure JSON parsing works.
    """
    if data is None:
        data = {}

    orig_load = storage.Store._async_load

    async def mock_async_load(store):
        """Mock version of load."""
        if store._data is None:
            # No data to load
            if store.key not in data:
                return None

            mock_data = data.get(store.key)

            if "data" not in mock_data or "version" not in mock_data:
                _LOGGER.error('Mock data needs "version" and "data"')
                raise ValueError('Mock data needs "version" and "data"')

            store._data = mock_data

        # Route through original load so that we trigger migration
        loaded = await orig_load(store)
        _LOGGER.info("Loading data for %s: %s", store.key, loaded)
        return loaded

    def mock_write_data(store, path, data_to_write):
        """Mock version of write data."""
        # To ensure that the data can be serialized
        _LOGGER.info("Writing data to %s: %s", store.key, data_to_write)
        raise_contains_mocks(data_to_write)
        data[store.key] = json.loads(json.dumps(data_to_write, cls=store._encoder))

    async def mock_remove(store):
        """Remove data."""
        data.pop(store.key, None)

    with patch(
        "homeassistant.helpers.storage.Store._async_load",
        side_effect=mock_async_load,
        autospec=True,
    ), patch(
        "homeassistant.helpers.storage.Store._write_data",
        side_effect=mock_write_data,
        autospec=True,
    ), patch(
        "homeassistant.helpers.storage.Store.async_remove",
        side_effect=mock_remove,
        autospec=True,
    ):
        yield data


def raise_contains_mocks(val):
    """Raise for mocks."""
    if isinstance(val, Mock):
        raise ValueError

    if isinstance(val, dict):
        for dict_value in val.values():
            raise_contains_mocks(dict_value)

    if isinstance(val, list):
        for dict_value in val:
            raise_contains_mocks(dict_value)
