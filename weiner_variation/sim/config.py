import numpy as np

SAMPLE_COUNT = 10

FIELDS = {}

SEED = 38945729345645209345

SIMS = ["nominal", "input", "durations"]
SIMS_STDS = ["temperature", "diameter"]

from papermill.translators import (
    papermill_translators,
    PythonTranslator,
)

papermill_translators.register("coconut", PythonTranslator)
