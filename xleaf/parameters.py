"""Model parameters and methods for generating random parameter samples"""

import numpy as np

wavelengths = (np.arange(2101) * 0.001) + 0.4
units = "micrometers"

LeafErectophile = (-1, 0)
LeafExtremophile = (0, 1)
LeafPlagiophile = (0, -1)
LeafPlanophile = (1, 0)
LeafSpherical = (-0.35, -0.15)
LeafUniform = (0, 0)
