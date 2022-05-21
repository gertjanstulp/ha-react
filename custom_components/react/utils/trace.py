"""Trace support for script."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any

from homeassistant.components.trace import ActionTrace, async_store_trace
from homeassistant.components.trace.const import CONF_STORED_TRACES
from homeassistant.core import Context
from homeassistant.helpers.trace import TraceElement, trace_append_element, trace_path_get, trace_stack_pop, trace_stack_push, trace_stack_cv

from ..base import ReactBase
from ..lib.config import Workflow

if TYPE_CHECKING:
    from ..lib.runtime import WorkflowRun

from ..const import (
    DOMAIN
)

class ReactTrace(ActionTrace):
    _domain = DOMAIN

    def __init__(self, workflow: Workflow, context: Context) -> None:
        super().__init__(workflow.id, workflow.as_dict(), {}, context)
        self._actor_description: str | None = None

    def set_actor_description(self, trigger: str) -> None:
        self._actor_description = trigger

    def as_short_dict(self) -> dict[str, Any]:
        if self._short_dict:
            return self._short_dict

        result = super().as_short_dict()
        result["actor"] = self._actor_description
        return result


@contextmanager
def trace_workflow(
    run: WorkflowRun
) -> Iterator[ReactTrace]:
    """Trace execution of a script."""
    workflow = run.runtime.workflow_config
    trace = ReactTrace(workflow, run.run_context)
    
    async_store_trace(run.runtime.react.hass, trace, workflow.trace_config[CONF_STORED_TRACES])

    try:
        run.set_trace(trace)
        yield trace
    except Exception as ex:
        if workflow.id:
            trace.set_error(ex)
        raise ex
    finally:
        if workflow.id:
            trace.finished()


# def trace_actor1(index, variables: dict) -> str:
#     actor_path = f"actor/{index}"
#     trace_element = TraceElement(variables, actor_path)
#     trace_append_element(trace_element)
#     return actor_path


def node_trace_append(variables, path):
    """Append a TraceElement to trace[path]."""
    trace_element = TraceElement(variables, path)
    trace_append_element(trace_element)
    return trace_element


@contextmanager
def trace_node(variables):
    """Trace action execution."""
    path = trace_path_get()
    trace_element = node_trace_append(variables, path)
    trace_stack_push(trace_stack_cv, trace_element)

    try:
        yield trace_element
    except Exception as ex:
        trace_element.set_error(ex)
        raise ex
    finally:
        trace_stack_pop(trace_stack_cv)


# def parallel_trace_append(path):
#     """Append a TraceElement to trace[path]."""
#     trace_element = TraceElement({}, path)
#     trace_append_element(trace_element)
#     return trace_element


# @contextmanager
# def trace_parallel():
#     """Trace action execution."""
#     path = trace_path_get()
#     trace_element = parallel_trace_append(path)
#     trace_stack_push(trace_stack_cv, trace_element)

#     try:
#         yield trace_element
#     except Exception as ex:
#         trace_element.set_error(ex)
#         raise ex
#     finally:
#         trace_stack_pop(trace_stack_cv)


# def reactor_trace_append(variables, path):
#     """Append a TraceElement to trace[path]."""
#     trace_element = TraceElement(variables, path)
#     trace_append_element(trace_element)
#     return trace_element


# @contextmanager
# def trace_reactor(variables):
#     """Trace action execution."""
#     path = trace_path_get()
#     trace_element = reactor_trace_append(variables, path)
#     trace_stack_push(trace_stack_cv, trace_element)

#     try:
#         yield trace_element
#     except Exception as ex:
#         trace_element.set_error(ex)
#         raise ex
#     finally:
#         trace_stack_pop(trace_stack_cv)

# def create_variables(workflow: Workflow):
#     result = {
#         "this": {
#             ATTR_ENTITY_ID: workflow.entity_id,
#             state: 
#         }
#     }