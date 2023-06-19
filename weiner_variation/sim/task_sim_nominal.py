import subprocess

import pytask
from pathlib import Path


@pytask.mark.task()
@pytask.mark.depends_on(["sim_nominal.py", "config.py", "process.py"])
@pytask.mark.produces("report.html")
def task_sim_nominal(depends_on: Path, produces: Path):
    result = subprocess.run(
        [
            "hatch",
            "run",
            "sim:python",
            "-m", "weiner_variation.sim.sim_nominal",
        ]
    )

    result.check_returncode()
