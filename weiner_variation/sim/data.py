from dataclasses import dataclass
import numpy as np
import pyroll.core as pr


@dataclass
class DrawInput:
    diameter: float
    temperature: float


@dataclass
class DrawDurations(DrawInput):
    durations: np.ndarray
