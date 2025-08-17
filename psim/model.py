from __future__ import annotations
import random

from psim.core import Simulation
from psim.blocks.base import Node, reset_entity_counter
from psim.blocks.source import Source
from psim.tracer import Tracer


def connect(from_node: Node, to_node: Node):
    """
    Connects two nodes together in sequence.
    """
    if from_node.out is not None:
        print(f"WARNING: Node {from_node.name} already has an output connection. It will be overwritten.")
    from_node.out = to_node


class Model:
    """
    A container for a simulation model. It holds the components,
    simulation engine, and run parameters.
    """
    def __init__(self, until: float, seed: int | None = None, warmup: float = 0.0):
        self._sim = Simulation()
        self.until = until
        self.warmup = warmup
        self.seed = seed
        self.nodes: list[Node] = []
        self.tracer = Tracer()

    def register(self, *nodes: Node):
        """
        Registers simulation nodes with the model, injecting the simulation
        environment and tracer into them.
        """
        for node in nodes:
            node.sim = self._sim
            node.tracer = self.tracer
            self.nodes.append(node)

    def run(self):
        """
        Runs the simulation.
        """
        # --- Setup before run ---
        # Seed the random number generator for reproducibility
        if self.seed is not None:
            random.seed(self.seed)

        # Reset global counters to ensure run is independent
        reset_entity_counter()

        print("--- Simulation starting ---")
        # Call start() on all nodes that have it (especially Sources)
        for node in self.nodes:
            # We only need to explicitly start Sources
            if isinstance(node, Source):
                node.start()

        self._sim.run(until=self.until)
        print(f"--- Simulation finished at time {self._sim.now:.2f} ---")
