import random

from psim import Model
from psim.blocks import Source, Process, Sink, Router
from psim.dists import Constant

# --- Define the routing logic ---
# This function will be passed to the Router instance.
# It receives an entity and must return the name of the destination node.
def routing_logic(entity):
    """Randomly chooses between 'Processor A' and 'Processor B'."""
    return random.choice(["Processor A", "Processor B"])

# --- Create the simulation model ---
m = Model(until=100.0, seed=42)

# --- Create simulation components ---
source = Source(
    name="Source",
    interarrival_dist=Constant(10),
)
router = Router(
    name="Router",
    routing_logic=routing_logic,
)
process_a = Process(
    name="Processor A",
    service_dist=Constant(15),
)
process_b = Process(
    name="Processor B",
    service_dist=Constant(30),
)
sink_a = Sink(name="Sink A")
sink_b = Sink(name="Sink B")

# --- Connect the components ---
# Standard `connect` for single-output nodes
from psim.model import connect
connect(source, router)
connect(process_a, sink_a)
connect(process_b, sink_b)

# The router has its own `.connect()` method for multiple outputs
router.connect(process_a).connect(process_b)

# --- Register all components with the model ---
m.register(
    source,
    router,
    process_a,
    process_b,
    sink_a,
    sink_b,
)
