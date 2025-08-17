from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Dict

from .base import Node, Entity

if TYPE_CHECKING:
    from psim.core import Simulation


class Router(Node):
    """
    Routes entities to one of several downstream nodes based on a logic function.
    """
    def __init__(self, name: str, routing_logic: Callable[[Entity], str]):
        """
        Initializes the Router.

        Args:
            name: The name of the router node.
            routing_logic: A function that takes an Entity and returns the
                           name of the downstream node it should be sent to.
        """
        super().__init__(name)
        self.routing_logic = routing_logic
        self.routes: Dict[str, Node] = {}

    def connect(self, node: Node):
        """
        Connects a downstream node to this router.
        The node's name is used as the key for routing.

        Args:
            node: The downstream node to connect.
        """
        if node.name in self.routes:
            print(f"WARNING: Route name '{node.name}' already exists in {self.name}. It will be overwritten.")
        self.routes[node.name] = node
        return self # Return self to allow chaining .connect() calls

    def put(self, entity: Entity):
        """
        Receives an entity, uses the routing logic to determine the destination,
        and passes the entity to the chosen downstream node.
        """
        if not self.routes:
            if self.tracer:
                self.tracer.log(self.sim.now, f"WARNING: {self.name} has no routes. Entity {entity.name} was destroyed.")
            return

        destination_name = self.routing_logic(entity)

        if destination_name not in self.routes:
            if self.tracer:
                self.tracer.log(self.sim.now, f"ERROR: {self.name} routing logic returned invalid destination '{destination_name}' for {entity.name}. Entity was destroyed.")
            return

        destination_node = self.routes[destination_name]

        if self.tracer:
            self.tracer.log_entity_moved(self.sim.now, entity, self, destination_node)

        # Schedule the arrival at the next component to happen instantaneously.
        self.sim.schedule(action=lambda: destination_node.put(entity), delay=0)
