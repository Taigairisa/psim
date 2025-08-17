from psim import Model, connect
from psim.blocks import Source, Process, Sink
from psim.dists import Constant

def test_simple_sps_model():
    """
    Tests a simple Source -> Process -> Sink model with deterministic times.
    - Source creates an entity every 10 time units.
    - Process takes 15 time units to serve an entity.
    """
    # 1. Define the model
    # Run until just after the third entity is expected to finish
    m = Model(until=55.0, seed=1)

    # 2. Define components
    source = Source(
        name="Source",
        interarrival_dist=Constant(10),
    )
    process = Process(
        name="Processor",
        service_dist=Constant(15),
    )
    sink = Sink(name="Sink")

    # 3. Wire them up
    connect(source, process)
    connect(process, sink)
    m.register(source, process, sink)

    # 4. Run the simulation
    m.run()

    # 5. Assert results
    # Time: Event
    # 10:   Source generates E1. E1 arrives at Process. Process starts service.
    #       (Process will be free at 10 + 15 = 25)
    # 20:   Source generates E2. E2 arrives at Process. Process is busy. E2 waits in queue.
    # 25:   Process finishes E1. E1 sent to Sink. Process pulls E2 from queue and starts service.
    #       (Process will be free at 25 + 15 = 40)
    # 30:   Source generates E3. E3 arrives at Process. Process is busy. E3 waits in queue.
    # 40:   Process finishes E2. E2 sent to Sink. Process pulls E3 from queue and starts service.
    #       (Process will be free at 40 + 15 = 55)
    # 50:   Source would generate E4, but we run until 55.
    # 55:   Process finishes E3. E3 sent to Sink. Simulation ends.

    # The sink should have received 3 entities
    assert sink.entities_received == 3

    # The final entity should have arrived at the sink at t=55
    assert sink.last_arrival_time == 55.0

    # The simulation should have ended exactly at the 'until' time
    assert m._sim.now == 55.0
