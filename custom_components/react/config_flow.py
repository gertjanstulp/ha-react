import secrets

from homeassistant import config_entries

from .const import (
    DOMAIN,
)


@config_entries.HANDLERS.register(DOMAIN)
class ReactConfigFlow(config_entries.ConfigFlow):
    async def async_step_user(self, user_input=None):
        # Only a single instance of the integration
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        id = secrets.token_hex(6)

        await self.async_set_unique_id(id)
        self._abort_if_unique_id_configured(updates=user_input)

        return self.async_create_entry(title="React", data={})