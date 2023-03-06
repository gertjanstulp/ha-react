from __future__ import annotations

from aiohttp import web

from homeassistant.components.http import HomeAssistantView

from custom_components.react.base import ReactBase
from custom_components.react.react_frontend import locate_dir
from custom_components.react.react_frontend import VERSION as FE_VERSION
from custom_components.react.tasks.base import ReactTask, ReactTaskType


from ...const import (
    DOMAIN,
)

URL_BASE = "/reactfiles"


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Setup the React frontend."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.STARTUP


    async def async_execute(self) -> None:
        """Execute the task."""

        # Register themes
        self.react.hass.http.register_static_path(f"{URL_BASE}/themes", self.react.hass.config.path("themes"))

        # Register frontend
        if self.react.configuration.frontend_repo_url:
            self.task_logger(self.react.log.warning, "Frontend development mode enabled. Do not run in production!")
            self.react.hass.http.register_view(ReactFrontendDev())
        else:
            self.react.hass.http.register_static_path(f"{URL_BASE}/frontend", locate_dir(), cache_headers=False)

        # # Custom iconset
        # self.react.hass.http.register_static_path(
        #     f"{URL_BASE}/iconset.js", str(self.react.integration_dir / "iconset.js")
        # )
        # if "frontend_extra_module_url" not in self.react.hass.data:
        #     self.react.hass.data["frontend_extra_module_url"] = set()
        # self.react.hass.data["frontend_extra_module_url"].add(f"{URL_BASE}/iconset.js")

        # # Register www/community for all other files
        # use_cache = self.react.core.lovelace_mode == "storage"
        # self.task_logger(
        #     self.react.log.info,
        #     f"{self.react.core.lovelace_mode} mode, cache for /reactfiles/: {use_cache}",
        # )

        # self.react.hass.http.register_static_path(
        #     URL_BASE,
        #     self.react.hass.config.path("www/community"),
        #     cache_headers=use_cache,
        # )

        self.react.frontend_version = FE_VERSION

        # Add to sidepanel if needed
        if DOMAIN not in self.react.hass.data.get("frontend_panels", {}):
            self.react.hass.components.frontend.async_register_built_in_panel(
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
