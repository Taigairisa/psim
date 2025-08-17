import random
from abc import ABC, abstractmethod

class Distribution(ABC):
    """Abstract base class for all probability distributions."""
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random

    @abstractmethod
    def sample(self) -> float:
        """Returns a single sample from the distribution."""
        pass

class Exponential(Distribution):
    """Exponential distribution."""
    def __init__(self, mean: float, rng: random.Random | None = None):
        super().__init__(rng)
        if mean <= 0:
            raise ValueError("Mean must be positive for Exponential distribution.")
        # The parameter for Python's expovariate is 1/mean (the rate lambda).
        self.lambd = 1.0 / mean

    def sample(self) -> float:
        return self._rng.expovariate(self.lambd)

class Triangular(Distribution):
    """Triangular distribution."""
    def __init__(self, low: float, high: float, mode: float, rng: random.Random | None = None):
        super().__init__(rng)
        if not low <= mode <= high:
            raise ValueError("Constraints not met: low <= mode <= high.")
        self.low = low
        self.high = high
        self.mode = mode

    def sample(self) -> float:
        return self._rng.triangular(self.low, self.high, self.mode)


class Constant(Distribution):
    """Constant value distribution. Returns the same value for every sample."""
    def __init__(self, value: float, rng: random.Random | None = None):
        super().__init__(rng)
        self.value = value

    def sample(self) -> float:
        return self.value
