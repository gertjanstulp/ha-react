from __future__ import annotations

from aiohttp import web

from homeassistant.components import frontend
from homeassistant.components.http import HomeAssistantView, StaticPathConfig

from custom_components.react.base import ReactBase
from custom_components.react.const import DOMAIN
from custom_components.react.react_frontend import locate_dir
from custom_components.react.react_frontend import VERSION as FE_VERSION
from custom_components.react.tasks.base import ReactTask, ReactTaskType

URL_BASE = "/reactfiles"


async def async_setup_task(react: ReactBase) -> Task:
    return Task(react=react)


class Task(ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.STARTUP


    async def async_execute(self) -> None:
        self.task_logger.debug("Setting up react frontend")

        # Register themes
        await self.react.hass.http.async_register_static_paths([StaticPathConfig(f"{URL_BASE}/themes", self.react.hass.config.path("themes"), cache_headers=True)])

        # Register frontend
        if self.react.configuration.frontend_repo_url:
            self.task_logger.warning("Frontend development mode enabled. Do not run in production!")
            self.react.hass.http.register_view(ReactFrontendDev())
        else:
            await self.react.hass.http.async_register_static_paths([StaticPathConfig(f"{URL_BASE}/frontend", locate_dir(), cache_headers=False)])

        self.react.frontend_version = FE_VERSION

        # Add to sidepanel if needed
        if DOMAIN not in self.react.hass.data.get("frontend_panels", {}):
            frontend.async_register_built_in_panel(
                self.react.hass,
                component_name="custom",
                sidebar_title=self.react.configuration.sidepanel_title,
                sidebar_icon=self.react.configuration.sidepanel_icon,
                frontend_url_path=DOMAIN,
                config={
                    "_panel_custom": {
                        "name": "react-frontend",
                        "embed_iframe": True,
                        "trust_external": False,
                        "js_url": f"/reactfiles/frontend/entrypoint.js?reacttag={FE_VERSION}",
                    }
                },
                require_admin=True,
            )


class ReactFrontendDev(HomeAssistantView):
    """Dev View Class for React."""

    requires_auth = False
    name = "react_files:frontend"
    url = r"/reactfiles/frontend/{requested_file:.+}"

    async def get(self, request, requested_file):  # pylint: disable=unused-argument
        """Handle React Web requests."""
        react: ReactBase = request.app["hass"].data.get(DOMAIN)
        requested = requested_file.split("/")[-1]
        request = await react.session.get(f"{react.configuration.frontend_repo_url}/{requested}")
        if request.status == 200:
            result = await request.read()
            response = web.Response(body=result)
            response.headers["Content-Type"] = "application/javascript"

            return response
