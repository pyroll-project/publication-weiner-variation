import subprocess

import pytask
from pathlib import Path

from weiner_variation.config import DATA_DIR

FACTORS = [0.2, 0.5, 1, 2, 4]


@pytask.mark.depends_on(["sim_temperature_stds.py", DATA_DIR / "input_dist.csv", "config.py", "process.py"])
@pytask.mark.produces([
    DATA_DIR / "sim_temperature_stds_results" / f"{f}.csv"
    for f in FACTORS
])
def task_sim_temperature_stds(depends_on: Path, produces: Path):
    result = subprocess.run(
        [
            "hatch",
            "run",
            "sim:python",
            "-m", "weiner_variation.sim.sim_temperature_stds",
        ]
    )

    result.check_returncode()
