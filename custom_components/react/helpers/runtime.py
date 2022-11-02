# from homeassistant.core import HomeAssistant
# from custom_components.react.base import ReactBase
# from custom_components.react.const import DOMAIN
# from custom_components.react.lib.config import Workflow

# from custom_components.react.runtime.handler import WorkflowHandler
# from custom_components.react.helpers.scheduler import get_scheduler


# def create_workflow_handler(react: ReactBase, workflow_config: Workflow, entity_id: str) -> WorkflowHandler:
#     handler = react.handler_registry.create_new(workflow_config, entity_id)
#     react.scheduler_registry.register(workflow_config.id)
#     return handler


# def destroy_workflow_handler(react: ReactBase, workflow_id: str):
#     react.handler_registry.destroy(workflow_id)
#     react.scheduler_registry.unregister(workflow_id)


# def abort_all(react: ReactBase, workflow_id: str):
#     get_scheduler(react, workflow_id).abort_all()
