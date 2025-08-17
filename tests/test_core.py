import pytest
from psim.core import Simulation, Event, FEL

# This import is for the fixture to reset the counter
from psim import core as psim_core

@pytest.fixture(autouse=True)
def reset_globals():
    """Resets any global counters before each test for test isolation."""
    psim_core._event_seq_counter = 0

def test_fel_ordering():
    fel = FEL()

    # Events are ordered by: 1. timestamp, 2. priority, 3. sequence number.
    # We create them in a non-trivial order to test this.
    action = lambda: None
    e_t10_p1_s1 = Event(timestamp=10, priority=1, action=action) # Will have seq=0
    e_t5_p1_s0 = Event(timestamp=5, priority=1, action=action)   # Will have seq=1
    e_t10_p0_s2 = Event(timestamp=10, priority=0, action=action) # Will have seq=2
    e_t10_p1_s3 = Event(timestamp=10, priority=1, action=action) # Will have seq=3

    # Schedule out of order
    fel.schedule(e_t10_p1_s1)
    fel.schedule(e_t5_p1_s0)
    fel.schedule(e_t10_p0_s2)
    fel.schedule(e_t10_p1_s3)

    # Expected pop order:
    # 1. e_t5_p1_s0 (lowest timestamp)
    # 2. e_t10_p0_s2 (same timestamp as others, but higher priority (lower number))
    # 3. e_t10_p1_s1 (same time/priority as next, but lower seq number)
    # 4. e_t10_p1_s3 (last)
    assert fel.pop_next() == e_t5_p1_s0
    assert fel.pop_next() == e_t10_p0_s2
    assert fel.pop_next() == e_t10_p1_s1
    assert fel.pop_next() == e_t10_p1_s3
    assert fel.is_empty

def test_simulation_run():
    sim = Simulation()

    # A list to record the order of events
    event_log = []

    # Schedule three events
    sim.schedule(action=lambda: event_log.append("A"), at=10)
    sim.schedule(action=lambda: event_log.append("B"), at=5)
    sim.schedule(action=lambda: event_log.append("C"), delay=15) # scheduled at t=0+15=15

    sim.run(until=20)

    # Check that events were executed in the correct order
    assert event_log == ["B", "A", "C"]

    # Check that simulation time advanced correctly
    assert sim.now == 20

def test_simulation_run_stops_at_until():
    sim = Simulation()
    event_log = []
    sim.schedule(action=lambda: event_log.append(1), at=10)
    sim.schedule(action=lambda: event_log.append(2), at=20)

    sim.run(until=15)

    assert event_log == [1] # Only the first event should have run
    assert sim.now == 15   # Time should be exactly `until`

def test_schedule_in_past_raises_error():
    sim = Simulation()
    sim.now = 10
    with pytest.raises(ValueError, match="Cannot schedule an event in the past"):
        sim.schedule(action=lambda: None, at=5)

    with pytest.raises(ValueError, match="Delay cannot be negative"):
        sim.schedule(action=lambda: None, delay=-5)

def test_schedule_requires_at_or_delay():
    sim = Simulation()
    with pytest.raises(ValueError, match="Either 'at' or 'delay' must be specified"):
        sim.schedule(action=lambda: None)

    with pytest.raises(ValueError, match="Either 'at' or 'delay' must be specified"):
        sim.schedule(action=lambda: None, at=10, delay=5)
