from __future__ import annotations
from typing import TYPE_CHECKING
from collections import deque

from .base import Node, Entity

if TYPE_CHECKING:
    from psim.core import Simulation


class Buffer(Node):
    """
    Represents a buffer or queue area in the simulation.

    In this initial push-based implementation, the buffer acts as a "gate".
    It has a capacity, but it does not hold entities for any length of time.
    It checks if an entity *could* enter, and if so, immediately passes it
    to the next component. True decoupling/blocking logic will be added later.
    """
    def __init__(self, name: str, capacity: int = float('inf')):
        super().__init__(name)
        self.capacity = capacity
        # The content queue is used to conceptually track items, even if they pass through.
        self.content = deque()

    def put(self, entity: Entity):
        """Receives an entity. If there is capacity, passes it to the next block."""
        if len(self.content) >= self.capacity:
            if self.tracer:
                self.tracer.log(self.sim.now, f"WARNING: {self.name} is full. Entity {entity.name} was rejected/dropped.")
            return

        if self.tracer:
            self.tracer.log(self.sim.now, f"{entity.name} entered {self.name}")

        self.content.append(entity)
        # In this simple push model, the buffer tries to pass the entity on immediately.
        self._try_pass_next()

    def _try_pass_next(self):
        """Tries to pass the next entity in the queue to the downstream block."""
        if self.content and self.out:
            entity_to_pass = self.content.popleft()
            if self.tracer:
                self.tracer.log(self.sim.now, f"{entity_to_pass.name} is leaving {self.name}")
            self.pass_to_next(entity_to_pass)
