from dataclasses import dataclass

import numpy as np


@dataclass
class DrawInput:
    diameter: float
    temperature: float


@dataclass
class DrawDurations(DrawInput):
    durations: np.ndarray
