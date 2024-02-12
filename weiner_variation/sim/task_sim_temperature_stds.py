import subprocess

import pytask
from pathlib import Path

from weiner_variation.config import DATA_DIR
from weiner_variation.sim.process import TEMPERATURE

FACTORS = [0.01, 0.02, 0.05, 0.1]

for f in FACTORS:
    @pytask.mark.task(id=f)
    @pytask.mark.depends_on(["sim_input.ipynb", "config.py", "process.py"])
    @pytask.mark.produces(DATA_DIR / "sim_temperature_stds_results" / f"{f}.csv")
    def task_sim_temperature_stds(depends_on: dict[..., Path], produces: Path, factor=f):
        result = subprocess.run(
            [
                "hatch",
                "run",
                "sim:papermill",
                "--language", "python",
                "--stdout-file", str(depends_on[0].with_suffix(".log")),
                str(depends_on[0]),
                str(depends_on[0].with_suffix(".out.ipynb")),
                "-p", "OUTPUT_FILENAME", str(produces),
                "-p", "TEMPERATURE_STD", str(factor * TEMPERATURE),
            ]
        )

        result.check_returncode()
