from __future__ import annotations

import asyncio
from collections import deque
from contextvars import ContextVar
from datetime import datetime
from decimal import InvalidOperation
from itertools import product
from typing import Callable, Generator, Union
import secrets

from homeassistant.core import HomeAssistant, callback, Context, CALLBACK_TYPE
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers.event import async_track_template, async_track_point_in_utc_time
from homeassistant.helpers.template import Template
from homeassistant.util import dt as dt_util
from homeassistant.util.dt import utcnow
from custom_components.react.enums import YIELD_RESULTS, StepResult

from custom_components.react.lib.config import Workflow, calculate_reaction_datetime
from custom_components.react.reactions.base import ReactionData
from custom_components.react.runtime.snapshots import WorkflowSnapshot
from custom_components.react.utils.events import ActionEventPayload
from custom_components.react.utils.logger import format_data, get_react_logger
from custom_components.react.utils.struct import ReactorRuntime
from custom_components.react.utils.trace import ReactTrace, create_trace

from custom_components.react.const import (
    ACTION_AVAILABLE, 
    ACTION_TOGGLE, 
    ACTION_UNAVAILABLE, 
    ATTR_ACTOR, 
    ATTR_CONDITION, 
    ATTR_CONTEXT,
    ATTR_CREATED, 
    ATTR_DELAY,
    ATTR_DONE, 
    ATTR_EVENT, 
    ATTR_ID,
    ATTR_REACTOR_ID,
    ATTR_REMAINING,
    ATTR_RUN_ID, 
    ATTR_SCHEDULE,
    ATTR_START_TIME, 
    ATTR_STATE, 
    ATTR_THIS,
    ATTR_TIMESTAMP, 
    ATTR_VARIABLES,
    ATTR_WAIT,
    ATTR_WAIT_TYPE,
    ATTR_WHEN,
    ATTR_WORKFLOW_ID,
    EVENT_REACT_REACTION,
    EVENT_REACTION_REGISTRY_UPDATED,
    EVENT_RUN_REGISTRY_UPDATED,
    RESTART_MODE_FORCE, 
    SIGNAL_WORKFLOW_RESET, 
    TRACE_PATH_ACTOR, 
    TRACE_PATH_CONDITION,
    TRACE_PATH_DELAY,
    TRACE_PATH_DISPATCH, 
    TRACE_PATH_PARALLEL, 
    TRACE_PATH_REACTOR,
    TRACE_PATH_RESET,
    TRACE_PATH_SCHEDULE,
    TRACE_PATH_STATE,
    TRACE_PATH_TRIGGER,
    WORKFLOW_MODE_QUEUED, 
    WORKFLOW_MODE_RESTART, 
    WORKFLOW_MODE_SINGLE,
)


_LOGGER = get_react_logger()

run_stack_cv: ContextVar[list[int] | None] = ContextVar("run_stack", default=None)


class _ConditionFail(Exception):
    """Throw if workflow needs to stop because a condition evaluated to False."""


DONE_RESULTS = [StepResult.SUCCESS, StepResult.FAIL, StepResult.STOP]


def make_path(elements: Union[str, list[str]], parent: str = None):
    if isinstance(elements, str):
        elements = [elements]
    if parent:
        elements.insert(0, parent)
    return "/".join(elements)


class ReactionRegistry:
    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._reactions_by_id: dict[str, Reaction] = {}
        self._reactions_by_run: dict[str, list[Reaction]] = {}


    def get_all_reactions(self) -> list[dict]:
        return [ reaction.as_short_dict() for reaction in self._reactions_by_id.values() ]


    def get_reaction(self, reaction_id: str) -> Reaction:
        return self._reactions_by_id.get(reaction_id, None)


    def get_reactions_by_run(self, workflow_run_id: str) -> list[Reaction]:
        return list(self._reactions_by_run.get(workflow_run_id))


    def register(self, reactor: ReactorRuntime, reaction: Reaction) -> Reaction:
        if reactor.overwrite:
            existing_reactions = self.find(workflow_id=reaction.workflow_id, reactor_id=reaction.reactor_id)
            for existing_reaction in existing_reactions:
                existing_reaction.stop()

        id = secrets.token_hex(6)
        while id in self._reactions_by_id:
            id = secrets.token_hex(6)
        reaction.id = id

        self._reactions_by_id[reaction.id] = reaction
        if not reaction.workflow_run_id in self._reactions_by_run:
            self._reactions_by_run[reaction.workflow_run_id] = []
        self._reactions_by_run[reaction.workflow_run_id].append(reaction)

        self._hass.bus.async_fire(
            EVENT_REACTION_REGISTRY_UPDATED, {"action": "create", "run_id": reaction.id}
        )
        return reaction


    def remove(self, reaction: Reaction):
        self._reactions_by_id.pop(reaction.id)
        self._reactions_by_run[reaction.workflow_run_id].remove(reaction)

        self._hass.bus.async_fire(
            EVENT_REACTION_REGISTRY_UPDATED, {"action": "remove", "run_id": reaction.id}
        )


    def find(self, workflow_id: str = None, reactor_id: str = None) -> Generator[Reaction, None, None]:
        for reaction in list(self._reactions_by_id.values()):
            if ((workflow_id is None or reaction.workflow_id == workflow_id) and
                (reactor_id is None or reaction.reactor_id == reactor_id)):
                yield reaction


class RunRegistry:
    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._runs: dict[str, list[WorkflowRun]] = {}
        self._runs_by_id: dict[str, WorkflowRun] = {}


    def get_all_runs(self) -> list[dict]:
        return [ run.as_short_dict() for run in self._runs_by_id.values() ]


    def get_runs(self, workflow_id: str) -> list[WorkflowRun]:
        return self._runs.get(workflow_id, [])


    def get_run(self, run_id: str) -> WorkflowRun:
        return self._runs_by_id.get(run_id, None)


    def register(self, run: WorkflowRun):
        id = secrets.token_hex(6)
        while id in self._runs_by_id:
            id = secrets.token_hex(6)
        run.id = id

        if not run.workflow_id in self._runs:
            self._runs[run.workflow_id] = []
        self._runs[run.workflow_id].append(run)
        self._runs_by_id[run.id] = run

        self._hass.bus.async_fire(
            EVENT_RUN_REGISTRY_UPDATED, {"action": "create", "run_id": run.id}
        )
        return run


    def remove(self, workflow_id: str, workflow_run: WorkflowRun):
        self._runs[workflow_id].remove(workflow_run)
        self._runs_by_id.pop(workflow_run.id)

        self._hass.bus.async_fire(
            EVENT_RUN_REGISTRY_UPDATED, {"action": "remove", "run_id": workflow_run.id}
        )


    def find(self, workflow_id: str = None) -> Generator[Reaction, None, None]:
        for run in list(self._runs_by_id.values()):
            if (workflow_id is None or run.workflow_id == workflow_id):
                yield run


class ReactRuntime:

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._workflow_runtimes: dict[str, WorkflowRuntime] = {}
        self.run_registry = RunRegistry(hass)
        self.reaction_registry = ReactionRegistry(hass)

        @callback
        async def async_reset(workflow_id: str):
            if workflow_runtime := self.get_workflow_runtime(workflow_id):
                await workflow_runtime.async_stop_all_runs()
        self._cancel_reset = async_dispatcher_connect(hass, SIGNAL_WORKFLOW_RESET, async_reset)


    def _debug(self, message: str):
        _LOGGER.debug(f"Runtime: ReactRuntime - {message}")

        
    def create_workflow_runtime(self, workflow_config: Workflow) -> WorkflowRuntime:
        self._debug(f"Creating workflowruntime for {workflow_config.id}")
        result = WorkflowRuntime(self._hass, self.run_registry, self.reaction_registry, workflow_config)
        self._workflow_runtimes[workflow_config.id] = result
        self._debug(f"Created workflowruntime for {workflow_config.id}")
        return result


    async def async_destroy_workflow_runtime(self, workflow_id: str, is_hass_shutdown: bool = False):
        self._debug(f"Destroying workflowruntime for {workflow_id}")
        await self.async_stop_workflow_runtime(workflow_id, is_hass_shutdown=is_hass_shutdown)
        self._workflow_runtimes.pop(workflow_id)
        self._debug(f"Destroyed workflowruntime for {workflow_id}")


    def start_workflow_runtime(self, workflow_id: str):
        if workflow_runtime := self.get_workflow_runtime(workflow_id):
            workflow_runtime.start()


    async def async_stop_workflow_runtime(self, workflow_id: str, is_hass_shutdown: bool = False):
        self._debug(f"Stopping workflowruntime for {workflow_id}")
        workflow_runtime = self.get_workflow_runtime(workflow_id)
        if workflow_runtime and workflow_runtime.running:
            await workflow_runtime.async_stop(is_hass_shutdown=is_hass_shutdown)
        self._debug(f"Stopped workflowruntime for {workflow_id}")


    def get_workflow_runtime(self, workflow_id: str) -> WorkflowRuntime:
        return self._workflow_runtimes.get(workflow_id, None)


    async def async_run(self, workflow_id: str, snapshot: WorkflowSnapshot, entity_vars: dict, hass_run_context: Context):
        if workflow_runtime := self.get_workflow_runtime(workflow_id):
            await workflow_runtime.async_run(snapshot, entity_vars, hass_run_context)


    def run_now(self, run_id: str):
        workflow_run = self.run_registry.get_run(run_id)
        if workflow_run:
            workflow_run.force_resume()
        else:
            _LOGGER.warn(f"Workflow run '{run_id}' could not be found")


    def react_now(self, reaction_id: str):
        reaction = self.reaction_registry.get_reaction(reaction_id)
        if reaction:
            reaction.force_resume()
        else:
            _LOGGER.warn(f"Reaction '{reaction_id}' could not be found")


    async def async_delete_run(self, run_id: str):
        workflow_run = self.run_registry.get_run(run_id)
        if workflow_run:
            await workflow_run.async_stop()
        else:
            _LOGGER.warn(f"Workflow run '{run_id}' could not be found")


    def delete_reaction(self, reaction_id: str):
        reaction = self.reaction_registry.get_reaction(reaction_id)
        if reaction:
            reaction.stop()
        else:
            _LOGGER.warn(f"Reaction '{reaction_id}' could not be found")


    async def async_shutdown(self, is_hass_shutdown: bool = False):
        if self._cancel_reset:
            self._cancel_reset()
            self._cancel_reset = None
        for workflow_id in list(self._workflow_runtimes):
            await self.async_destroy_workflow_runtime(workflow_id, is_hass_shutdown=is_hass_shutdown)

    
class WorkflowRuntime:

    def __init__(self, hass: HomeAssistant, run_registry: RunRegistry, reaction_registry: ReactionRegistry, workflow_config: Workflow) -> None:
        self._hass = hass
        self._run_registry = run_registry
        self._reaction_registry = reaction_registry
        self._workflow_config = workflow_config
        self._queue: deque[WorkflowRun] = deque()
        self.running = False
        

    def _debug(self, message: str):
        _LOGGER.debug(f"Runtime: WorkflowRuntime {self._workflow_config.id} - {message}")


    def get_runs(self) -> list[WorkflowRun]:
        return self._run_registry.get_runs(self._workflow_config.id)


    def start(self):
        self._debug("starting")
        self.running = True
        self._debug("started")


    async def async_stop(self, is_hass_shutdown: bool = False):
        self._debug("stopping")
        self.running = False
        await self.async_stop_all_runs(is_hass_shutdown=is_hass_shutdown)
        self._debug("stopped")


    async def async_run(self, snapshot: WorkflowSnapshot, entity_vars: dict, hass_run_context: Context):
        self._debug(f"triggered by event ({format_data(entity=snapshot.action_event.payload.entity, type=snapshot.action_event.payload.type, action=snapshot.action_event.payload.action, data=snapshot.action_event.payload.data)})")
        if not self.running:
            self._debug(f"skipping (workflow is disabled)")
            return
        elif self._workflow_config.mode == WORKFLOW_MODE_SINGLE and self.runs > 0:
            self._debug(f"skipping (workflow is in 'Single' mode and another run is active)")
            return

        # Prevent non-allowed recursive calls which will cause deadlocks when we try to
        # stop (restart) or wait for (queued) our own workflow run.
        run_stack = run_stack_cv.get()
        if (
            self._workflow_config.mode in (WORKFLOW_MODE_RESTART, WORKFLOW_MODE_QUEUED)
            and (run_stack := run_stack_cv.get()) is not None
            and id(self) in run_stack
        ):
            self._debug(f"skipping (workflow is in 'Restart' or 'Queued' mode and a recursion was detected)")
            return

        run = WorkflowRun(
            self._hass, 
            self._workflow_config,
            self._reaction_registry,
            id(self), 
            snapshot, 
            dict(entity_vars), 
            hass_run_context, 
            self.finish_run)

        self._run_registry.register(run)
        if self._workflow_config.mode == WORKFLOW_MODE_RESTART:
            await self.async_stop_all_runs(spare=run)

        if self._workflow_config.mode == WORKFLOW_MODE_QUEUED and self.runs > 1:
            self._queue.append(run)
        else:
            await self.async_run_now(run)


    async def async_run_now(self, run: WorkflowRun):
        try:
            self._debug(f"startig run '{run.id}'")
            await run.async_run()
        except asyncio.CancelledError:
            await run.async_stop()
            raise

    
    def finish_run(self, run: WorkflowRun):
        self._run_registry.remove(self._workflow_config.id, run)
        if self._workflow_config.mode == WORKFLOW_MODE_QUEUED:
            if len(self._queue) > 0:
                next_run = self._queue.popleft()
                self._hass.add_job(self.async_run_now(next_run))


    async def async_stop_all_runs(self, is_hass_shutdown: bool = False, spare: WorkflowRun | None = None) -> None:
        self._debug(f"stopping all runs")
        self._queue.clear()
        aws = [ asyncio.create_task(run.async_stop(is_hass_shutdown)) for run in self.get_runs() if run != spare ]
        if not aws:
            self._debug(f"no runs to stop")
            return
        await asyncio.shield(self._async_stop_all_runs(aws))


    async def _async_stop_all_runs(self, aws: list[asyncio.Task]) -> None:
        await asyncio.wait(aws)


    @property
    def runs(self) -> int:
        return len(self.get_runs())

    
    @property
    def queue_length(self) -> int:
        return len(self._queue)


class WorkflowRun:
    def __init__(self, 
        hass: HomeAssistant, 
        workflow_config: Workflow,
        reaction_registry: ReactionRegistry,
        runtime_id: int,
        snapshot: WorkflowSnapshot, 
        entity_vars: dict, 
        hass_run_context: Context,
        run_done_callback: Callable[[WorkflowRun], None],
    ) -> None:

        self._hass = hass
        self._workflow = workflow_config
        self._reaction_registry = reaction_registry
        self._runtime_id = runtime_id
        self.snapshot = snapshot
        self._entity_vars = entity_vars
        self._hass_run_context = hass_run_context
        self._run_done_callback = run_done_callback

        self._stopped = False
        self._start_time = utcnow()
        self.id: str = None


    @property
    def workflow_id(self):
        return self._workflow.id


    def _debug(self, message: str):
        _LOGGER.debug(f"Runtime: WorkflowRun {self.id} - {message}")


    def as_short_dict(self):
        return {
            ATTR_ID: self.id,
            ATTR_WORKFLOW_ID: self.workflow_id,
            ATTR_START_TIME: self._start_time,
        }

    
    async def async_stop(self, is_hass_shutdown: bool = False) -> None:
        self._debug(f"stopping")

        self._stopped = True
        for reaction in self._get_reactions():
            reaction.stop(is_hass_shutdown)


    def finish(self) -> None:
        self._debug(f"finished")
        self.trace.finished()
        self._run_done_callback(self)


    @callback
    async def async_run(self):
        # Push the run to the run execution stack
        if (run_stack := run_stack_cv.get()) is None:
            run_stack = []
            run_stack_cv.set(run_stack)
        run_stack.append(self._runtime_id)

        try:
            self._debug("running")
            await self.async_step_main()
        except _ConditionFail:
            self.finish()
        except Exception as ex:
            _LOGGER.exception(f"workflow run failed")
            raise


    async def async_step_main(self):
        self.step_init_trace()
        self.step_actor_root()
        self.step_context_builder()
        await self.async_step_reactors_root()


    def step_init_trace(self):
        variables = {
            ATTR_THIS: self._entity_vars,
            ATTR_VARIABLES: 
                self.snapshot.variables.as_dict() | 
                { ATTR_EVENT: self.snapshot.action_event.payload } |
                { ATTR_ACTOR: { ATTR_ID: self.snapshot.actor.id } },
            ATTR_ACTOR: {
                ATTR_ID: self.snapshot.actor.id, 
                ATTR_CONTEXT: self.snapshot.action_event.context
            }
        }
        self.trace = create_trace(self._hass, self._workflow, self._hass_run_context, variables)        


    def step_actor_root(self):
        path = make_path([TRACE_PATH_ACTOR, str(self.snapshot.actor.index)])
        self.step_actor_trigger(path)
        self.step_actor_condition(path)


    def step_actor_trigger(self, parent_path: str):
        self.trace.trace_node(make_path(TRACE_PATH_TRIGGER, parent_path), event=self.snapshot.action_event.payload.as_dict(skip_none=True))


    def step_actor_condition(self, parent_path: str):
        condition_result = self.snapshot.actor.condition
        if self.snapshot.actor.is_template(ATTR_CONDITION):
            self.trace.trace_node(make_path(TRACE_PATH_CONDITION, parent_path), result=condition_result)
            
        if not condition_result:
            self._debug(f"skipping actor {self.snapshot.actor.id} (condition false)")
            raise _ConditionFail()
        

    def step_context_builder(self):
        self.trace.set_var(ATTR_CONTEXT, self.snapshot.action_event.context)


    async def async_step_reactors_root(self):
        if len(self.snapshot.reactors) > 1:
            self.trace.trace_node(TRACE_PATH_PARALLEL, parallel=True)
        
        def create_reaction(reactor: ReactorRuntime) -> Reaction:
            reaction = Reaction(self._hass, self.id, self.workflow_id, self.snapshot.action_event.payload, reactor, self.trace, self.reaction_done)
            self._reaction_registry.register(reactor, reaction)
            return reaction
        reactions = [ create_reaction(reactor) for reactor in self.snapshot.reactors ]
        
        async def async_run_reactor(reaction: Reaction) -> None:
            self._debug(f"starting reaction {reaction.id}")
            reaction.run()
        results = await asyncio.gather(
            *(async_run_reactor(reaction) for reaction in reactions),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, Exception):
                raise result


    def reaction_done(self, reaction: Reaction):
        self._reaction_registry.remove(reaction)
        all_done = all([reaction.result in DONE_RESULTS for reaction in self._get_reactions()])
        if all_done:
            self.finish()


    def force_resume(self, reactor_id: str = None):
        for reaction in self._get_reactions():
            if reactor_id is None or reaction.id == reactor_id:
                reaction.force_resume()


    def _get_reactions(self) -> list[Reaction]:
        return self._reaction_registry.get_reactions_by_run(self.id)


class Reaction:
    def __init__(self, 
        hass: HomeAssistant,
        workflow_run_id: str,
        workflow_id: str, 
        event_payload: ActionEventPayload,
        reactor: ReactorRuntime,
        trace: ReactTrace,
        reaction_done_callback: Callable[[Reaction], None],
    ) -> None:

        self._hass = hass
        self.workflow_run_id = workflow_run_id
        self.workflow_id = workflow_id
        self._event_payload = event_payload
        self._reactor = reactor
        self._trace = trace
        self._reaction_done_callback = reaction_done_callback

        self._steps = self.run_steps()
        self._path = make_path([TRACE_PATH_REACTOR, str(self._reactor.index)])
        self.result = StepResult.NONE
        self._cancel_yield: CALLBACK_TYPE = None
        self.id: str = None
        self._created = utcnow()
        self._when: datetime = None
        self._restart_mode: str = None
        

    @property
    def reactor_id(self):
        return self._reactor.id


    def _debug(self, message: str):
        _LOGGER.debug(f"Runtime: Reaction {self._reactor.id} {self.id} - {message}")


    def as_short_dict(self):
        return {
            ATTR_ID: self.id,
            ATTR_RUN_ID: self.workflow_run_id,
            ATTR_REACTOR_ID: self._reactor.id,
            ATTR_WORKFLOW_ID: self.workflow_id,
            ATTR_CREATED: self._created,
            ATTR_WHEN: self._when,
            ATTR_WAIT_TYPE: self.result,
        }


    def make_reactor_path(self, elements: Union[str, list[str]]):
        return make_path(elements, self._path)


    def stop(self, is_hass_shutdown: bool = False):
        self._debug("stopping")
        if is_hass_shutdown and self._restart_mode == RESTART_MODE_FORCE:
            self.force_resume()
        else:
            self.yield_done()
            self._steps.close()
            self.result = StepResult.STOP
            self.finish()


    def force_resume(self):
        while self.result in YIELD_RESULTS:
            self.run()


    def finish(self):
        self._debug(f"finished")
        self._reaction_done_callback(self)


    def yield_done(self):
        if self._cancel_yield:
            self._cancel_yield()
            self._cancel_yield = None


    @callback
    def run(self, *args):
        try:
            self._debug("resuming" if self.result in YIELD_RESULTS else "running")
            if self.result in DONE_RESULTS:
                raise InvalidOperation()
            self.result = next(self._steps, StepResult.SUCCESS)
            if self.result in DONE_RESULTS:
                self._steps.close()
                self.finish()
        except Exception as ex:
            _LOGGER.exception(ex)
            self.result = StepResult.FAIL
            self.finish()


    def run_steps(self) -> Generator[StepResult, None, None]:
        try:
            self.step_reactor_condition()
            yield from self.step_reactor_event()
        except _ConditionFail:
            self._debug(f"skipping (condition false)")
            pass

    
    def step_reactor_condition(self):
        condition_result = self._reactor.condition
        if self._reactor.is_template(ATTR_CONDITION):
            self._trace.trace_section_node(self.id, self.make_reactor_path(TRACE_PATH_CONDITION), result=condition_result)
        if not condition_result:
            raise _ConditionFail()


    def step_reactor_event(self) -> Generator[StepResult, None, None]:
        reactor_action = [ self._event_payload.action ] if self._reactor.forward_action else self._reactor.action
        reactor_data = [ self._event_payload.data ] if self._reactor.forward_data else self._reactor.data
        for entity, type, action, data in product(self._reactor.entity or [None], self._reactor.type or [None], reactor_action or [None], reactor_data or [None]):
            reaction = ReactionData(self._reactor.id, entity, type, action, data.as_dict() if data else None)
            yield from self.step_reaction_main(reaction)


    def step_reaction_main(self, reaction: ReactionData) -> Generator[StepResult, None, None]:
        if self._reactor.wait:
            if ATTR_STATE in self._reactor.wait.keys():
                yield from self.step_reaction_state()
            if ATTR_DELAY in self._reactor.wait.keys():
                yield from self.step_reaction_delay()
            elif ATTR_SCHEDULE in self._reactor.wait.keys():
                yield from self.step_reaction_schedule()
        if self._reactor.reset_workflow:
            self.step_reaction_reset()
        else:
            self.step_reaction_dispatch(reaction)

    
    def step_reaction_state(self) -> Generator[StepResult, None, None]:
        # could be configured in the future
        timeout = 0

        wait = {ATTR_REMAINING: timeout, ATTR_DONE: False}
        self._trace.set_var(ATTR_WAIT, wait, self.id)
        self._trace.trace_section_node(self.id, self.make_reactor_path(TRACE_PATH_STATE), wait=wait)
        if self._reactor.wait.state.condition:
            wait[ATTR_DONE] = True
            return

        self._restart_mode = self._reactor.wait.state.restart_mode
        wait_template_string = self._reactor.wait.state.get_template(ATTR_CONDITION)
        wait_template = Template(wait_template_string, self._hass)
        self._cancel_yield = async_track_template(self._hass, wait_template, self.run, self._trace.get_vars(self.id))
        self._debug("yielding on state")
        yield StepResult.YIELD_STATE

        wait[ATTR_DONE] = True
        self.yield_done()


    def step_reaction_delay(self) -> Generator[StepResult, None, None]:
        self._when = calculate_reaction_datetime(delay = self._reactor.wait.delay)
        trace_timestamp = self._when.astimezone(dt_util.DEFAULT_TIME_ZONE).strftime("%c (%Z)")
        wait = {ATTR_DELAY: self._reactor.wait.delay, ATTR_TIMESTAMP: trace_timestamp, ATTR_DONE: False}
        self._trace.set_var(ATTR_WAIT, wait, self.id)
        self._trace.trace_section_node(self.id, self.make_reactor_path(TRACE_PATH_DELAY), wait=wait)

        self._restart_mode = self._reactor.wait.delay.restart_mode
        self._cancel_yield = async_track_point_in_utc_time(self._hass, self.run, self._when)
        self._debug("yielding with delay")
        yield StepResult.YIELD_DELAY
        
        wait[ATTR_DONE] = True
        self.yield_done()


    def step_reaction_schedule(self) -> Generator[StepResult, None, None]:
        self._when = calculate_reaction_datetime(schedule = self._reactor.wait.schedule)
        trace_timestamp = self._when.astimezone(dt_util.DEFAULT_TIME_ZONE).strftime("%c (%Z)")
        wait = {ATTR_SCHEDULE: self._reactor.wait.schedule.as_dict(), ATTR_TIMESTAMP: trace_timestamp, ATTR_DONE: False}
        self._trace.set_var(ATTR_WAIT, wait, self.id)
        self._trace.trace_section_node(self.id, self.make_reactor_path(TRACE_PATH_SCHEDULE), wait=wait)

        self._restart_mode = self._reactor.wait.schedule.restart_mode
        self._cancel_yield = async_track_point_in_utc_time(self._hass, self.run, self._when)
        self._debug("yielding with schedule")
        yield StepResult.YIELD_SCHEDULE
 
        wait[ATTR_DONE] = True
        self.yield_done()


    def step_reaction_reset(self):
        self._trace.trace_section_node(self.id, self.make_reactor_path(TRACE_PATH_RESET), reset_workflow=self._reactor.reset_workflow)
        self._debug(f"dispatching reset: {self._reactor.reset_workflow}")
        async_dispatcher_send(self._hass, SIGNAL_WORKFLOW_RESET, self._reactor.reset_workflow)


    def step_reaction_dispatch(self, reaction: ReactionData):
        node = self._trace.trace_section_node(self.id, self.make_reactor_path(TRACE_PATH_DISPATCH))
        if self._reactor.forward_action and self._event_payload.action == ACTION_TOGGLE:
            # Don't forward toggle actions as they are always accompanied by other actions which will be forwarded
            self._debug(f"skipping (action 'toggle' with forward_action)")
            node.set_result(message="Skipped, toggle with forward-action")
                
        elif self._reactor.forward_action and (self._event_payload.action == ACTION_AVAILABLE or self._event_payload.action == ACTION_UNAVAILABLE):
            # Don't forward availabililty actions as reactors don't support them
            self._debug(f"skipping reactor (availability action with forward_action)")
            node.set_result(message="Skipped, availability action with forward_action")

        else:
            self._debug(f"dispatching reaction: {format_data(entity=reaction.entity, type=reaction.type, action=reaction.action, overwrite=self._reactor.overwrite, reset_workflow=self._reactor.reset_workflow)}")
            self._hass.bus.async_fire(EVENT_REACT_REACTION, vars(reaction))
            node.set_result(reaction=reaction.to_trace_result())