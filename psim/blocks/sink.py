from __future__ import annotations
from typing import TYPE_CHECKING

from .base import Node, Entity

if TYPE_CHECKING:
    from psim.core import Simulation


class Sink(Node):
    """
    Represents the exit point of the model. Consumes entities.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.entities_received = 0
        self.last_arrival_time = 0.0

    def put(self, entity: Entity):
        """Receives an entity and removes it from the simulation."""
        self.entities_received += 1
        self.last_arrival_time = self.sim.now
        if self.tracer:
            self.tracer.log_entity_destroyed(self.sim.now, entity, self)
            self.tracer.log(self.sim.now, f"{self.name} received and destroyed {entity.name}")
