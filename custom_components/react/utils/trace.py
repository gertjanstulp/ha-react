"""Trace support for script."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from homeassistant.components.trace import ActionTrace, async_store_trace
from homeassistant.components.trace.const import CONF_STORED_TRACES
from homeassistant.helpers.trace import TraceElement, trace_append_element, trace_path_get, trace_stack_pop, trace_stack_push, trace_stack_cv

from ..lib.config import Workflow

if TYPE_CHECKING:
    from ..lib.runtime import WorkflowRun, WorkflowRunContext

from ..const import (
    DOMAIN
)


class ReactTrace(ActionTrace):
    _domain = DOMAIN

    def __init__(self, wctx: WorkflowRunContext) -> None:
        super().__init__(wctx.workflow_config.id, wctx.workflow_config.as_dict(wctx.actx.actor_id), {}, wctx.hass_run_context)
        
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
def trace_workflow(workflow_run: WorkflowRun) -> Iterator[ReactTrace]:
    """Trace execution of a script."""
    trace = ReactTrace(workflow_run.wctx)
    
    async_store_trace(workflow_run.wctx.react.hass, trace, workflow_run.wctx.workflow_config.trace_config[CONF_STORED_TRACES])

    try:
        workflow_run.set_trace(trace)
        yield trace
    except Exception as ex:
        if workflow_run.wctx.workflow_config.id:
            trace.set_error(ex)
        raise ex
    finally:
        if workflow_run.wctx.workflow_config.id:
            trace.finished()


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
