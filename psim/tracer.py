from PySide6.QtCore import QObject, Signal

class Tracer(QObject):
    """
    A QObject that emits signals for various simulation events.
    The viewer can connect to these signals to visualize the simulation.
    """

    # A generic signal for logging text messages.
    # Args: timestamp (float), message (str)
    message_logged = Signal(float, str)

    # Signal for when a node's state changes (e.g., busy, idle, queue length).
    # Args: timestamp (float), node_name (str), new_state (dict)
    node_state_changed = Signal(float, str, dict)

    # Signal for when an entity is created.
    # Args: timestamp (float), entity_id (int), entity_name (str), node_name (str)
    entity_created = Signal(float, int, str, str)

    # Signal for when an entity moves between nodes.
    # Args: timestamp (float), entity_id (int), from_node_name (str), to_node_name (str)
    entity_moved = Signal(float, int, str, str)

    # Signal for when an entity is destroyed.
    # Args: timestamp (float), entity_id (int), node_name (str)
    entity_destroyed = Signal(float, int, str)

    def __init__(self):
        super().__init__()

    def log(self, sim_time: float, message: str):
        """Emits a generic log message."""
        self.message_logged.emit(sim_time, message)

    def log_node_state(self, sim_time: float, node_name: str, state: dict):
        """Emits a signal about a node's state change."""
        self.node_state_changed.emit(sim_time, node_name, state)

    def log_entity_created(self, sim_time: float, entity, node):
        self.entity_created.emit(sim_time, entity.id, entity.name, node.name)

    def log_entity_moved(self, sim_time: float, entity, from_node, to_node):
        self.entity_moved.emit(sim_time, entity.id, from_node.name, to_node.name)

    def log_entity_destroyed(self, sim_time: float, entity, node):
        self.entity_destroyed.emit(sim_time, entity.id, node.name)
