import json
import subprocess

import pytask
from pathlib import Path

from weiner_variation.config import DATA_DIR


@pytask.mark.task()
@pytask.mark.depends_on(["sim_input.ipynb", DATA_DIR / "input_dist.csv", "config.py", "process.py"])
@pytask.mark.produces(DATA_DIR / "sim_input_results.csv")
def task_sim_input(depends_on: dict[..., Path]):
    result = subprocess.run(
        [
            "hatch",
            "run",
            "sim:papermill",
            "-l", "python",
            "--stdout-file", str(depends_on[0].with_suffix(".log")),
            str(depends_on[0]),
            str(depends_on[0].with_suffix(".out.ipynb"))
        ]
    )

    result.check_returncode()
