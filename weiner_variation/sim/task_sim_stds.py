import subprocess

import pytask

from weiner_variation.config import DATA_DIR, SIM_DIR
from weiner_variation.sim import process
from weiner_variation.sim.config import SIMS_STDS

FACTORS = [0.01, 0.02, 0.05, 0.1]

for sim in SIMS_STDS:
    for f in FACTORS:

        @pytask.task(id=f"{sim}/{f}")
        def task_sim_stds(
            notebook_file=SIM_DIR / f"sim_input.ipynb",
            config_file=SIM_DIR / "config.py",
            process_file=SIM_DIR / "process.py",
            produces=DATA_DIR
            / f"sim_{sim}_stds_results"
            / f"{str(f).replace('.', '-')}.csv",
            factor=f,
            sim_key=sim.upper(),
        ):
            base_value = getattr(process, sim_key)

            result = subprocess.run(
                [
                    "papermill",
                    "--language",
                    "python",
                    "--stdout-file",
                    str(produces.with_suffix(".log")),
                    str(notebook_file),
                    str(notebook_file.with_suffix(".out.ipynb")),
                    "-p",
                    "OUTPUT_FILENAME",
                    str(produces),
                    "-p",
                    f"{sim_key}_STD",
                    str(factor * base_value),
                ]
            )

            result.check_returncode()
