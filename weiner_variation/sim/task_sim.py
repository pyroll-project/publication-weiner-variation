import subprocess

import pytask

from weiner_variation.config import DATA_DIR, SIM_DIR
from weiner_variation.sim.config import SIMS

for sim in SIMS:

    @pytask.task(id=sim)
    def task_sim(
        notebook=SIM_DIR / f"sim_{sim}.ipynb",
        config_file=SIM_DIR / "config.py",
        process_file=SIM_DIR / "process.py",
        produces=DATA_DIR / f"sim_{sim}_results.csv",
    ):
        result = subprocess.run(
            [
                "papermill",
                "--language",
                "python",
                "--stdout-file",
                str(produces.with_suffix(".log")),
                str(notebook),
                str(notebook.with_suffix(".out.ipynb")),
            ]
        )

        result.check_returncode()
