import subprocess

import pytask
from pathlib import Path

from weiner_variation.config import DATA_DIR


@pytask.mark.task()
@pytask.mark.depends_on(["sim_input.py", DATA_DIR / "input_dist.csv", "config.py", "process.py"])
@pytask.mark.produces(DATA_DIR / "sim_input_results.csv")
def task_sim_input(depends_on: Path, produces: Path):
    result = subprocess.run(
        [
            "hatch",
            "run",
            "sim_base:python",
            "-m", "weiner_variation.sim.sim_input",
            "-i", str(depends_on[1]),
            "-o", str(produces),
            "-p",
            ",".join([
                "basic",
            ]),
        ]
    )

    result.check_returncode()
