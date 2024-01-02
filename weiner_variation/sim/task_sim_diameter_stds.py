import subprocess

import pytask
from pathlib import Path

from weiner_variation.config import DATA_DIR
from weiner_variation.sim.process import DIAMETER_STD

FACTORS = [0.2, 0.5, 1, 2, 4]

for f in FACTORS:
    @pytask.mark.task(id=f)
    @pytask.mark.depends_on(["sim_input.ipynb", "config.py", "process.py"])
    @pytask.mark.produces(DATA_DIR / "sim_diameter_stds_results" / f"{f}.csv")
    def task_sim_diameter_stds(depends_on: dict[..., Path], produces: Path, factor=f):
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
                "-p", "DIAMETER_STD", str(factor * DIAMETER_STD),
            ]
        )

        result.check_returncode()
