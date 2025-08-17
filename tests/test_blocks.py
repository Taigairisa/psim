import pytest
from unittest.mock import MagicMock

from psim.core import Simulation
from psim.model import connect
from psim.blocks import Source, Process, Buffer, Sink, Router
from psim.blocks.base import Entity, reset_entity_counter
from psim.dists import Constant

class TestSource:
    def test_source_creation(self):
        source = Source(name="S1", interarrival_dist=Constant(10))
        assert source.name == "S1"
        assert source.entities_created == 0

    def test_source_generates_entity(self):
        """Tests that a source generates an entity and passes it to the next block."""
        sim = Simulation()
        source = Source(name="S1", interarrival_dist=Constant(10))
        sink = Sink(name="Sink")

        # Setup connections and simulation environment
        connect(source, sink)
        source.sim = sim
        sink.sim = sim

        source.start()
        sim.run(until=15)

        assert source.entities_created == 1
        assert sink.entities_received == 1
        assert sink.last_arrival_time == 10.0
        # The next arrival is scheduled at t=20
        assert not sim._fel.is_empty
        assert sim._fel._events[0].timestamp == 20.0

    def test_source_reaches_limit(self):
        """Tests that a source stops generating entities when it reaches its limit."""
        sim = Simulation()
        source = Source(name="S1", interarrival_dist=Constant(10), limit=2)
        sink = Sink(name="Sink")

        connect(source, sink)
        source.sim = sim
        sink.sim = sim

        source.start()
        sim.run(until=50) # Run for long enough to generate more if not limited

        assert source.entities_created == 2
        assert sink.entities_received == 2
        assert sim._fel.is_empty

    def test_source_put_raises_error(self):
        """Tests that calling put() on a source raises a RuntimeError."""
        source = Source(name="S1", interarrival_dist=Constant(10))
        with pytest.raises(RuntimeError, match="S1 is a Source and cannot receive entities"):
            source.put(MagicMock())


class TestProcess:
    def test_process_creation(self):
        process = Process(name="P1", service_dist=Constant(5))
        assert process.name == "P1"
        assert process.capacity == 1
        assert process.busy_units == 0
        assert len(process.queue) == 0

    def test_single_entity_service(self):
        """Tests a single entity arriving at an idle process."""
        sim = Simulation()
        source = Source("S1", interarrival_dist=Constant(10), limit=1)
        process = Process("P1", service_dist=Constant(5))
        sink = Sink("Sink")

        connect(source, process)
        connect(process, sink)
        source.sim = sim
        process.sim = sim
        sink.sim = sim

        source.start()
        sim.run(until=20)

        assert process.busy_units == 0
        assert sink.entities_received == 1
        assert sink.last_arrival_time == 15.0

    def test_queuing_behavior(self):
        """Tests that entities queue up when the process is at capacity."""
        sim = Simulation()
        source = Source("S1", interarrival_dist=Constant(1), limit=2)
        process = Process("P1", service_dist=Constant(5), capacity=1)
        sink = Sink("Sink")

        connect(source, process)
        connect(process, sink)
        source.sim = sim
        process.sim = sim
        sink.sim = sim

        source.start()
        sim.run(until=12)

        assert sink.entities_received == 2
        assert sink.last_arrival_time == 11.0 # E1 arrives 1, served by 6. E2 arrives 2, starts service at 6, served by 11.
        assert process.busy_units == 0
        assert len(process.queue) == 0

    def test_multi_capacity(self):
        """Tests a process with a capacity greater than 1."""
        sim = Simulation()
        source = Source("S1", interarrival_dist=Constant(1), limit=3)
        process = Process("P1", service_dist=Constant(5), capacity=2)
        sink = Sink("Sink")

        connect(source, process)
        connect(process, sink)
        source.sim = sim
        process.sim = sim
        sink.sim = sim

        source.start()
        sim.run(until=10)

        # E1 arrives 1, finishes 6
        # E2 arrives 2, finishes 7
        # E3 arrives 3, queues, starts service at 6 (when E1 leaves), finishes 11
        assert sink.entities_received == 2 # At t=10, E1 and E2 have finished
        assert process.busy_units == 1 # E3 is still processing
        assert len(process.queue) == 0


class TestSink:
    def test_sink_receives_entity(self):
        sim = MagicMock()
        sim.now = 10.0
        sink = Sink("Sink")
        sink.sim = sim

        entity = MagicMock()
        entity.name = "E1"

        sink.put(entity)

        assert sink.entities_received == 1
        assert sink.last_arrival_time == 10.0

        sim.now = 25.5
        sink.put(entity)
        assert sink.entities_received == 2
        assert sink.last_arrival_time == 25.5


class TestBuffer:
    def test_buffer_pass_through(self):
        """Tests that an entity passes through a buffer with available capacity."""
        sim = Simulation()
        sim.now = 5.0 # Set current time
        buffer = Buffer("B1", capacity=1)
        sink = Sink("Sink")

        connect(buffer, sink)
        buffer.sim = sim
        sink.sim = sim

        entity = MagicMock()
        buffer.put(entity)

        # The put is scheduled, so we need to run the simulation for it to execute
        sim.run()

        assert len(buffer.content) == 0
        assert sink.entities_received == 1

    def test_buffer_capacity_limit(self):
        """Tests that a buffer rejects entities when at capacity."""
        sim = Simulation()
        sim.now = 5.0
        buffer = Buffer("B1", capacity=1)
        buffer.sim = sim

        entity1 = MagicMock(name="E1")
        entity2 = MagicMock(name="E2")

        # Manually prevent the buffer from passing the entity by not connecting it
        buffer.out = None

        # We also need to mock the schedule method to check what is passed to it,
        # but for this test, we can just check the content length.
        # This is because the pass_to_next is what schedules, and if there is no out,
        # it won't schedule anything.
        buffer.put(entity1)
        assert len(buffer.content) == 1

        # Now the buffer is conceptually full. Try to add another entity.
        buffer.put(entity2)

        # The entity should be rejected, and the content should not increase
        assert len(buffer.content) == 1


class TestRouter:
    def test_router_connect_and_routes(self):
        """Tests that the connect method correctly adds routes."""
        router = Router("R1", routing_logic=lambda e: "P1")
        process1 = Process("P1", service_dist=Constant(1))
        process2 = Process("P2", service_dist=Constant(1))

        router.connect(process1).connect(process2)

        assert len(router.routes) == 2
        assert router.routes["P1"] == process1
        assert router.routes["P2"] == process2

    def test_routing_logic(self):
        """Tests that the router sends entities to the correct destination."""
        sim = Simulation()
        # This logic function always returns 'P_A'
        logic = lambda entity: "P_A"
        router = Router("R1", routing_logic=logic)
        sink_a = Sink("P_A")
        sink_b = Sink("P_B")

        router.connect(sink_a).connect(sink_b)
        router.sim = sim
        sink_a.sim = sim
        sink_b.sim = sim

        entity = MagicMock()
        router.put(entity)
        sim.run()

        assert sink_a.entities_received == 1
        assert sink_b.entities_received == 0

    def test_invalid_destination(self):
        """Tests that the router handles an invalid destination from the logic function."""
        sim = Simulation()
        # This logic function returns a destination that does not exist
        logic = lambda entity: "P_C" # P_C is not a connected route
        router = Router("R1", routing_logic=logic)
        sink_a = Sink("P_A")

        router.connect(sink_a)
        router.sim = sim
        sink_a.sim = sim

        # We need a tracer to see the error message
        tracer = MagicMock()
        router.tracer = tracer

        reset_entity_counter()
        entity = Entity(name="E1", creation_time=0.0)
        router.put(entity)
        sim.run()

        assert sink_a.entities_received == 0
        tracer.log.assert_called_with(
            0.0,
            "ERROR: R1 routing logic returned invalid destination 'P_C' for E1. Entity was destroyed."
        )
