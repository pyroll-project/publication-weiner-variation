import papermill
import pytask

from weiner_variation.config import DATA_DIR, SIM_DIR
from weiner_variation.sim import process
from weiner_variation.sim.config import SIMS_STDS

FACTORS = [0.01, 0.02, 0.05]

for sim in SIMS_STDS:
    for f in FACTORS:

        @pytask.task(id=f"{sim}/{f}")
        def task_sim_stds(
            notebook_file=SIM_DIR / "sim_input.ipynb",
            config_file=SIM_DIR / "config.py",
            process_file=SIM_DIR / "process.py",
            produces=DATA_DIR / f"sim_{sim}_stds_results" / f"{f}.csv",
            factor=f,
            sim_key=sim.upper(),
        ):
            base_value = getattr(process, sim_key)

            papermill.execute_notebook(
                notebook_file,
                produces.with_suffix(".out.ipynb"),
                parameters={
                    "OUTPUT_FILENAME": str(produces),
                    f"{sim_key}_STD": factor * base_value,
                },
            )
