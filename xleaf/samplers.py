"""Methods for generating random parameter samples"""

from typing import Callable

import numpy as np


class BaseSampler:
    """Base class for creating random samples of leaf/canopy parameters."""

    generator: Callable
    seed: int
    min: float
    max: float
    mean: float
    stdv: float

    def __init__(self, seed: int = None, min: float = None, max: float = None, mean: float = None, stdv: float = None):
        """Create a generic random sampler class. Designed to be extended."""
        generator = np.random.default_rng(seed=seed)
        self.generator = generator
        self.seed = seed
        self.min = min
        self.max = max
        self.mean = mean
        self.stdv = stdv

    @classmethod
    def sample(self, **kwargs) -> float:
        """Placeholder for the method implemented by the subclass."""
        pass


class UniformSampler(BaseSampler):
    """Uniform random sample generator."""

    def __init__(self, min: float, max: float, seed: int = 2017):
        """Generate a uniform random sampler from a range of values.

        Args:
            min: the minimum value to include in sampling.
            max: the maximum value to include in sampling.
            seed: set the seed for consistent random number generation.

        Usage:
            us = xleaf.samplers.UniformSampler(5, 10)
            us.sample()
            >>> 9.709636474059744
        """
        super().__init__(min=min, max=max, seed=seed)

    def sample(self) -> float:
        """Return a uniform random sample drawn from the min/max range."""
        return self.generator.uniform(self.min, self.max)


class NormalSampler(BaseSampler):
    """Generate a normally distributed random samples"""

    def __init__(self, mean: float, stdv: float, min: float = None, max: float = None, seed: int = 2017):
        """Generate a normal random sampler from a parameterized distribution.

        Args:
            mean: the center of the distribution.
            stdv: the spread of the distribution. must be >= 0.
            min: the minimum value to include in sampling.
            max: the maximum value to include in sampling.
                both min and max must be set if either are set.
            seed: set the seed for consistent random number generation.

        Usage:
            ns = xleaf.samplers.NormalSampler(4, 2, min=0.2, max=10)
            ns.sample()
            >>> 6.751017489983783
        """
        super().__init__(mean=mean, stdv=stdv, min=min, max=max, seed=seed)

    def sample(self) -> float:
        """Return a random sample drawn from a normal distribution."""
        rnd = self.generator.normal(self.mean, self.stdv)

        if self.min is not None or self.max is not None:
            while rnd < self.min or rnd > self.max:
                rnd = self.generator.normal(self.mean, self.stdv)

        return rnd
