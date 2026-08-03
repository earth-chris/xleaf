"""Methods for generating random parameter samples"""

from __future__ import annotations

import abc

import numpy as np


class BaseSampler(abc.ABC):
    """Base class for creating random samples of leaf/canopy parameters."""

    def __init__(
        self,
        seed: int | None = None,
        min: float | None = None,
        max: float | None = None,
        mean: float | None = None,
        stdv: float | None = None,
    ):
        """Create a generic random sampler class. Designed to be extended."""
        self.generator = np.random.default_rng(seed=seed)
        self.seed = seed
        self.min = min
        self.max = max
        self.mean = mean
        self.stdv = stdv

    @abc.abstractmethod
    def sample(self) -> float:
        """Return a single random sample. Implemented by the subclass."""


class UniformSampler(BaseSampler):
    """Uniform random sample generator."""

    def __init__(self, min: float, max: float, seed: int | None = 2017):
        """Generate a uniform random sampler from a range of values.

        Args:
            min: the minimum value to include in sampling.
            max: the maximum value to include in sampling.
            seed: set the seed for consistent random number generation.

        Example:
            >>> us = xleaf.samplers.UniformSampler(5, 10)
            >>> us.sample()
            9.709636474059744
        """
        super().__init__(min=min, max=max, seed=seed)

    def sample(self) -> float:
        """Return a uniform random sample drawn from the min/max range."""
        assert self.min is not None and self.max is not None
        return self.generator.uniform(self.min, self.max)


class NormalSampler(BaseSampler):
    """Generate normally distributed random samples."""

    def __init__(
        self,
        mean: float,
        stdv: float,
        min: float | None = None,
        max: float | None = None,
        seed: int | None = 2017,
    ):
        """Generate a normal random sampler from a parameterized distribution.

        Args:
            mean: the center of the distribution.
            stdv: the spread of the distribution. must be >= 0.
            min: the minimum value to include in sampling.
            max: the maximum value to include in sampling.
                both min and max must be set if either are set.
            seed: set the seed for consistent random number generation.

        Example:
            >>> ns = xleaf.samplers.NormalSampler(4, 2, min=0.2, max=10)
            >>> ns.sample()
            6.751017489983783
        """
        super().__init__(mean=mean, stdv=stdv, min=min, max=max, seed=seed)

    def sample(self) -> float:
        """Return a random sample drawn from a normal distribution.

        If min and max are set, samples outside the range are rejected and
        redrawn.
        """
        assert self.mean is not None and self.stdv is not None
        rnd = self.generator.normal(self.mean, self.stdv)

        if self.min is not None and self.max is not None:
            while rnd < self.min or rnd > self.max:
                rnd = self.generator.normal(self.mean, self.stdv)

        return rnd
