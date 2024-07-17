SAMPLE_COUNT = 10

SEED = 38945729345645209345

SIMS = ["nominal", "input", "durations"]
SIMS_STDS = ["temperature", "diameter"]

from papermill.translators import (
    PythonTranslator,
    papermill_translators,
)

papermill_translators.register("coconut", PythonTranslator)
