from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from .base import Node, Entity
from psim.dists import Distribution

if TYPE_CHECKING:
    from psim.core import Simulation


class Source(Node):
    """
    Generates entities and introduces them into the simulation.
    """
    def __init__(
        self,
        name: str,
        interarrival_dist: Distribution,
        entity_name: str = "Entity",
        limit: int = float('inf'),
    ):
        super().__init__(name)
        self.interarrival_dist = interarrival_dist
        self.entity_name = entity_name
        self.limit = limit
        self.entities_created = 0

    def start(self):
        """Schedules the first entity generation."""
        if self.sim is None:
            raise RuntimeError("Simulation environment not set for Source node.")
        self.sim.schedule(action=self._generate_entity, delay=self.interarrival_dist.sample())

    def _generate_entity(self):
        """Generate a new entity and schedule the next arrival."""
        if self.entities_created < self.limit:
            self.entities_created += 1
            entity = Entity(
                name=f"{self.entity_name}-{self.entities_created}",
                creation_time=self.sim.now,
            )
            if self.tracer:
                self.tracer.log_entity_created(self.sim.now, entity, self)
                self.tracer.log(self.sim.now, f"{self.name} generated {entity.name}")

            self.pass_to_next(entity)

            # Schedule the next arrival
            next_arrival_delay = self.interarrival_dist.sample()
            self.sim.schedule(action=self._generate_entity, delay=next_arrival_delay)

    def put(self, entity: Entity):
        """Source blocks cannot receive entities."""
        raise RuntimeError(f"{self.name} is a Source and cannot receive entities.")
