import subprocess

import pytask
from pathlib import Path

from weiner_variation.config import DATA_DIR


@pytask.mark.task()
@pytask.mark.depends_on([
    "sim_durations.py",
    DATA_DIR / "input_dist.csv",
    DATA_DIR / "duo_pauses_dist.csv",
    "config.py",
    "process.py",
])
@pytask.mark.produces(DATA_DIR / "sim_durations_results.csv")
def task_sim_durations():
    result = subprocess.run(
        [
            "hatch",
            "run",
            "sim:python",
            "-m", "weiner_variation.sim.sim_durations",
        ]
    )

    result.check_returncode()
