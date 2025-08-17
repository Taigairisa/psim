import sys
import sys
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsLineItem,
)
from PySide6.QtGui import QBrush, QPen, QColor

class SimulationThread(QThread):
    """A QThread that runs the simulation in the background."""
    simulation_finished = Signal()

    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        self.model.run()
        self.simulation_finished.emit()


class ViewerWindow(QMainWindow):
    def __init__(self, model=None):
        super().__init__()
        self.model = model
        self.setWindowTitle("psim Viewer")

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Graphics view for the simulation model
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        main_layout.addWidget(self.view)

        # Control buttons
        controls_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        self.setGeometry(100, 100, 800, 600)
        self.thread = None

        # Connect signals to slots
        self.start_button.clicked.connect(self.start_simulation)
        # self.stop_button.clicked.connect(self.stop_simulation)

        self.entity_items = {} # To store entity graphics items {entity_id: item}
        self.node_items = {}   # To store node graphics items {node_name: item}

        # Connect to the tracer if a model is provided
        if self.model:
            if self.model.tracer:
                self.model.tracer.message_logged.connect(self.update_log)
                self.model.tracer.node_state_changed.connect(self.on_node_state_changed)
                self.model.tracer.entity_created.connect(self.on_entity_created)
                self.model.tracer.entity_moved.connect(self.on_entity_moved)
                self.model.tracer.entity_destroyed.connect(self.on_entity_destroyed)
            self.draw_model()

    def draw_model(self):
        """Draws the static components of the model (nodes and connections)."""
        if not self.model:
            return

        node_items = {}
        # First, draw all nodes
        for node in self.model.nodes:
            if node.pos:
                x, y = node.pos
                rect_item = QGraphicsRectItem(x, y, 100, 50)
                rect_item.setBrush(QBrush(QColor("lightblue")))
                self.scene.addItem(rect_item)

                text_item = QGraphicsTextItem(node.name)
                text_item.setPos(x, y)
                self.scene.addItem(text_item)
                node_items[node.name] = rect_item

        # Second, draw all connections
        for node in self.model.nodes:
            if node.out and node.name in node_items and node.out.name in node_items:
                from_item = node_items[node.name]
                to_item = node_items[node.out.name]

                line = QGraphicsLineItem(
                    from_item.rect().right(),
                    from_item.rect().center().y(),
                    to_item.rect().left(),
                    to_item.rect().center().y()
                )
                line.setPen(QPen(Qt.black, 2))
                self.scene.addItem(line)


    def start_simulation(self):
        """Creates and starts the simulation thread."""
        if not self.model:
            print("No model to simulate.")
            return

        self.thread = SimulationThread(self.model)
        self.thread.simulation_finished.connect(self.on_simulation_finished)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.thread.start()
        print("Simulation thread started.")

    def on_simulation_finished(self):
        """Called when the simulation thread is finished."""
        print("Simulation thread finished.")
        self.thread = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_log(self, timestamp, message):
        """A slot to receive log messages from the tracer."""
        print(f"[GUI Log] {timestamp:.2f}: {message}")

    def on_node_state_changed(self, timestamp, node_name, state):
        """Slot to handle node state changes."""
        if node_name in self.node_items:
            item = self.node_items[node_name]
            busy_units = state.get("busy", 0)
            if busy_units > 0:
                item.setBrush(QBrush(QColor("salmon")))
            else:
                item.setBrush(QBrush(QColor("lightblue")))

            # Update a tooltip or text item with queue length etc.
            queued = state.get("queued", 0)
            item.setToolTip(f"Busy: {busy_units}\nQueued: {queued}")

    def on_entity_created(self, timestamp, entity_id, entity_name, node_name):
        """Slot to handle entity creation."""
        if node_name in self.node_items:
            node_item = self.node_items[node_name]
            entity_item = QGraphicsEllipseItem(0, 0, 10, 10)
            entity_item.setBrush(QBrush(QColor("green")))
            entity_item.setPos(node_item.rect().center())
            self.scene.addItem(entity_item)
            self.entity_items[entity_id] = entity_item

    def on_entity_moved(self, timestamp, entity_id, from_node_name, to_node_name):
        """Slot to handle entity movement (currently instant)."""
        if entity_id in self.entity_items and to_node_name in self.node_items:
            entity_item = self.entity_items[entity_id]
            to_node_item = self.node_items[to_node_name]
            # Here you would normally run a QPropertyAnimation for smooth movement.
            # For a simple version, we just move it instantly.
            entity_item.setPos(to_node_item.rect().center())

    def on_entity_destroyed(self, timestamp, entity_id, node_name):
        """Slot to handle entity destruction."""
        if entity_id in self.entity_items:
            entity_item = self.entity_items.pop(entity_id)
            self.scene.removeItem(entity_item)
            del entity_item

    def stop_simulation(self):
        print("Stop button clicked!")
        # To be implemented...

def launch_viewer(model):
    """Entry point for launching the GUI."""
    app = QApplication(sys.argv)
    window = ViewerWindow(model=model)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # This allows running the viewer standalone for testing
    app = QApplication(sys.argv)
    window = ViewerWindow()
    window.show()
    sys.exit(app.exec())
