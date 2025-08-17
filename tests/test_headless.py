import pytest
from psim import Model, connect
from psim.blocks import Source, Process, Sink
from psim.dists import Constant
import psim.viewer.main

def test_viewer_import_and_launch_without_pyside6():
    """
    Tests that importing and attempting to launch the viewer does not crash
    if PySide6 is not installed.
    """
    # In a headless environment, the HAVE_PYSIDE6 flag should be False.
    # Note: This test will fail if PySide6 is actually in the environment.
    # We rely on the test runner environment being minimal.
    assert not psim.viewer.main.HAVE_PYSIDE6, "This test requires PySide6 to be uninstalled."

    # Attempting to launch the viewer should not raise an error.
    # It should just print a message and return.
    try:
        psim.viewer.main.launch_viewer(model=None)
    except Exception as e:
        pytest.fail(f"launch_viewer() raised an unexpected exception: {e}")


def test_simple_model_runs_in_headless_mode():
    """
    Tests that a simple Source -> Process -> Sink model can run without
    any GUI components available.
    """
    # 1. Define the model
    m = Model(until=30.0)

    # 2. Define components
    source = Source(name="Source", interarrival_dist=Constant(10))
    process = Process(name="Processor", service_dist=Constant(5))
    sink = Sink(name="Sink")

    # 3. Wire them up
    connect(source, process)
    connect(process, sink)
    m.register(source, process, sink)

    # 4. Run the simulation
    m.run()

    # 5. Assert results
    # Time: Event
    # 10: Source generates E1 -> Process starts E1 (ends at 15)
    # 15: Process finishes E1 -> Sink receives E1
    # 20: Source generates E2 -> Process starts E2 (ends at 25)
    # 25: Process finishes E2 -> Sink receives E2
    # 30: Source generates E3 -> Process starts E3 (ends at 35)
    #    Simulation ends at 30. E3 is processed but not finished.
    assert sink.entities_received == 2
    assert sink.last_arrival_time == 25.0
    assert m._sim.now == 30.0
