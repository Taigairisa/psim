import heapq
from dataclasses import dataclass, field
from typing import Callable

# A unique sequence number to ensure FIFO for events with the same timestamp and priority.
# This makes the simulation deterministic.
_event_seq_counter = 0

@dataclass(order=True)
class Event:
    """
    Represents an event in the simulation.
    Events are ordered by timestamp, then priority, then a sequence number.
    """
    timestamp: float
    # The function to call when the event is processed.
    action: Callable = field(compare=False)
    # Lower number means higher priority
    priority: int = field(default=0, compare=True)
    # A unique sequence number for stable sorting.
    seq: int = field(init=False, compare=True)

    def __post_init__(self):
        global _event_seq_counter
        self.seq = _event_seq_counter
        _event_seq_counter += 1


class FEL:
    """
    A Future Event List (FEL) implemented with a min-heap.
    It stores and retrieves events in chronological order.
    """
    def __init__(self):
        self._events: list[Event] = []

    def schedule(self, event: Event):
        """Adds an event to the FEL."""
        heapq.heappush(self._events, event)

    def pop_next(self) -> Event:
        """Removes and returns the next event from the FEL."""
        return heapq.heappop(self._events)

    @property
    def is_empty(self) -> bool:
        """Returns True if the FEL is empty."""
        return not self._events

    def __len__(self) -> int:
        return len(self._events)


class Simulation:
    """
    The main simulation orchestrator.
    Manages virtual time, the Future Event List (FEL), and the simulation run loop.
    """
    def __init__(self):
        self.now: float = 0.0
        self._fel = FEL()

    def schedule(self, action: Callable, at: float | None = None, delay: float | None = None, priority: int = 0):
        """
        Schedules a new event.

        Either `at` (absolute time) or `delay` (relative to `self.now`) must be provided.
        """
        if (at is None and delay is None) or (at is not None and delay is not None):
            raise ValueError("Either 'at' or 'delay' must be specified, but not both.")

        if delay is not None:
            if delay < 0:
                raise ValueError("Delay cannot be negative.")
            timestamp = self.now + delay
        else: # at is not None
            timestamp = at

        if timestamp < self.now:
            raise ValueError("Cannot schedule an event in the past.")

        event = Event(timestamp=timestamp, priority=priority, action=action)
        self._fel.schedule(event)

    def run(self, until: float | None = None):
        """
        Runs the simulation.

        :param until: The virtual time to run the simulation until. If None, runs forever
                      or until the FEL is empty.
        """
        # If no end time, run as long as there are events.
        if until is None:
            while not self._fel.is_empty:
                event = self._fel.pop_next()
                self.now = event.timestamp
                event.action()
            return

        # Run until the specified time.
        while not self._fel.is_empty:
            # Peek at the next event.
            next_event = self._fel._events[0]
            if next_event.timestamp > until:
                break

            event = self._fel.pop_next()
            self.now = event.timestamp
            event.action()

        # Advance time to the `until` mark after the last event is processed.
        self.now = until
