from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from psim.core import Simulation
    from psim.tracer import Tracer

# A global counter to ensure unique entity IDs.
_entity_counter = 0

def reset_entity_counter():
    """Resets the global entity counter. Useful for test isolation."""
    global _entity_counter
    _entity_counter = 0

@dataclass
class Entity:
    """Represents an entity moving through the simulation."""
    name: str
    creation_time: float
    attributes: dict = field(default_factory=dict)
    id: int = field(init=False)

    def __post_init__(self):
        global _entity_counter
        self.id = _entity_counter
        _entity_counter += 1

class Node(ABC):
    """Abstract base class for all simulation components (blocks)."""
    def __init__(self, name: str):
        self.sim: Simulation | None = None
        self.tracer: Tracer | None = None
        self.name = name
        self.out: Node | None = None # The next node in the sequence
        self.pos: tuple[int, int] | None = None # For viewer layout

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def start(self):
        """A hook for nodes to perform any setup at the start of the simulation run."""
        pass

    @abstractmethod
    def put(self, entity: Entity):
        """The main method for receiving an entity from an upstream node."""
        pass

    def pass_to_next(self, entity: Entity):
        """Helper method to pass an entity to the next connected node."""
        if self.out:
            if self.tracer:
                self.tracer.log_entity_moved(self.sim.now, entity, self, self.out)
            # Schedule the arrival at the next component to happen instantaneously.
            # This keeps the event trace clean and respects the event-driven paradigm.
            self.sim.schedule(action=lambda: self.out.put(entity), delay=0)
        else:
            if self.tracer:
                self.tracer.log_entity_destroyed(self.sim.now, entity, self)
                self.tracer.log(self.sim.now, f"{entity.name} finished at {self.name} and was destroyed.")
