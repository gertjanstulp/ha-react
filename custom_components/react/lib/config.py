from typing import Any

from homeassistant.const import (
    STATE_ON,
)
from homeassistant.core import (
    HomeAssistant, 
)
from homeassistant.helpers.typing import ConfigType

from .. import const as co

async def load_from_config(hass: HomeAssistant, domain_config: ConfigType):
    co.LOGGER.info("Loading react configuration")

    if domain_config:
        co.LOGGER.info("Found react configuration, processing")

        template_config = domain_config.get(co.CONF_TEMPLATES, {})
        workflow_config = domain_config.get(co.CONF_WORKFLOWS, {})

        templates = await _parse_template_config(hass, template_config)
        result = await _parse_workflow_config(hass, workflow_config, templates)
    else:
        co.LOGGER.info("No react configuration found")
        result = []

    return result

async def _parse_template_config(hass, template_config):
    co.LOGGER.info("Loading react templates")
    
    result = {}

    for id, config in template_config.items():
        co.LOGGER.info("Processing template '{}'".format(id))
        if not config:
            config = {}
        
        template = Template(config)
        result[id] = template

    return result

async def _parse_workflow_config(hass: HomeAssistant, workflow_config: dict, templates: dict):
    co.LOGGER.info("Loading react workflows")

    workflows = []
    
    for id, config in workflow_config.items():
        co.LOGGER.info("Processing workflow '{}'".format(id))
        if not config:
            config = {}
        
        workflow = Workflow(id, config)
        template = await _get_template_by_name(templates, workflow.template_name)
        workflow.load(config, template)
        workflows.append(workflow)

    return workflows

async def _get_template_by_name(templates, template_name):
    result = None
    if template_name:
        if template_name in templates.keys():
            result = templates[template_name]
        else:
            co.LOGGER.warn("Template '{}' not found".format(template_name))
    
    return result


class Template():
    def __init__(self, config):
        self._actor = config.get(co.ATTR_ACTOR, None)
        self._actor_type = config.get(co.ATTR_ACTOR_TYPE, None)
        self._actor_action = config.get(co.ATTR_ACTOR_ACTION, None)
        self._reactor = config.get(co.ATTR_REACTOR, None)
        self._reactor_type = config.get(co.ATTR_REACTOR_TYPE, None)
        self._reactor_action = config.get(co.ATTR_REACTOR_ACTION, None)
        self._reactor_timing = config.get(co.ATTR_REACTOR_TIMING, None)
        self._reactor_delay = config.get(co.ATTR_REACTOR_DELAY, None)
        self._reactor_overwrite = config.get(co.ATTR_REACTOR_OVERWRITE, None)
        self._reset_workflow = config.get(co.ATTR_RESET_WORKFLOW, None)
        self._action_forward = config.get(co.ATTR_ACTION_FORWARD, None)

    @property
    def actor(self):
        return self._actor

    @property
    def actor_type(self):
        return self._actor_type

    @property
    def actor_action(self):
        return self._actor_action

    @property
    def reactor(self):
        return self._reactor

    @property
    def reactor_type(self):
        return self._reactor_type

    @property
    def reactor_action(self):
        return self._reactor_action

    @property
    def reactor_timing(self):
        return self._reactor_timing

    @property
    def reactor_delay(self):
        return self._reactor_delay

    @property
    def reactor_overwrite(self):
        return self._reactor_overwrite
        
    @property
    def reset_workflow(self):
        return self._reset_workflow
    
    @property
    def action_forward(self):
        return self._action_forward
    
    def get_attr(self, name: str):
        if (hasattr(self, name)):
            return getattr(self, name)
        return None

class Workflow():
    def __init__(self, id, config):
        self._id = id
        self._entity_id = co.ENTITY_ID_FORMAT.format(id)
        self._template_name = config.get(co.ATTR_TEMPLATE, None)
        self._token = config.get(co.ATTR_TOKEN, None)
        self._friendly_name = config.get(co.ATTR_FRIENDLY_NAME, None)
        self._icon = config.get(co.CONF_ICON, None)

    def load(self, config, template):
        self._actor = self._get_property(co.ATTR_ACTOR, config, template, [])
        self._actor_type = self._get_property(co.ATTR_ACTOR_TYPE, config, template, '')
        self._actor_action = self._get_property(co.ATTR_ACTOR_ACTION, config, template, '')
        self._reactor = self._get_property(co.ATTR_REACTOR, config, template, [])
        self._reactor_type = self._get_property(co.ATTR_REACTOR_TYPE, config, template, '')
        self._reactor_action = self._get_property(co.ATTR_REACTOR_ACTION, config, template, '')
        self._reactor_timing = self._get_property(co.ATTR_REACTOR_TIMING, config, template, 'immediate')
        self._reactor_delay = self._get_property(co.ATTR_REACTOR_DELAY, config, template, '')
        self._reactor_overwrite = self._get_property(co.ATTR_REACTOR_OVERWRITE, config, template, False)
        self._action_forward = self._get_property(co.ATTR_ACTION_FORWARD, config, template, False)
        self._reset_workflow = self._get_property(co.ATTR_RESET_WORKFLOW, config, template, '')

    def _get_property(self, name: str, config, template: Template, default: Any):
        result = config.get(name, None)
        if not result and template is not None and hasattr(template, name):
            template_value = getattr(template, name)
            if isinstance(template_value, list):
                result = template_value[:]
            else:
                result = template_value

        if self._token is not None:
            result = self._replace_token(result, self._token)

        if result is None:
            result = default

        return result

    def _replace_token(self, input, token):
        result = input
        if isinstance(result, str):
            result = result.replace('<token>', token)
        elif isinstance(result, list):
            for i in range(len(result)):
                result[i] = result[i].replace('<token>', token)
        return result

    def create_reaction(self):
        return 

    @property
    def id(self):
        return self._id

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def template_name(self):
        return self._template_name

    @property
    def actor(self):
        return self._actor

    @property
    def actor_type(self):
        return self._actor_type

    @property
    def actor_action(self):
        return self._actor_action

    @property
    def reactor(self):
        return self._reactor

    @property
    def reactor_type(self):
        return self._reactor_type

    @property
    def reactor_action(self):
        return self._reactor_action

    @property
    def reactor_timing(self):
        return self._reactor_timing

    @property
    def reactor_delay(self):
        return self._reactor_delay

    @property
    def reactor_overwrite(self):
        return self._reactor_overwrite
        
    @property
    def reset_workflow(self):
        return self._reset_workflow
        
    @property
    def action_forward(self):
        return self._action_forward
    
    @property
    def friendly_name(self):
        return self._friendly_name
        
    @property
    def icon(self):
        return self._icon

    def get_attr(self, name: str):
        if (hasattr(self, name)):
            return getattr(self, name)
        return None
