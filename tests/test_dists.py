import random
import pytest
from psim.dists import Exponential, Triangular, Constant

def test_constant_dist():
    dist = Constant(value=123.45)
    assert dist.sample() == 123.45
    assert dist.sample() == 123.45

def test_exponential_dist():
    dist = Exponential(mean=10.0)
    # Just check that it returns a float and doesn't crash
    assert isinstance(dist.sample(), float)

def test_triangular_dist():
    dist = Triangular(low=5, high=15, mode=10)
    sample = dist.sample()
    assert isinstance(sample, float)
    assert 5 <= sample <= 15

def test_reproducibility_with_seed():
    # Create a seeded random number generator
    rng1 = random.Random(42)
    dist1 = Exponential(mean=10, rng=rng1)
    samples1 = [dist1.sample() for _ in range(10)]

    # Create another identical generator
    rng2 = random.Random(42)
    dist2 = Exponential(mean=10, rng=rng2)
    samples2 = [dist2.sample() for _ in range(10)]

    assert samples1 == samples2

def test_exponential_invalid_mean():
    with pytest.raises(ValueError, match="Mean must be positive"):
        Exponential(mean=0)
    with pytest.raises(ValueError, match="Mean must be positive"):
        Exponential(mean=-10)

def test_triangular_invalid_params():
    with pytest.raises(ValueError, match="Constraints not met"):
        # mode > high
        Triangular(low=5, high=10, mode=11)
    with pytest.raises(ValueError, match="Constraints not met"):
        # low > mode
        Triangular(low=6, high=10, mode=5)
