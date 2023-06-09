"""Trace support for script."""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Any

from homeassistant.components.trace import ActionTrace, async_store_trace
from homeassistant.components.trace.const import CONF_STORED_TRACES
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers.trace import (
    TraceElement, 
    TemplateVarsType,
    variables_cv,
)
from homeassistant.util import dt as dt_util

from custom_components.react.const import DOMAIN
from custom_components.react.config.config import Workflow

ROOT_SECTION = "root"


class ReactTraceSection():
    def __init__(self, variables: dict[str, Any], last_variables: dict[str, Any] = {}) -> None:
        self.variables = variables
        self.last_variables = last_variables


    def shift(self):
        self.last_variables = dict(self.variables)


class ReactTrace(ActionTrace):
    _domain = DOMAIN

    def __init__(self, workflow_id: str, workflow_config_dict: dict, context: Context, trace_variables: dict[str, Any]) -> None:
        super().__init__(workflow_id, workflow_config_dict, {}, context)
        
        self._actor_description: str | None = None
        self.trace_nodes: dict[str, deque[ReactTraceElement]] = {}
        self.trace_paths: dict[str, list[str]] = {}
        self.trace_sections: dict[str, ReactTraceSection] = { ROOT_SECTION: ReactTraceSection(trace_variables) }
        self.set_trace(self.trace_nodes)


    def set_actor_description(self, trigger: str) -> None:
        self._actor_description = trigger


    def as_short_dict(self) -> dict[str, Any]:
        if self._short_dict:
            return self._short_dict

        result = super().as_short_dict()
        result["actor"] = self._actor_description
        return result


    def get_vars(self, section_id: str = ROOT_SECTION):
        return self.get_trace_section(section_id).variables


    def set_var(self, name: str, value: Any, section_id: str = ROOT_SECTION):
        self.get_vars(section_id)[name] = value


    def trace_node(self, path: str, **kwargs: Any) -> ReactTraceElement:
        return self.trace_section_node(ROOT_SECTION, path, **kwargs)


    def trace_section_node(self, section_id: str, path: str, **kwargs: Any) -> ReactTraceElement:
        return self.trace_node_core(path, self.get_trace_section(section_id), **kwargs)


    def get_trace_section(self, section_id: str):
        if not section_id in self.trace_sections:
            root_section = self.trace_sections.get(ROOT_SECTION)
            self.trace_sections[section_id] = ReactTraceSection(dict(root_section.variables), dict(root_section.last_variables))
        return self.trace_sections.get(section_id)


    def trace_node_core(self, path: str, section: ReactTraceSection, **kwargs: Any):
        node = ReactTraceElement(section, path)
        if (path := node.path) not in self.trace_nodes:
            self.trace_nodes[path] = deque()
        self.trace_nodes[path].append(node)
        if kwargs:
            node.set_result(**kwargs)
        return node


    def insert_node(self, path: str, node: ReactTraceElement):
        paths = path.split("/")
        inserted = False
        for i,existing_paths in enumerate(self.trace_paths):
            if self.compare(existing_paths, paths) > 0:
                self.trace_nodes[path].insert(i, node)
                inserted = True
                break
        if not inserted:
            self.trace_nodes[path].append(node)
        self.trace_paths[path] = paths


    def compare(self, paths1: list[str], paths2: list[str]):
        if paths1[0] < paths2[0]:
            return -1
        elif paths1[0] > paths2[0]:
            return 1
        else:
            if paths1[1] < paths2[1]:
                return -1
            elif paths1[1] > paths2[1]:
                return 1
        return 1
            

class ReactTraceElement(TraceElement):
    def __init__(self, section: ReactTraceSection, path: str) -> None:
        """Container for trace data."""
        self._child_key: str | None = None
        self._child_run_id: str | None = None
        self._error: Exception | None = None
        self.path: str = path
        self._result: dict[str, Any] | None = None
        self.reuse_by_child = False
        self._timestamp = dt_util.utcnow()

        # if variables is None:
        #     variables = {}
        # last_variables = variables_cv.get() or {}
        # variables_cv.set(dict(variables))
        changed_variables = {
            key: value
            for key, value in section.variables.items()
            if key not in section.last_variables or section.last_variables[key] != value
        }
        self._variables = changed_variables
        section.shift()
        

def create_trace(hass: HomeAssistant, workflow_config: Workflow, context: Context, trace_variables: dict[str, Any]) -> ReactTrace:
    trace = ReactTrace(workflow_config.id, workflow_config.get_trace_config(), context, trace_variables)
    async_store_trace(hass, trace, workflow_config.trace_config[CONF_STORED_TRACES])
    return trace
