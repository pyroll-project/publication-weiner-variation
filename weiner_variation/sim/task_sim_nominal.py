import subprocess

import pytask
from pathlib import Path

from weiner_variation.config import DATA_DIR


@pytask.mark.task()
@pytask.mark.depends_on(["sim_nominal.ipynb", "config.py", "process.py"])
@pytask.mark.produces(DATA_DIR / "sim_nominal_results.csv")
def task_sim_nominal(depends_on: dict[..., Path]):
    result = subprocess.run(
        [
            "papermill",
            "--language", "python",
            "--stdout-file", str(depends_on[0].with_suffix(".log")),
            str(depends_on[0]),
            str(depends_on[0].with_suffix(".out.ipynb"))
        ]
    )

    result.check_returncode()

