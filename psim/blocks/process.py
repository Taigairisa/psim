from __future__ import annotations
from typing import TYPE_CHECKING
from collections import deque
import functools

from .base import Node, Entity
from psim.dists import Distribution

if TYPE_CHECKING:
    from psim.core import Simulation


class Process(Node):
    """
    Represents a service station with a queue.
    """
    def __init__(
        self,
        name: str,
        service_dist: Distribution,
        capacity: int = 1,
    ):
        super().__init__(name)
        self.service_dist = service_dist
        self.capacity = capacity
        self.queue = deque()
        self.busy_units = 0

    def _log_state(self):
        if self.tracer:
            state = {"busy": self.busy_units, "queued": len(self.queue)}
            self.tracer.log_node_state(self.sim.now, self.name, state)

    def put(self, entity: Entity):
        """An entity arrives at the process block."""
        if self.tracer:
            self.tracer.log(self.sim.now, f"{entity.name} arrived at {self.name}")

        if self.busy_units < self.capacity:
            self._start_service(entity)
        else:
            self.queue.append(entity)

        self._log_state()

    def _start_service(self, entity: Entity):
        """Starts the service for a given entity."""
        self.busy_units += 1
        if self.tracer:
            self.tracer.log(self.sim.now, f"{entity.name} started service at {self.name}")
        self._log_state()

        service_time = self.service_dist.sample()

        finish_action = functools.partial(self._finish_service, entity=entity)
        self.sim.schedule(action=finish_action, delay=service_time)

    def _finish_service(self, entity: Entity):
        """Finishes the service for a given entity."""
        self.busy_units -= 1
        if self.tracer:
            self.tracer.log(self.sim.now, f"{entity.name} finished service at {self.name}")

        self.pass_to_next(entity)

        if self.queue:
            next_entity = self.queue.popleft()
            self._start_service(next_entity)

        self._log_state()
