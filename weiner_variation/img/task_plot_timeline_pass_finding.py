import pytask
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
from weiner_variation.config import DATA_DIR, ROOT_DIR
from weiner_variation.data.task_extract_pass_data import find_passes, PROMINENCE_DUO

FILE_STEM = "plot_timeline_pass_finding"
FILE_TYPES = ["png", "svg", "pdf"]


@pytask.mark.task()
@pytask.mark.depends_on([DATA_DIR / "raw_data" / "2022-09-26_01.csv", ROOT_DIR / "config.py"])
@pytask.mark.produces([f"{FILE_STEM}.{t}" for t in FILE_TYPES])
def task_plot_timeline_pass_finding(depends_on: Path, produces: dict[..., Path]):
    fig: plt.Figure = plt.figure(dpi=600)
    ax: plt.Axes = fig.add_subplot()

    raw_data: pd.DataFrame = pd.read_csv(depends_on[0], header=0, index_col=0)
    raw_data.index = pd.to_datetime(raw_data.index)
    raw_data = raw_data.resample("10ms").mean()["2022-09-26T11:23:15":"2022-09-26T11:24:13"]
    raw_data.index = (raw_data.index - raw_data.index[0]).map(lambda self: self.total_seconds())

    duo_passes = find_passes(raw_data["roll_torque_duo"], PROMINENCE_DUO)

    raw_data["roll_torque_duo"].plot(ax=ax, label="Roll Torque Signal", lw=1, c="k")

    spans = [
        ax.axvspan(p.start, p.end, alpha=0.5, fc="C0")
        for p in duo_passes.itertuples()
    ]
    spans[0].set_label("Passes")

    mids = [
        ax.axvline(p.mid, ls="--", lw=1, c="C0")
        for p in duo_passes.itertuples()
    ]
    mids[0].set_label("Middles")

    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time $\\Duration$ in \\unit{{\\second}}")
    ax.set_ylabel("Roll Torque $\\RollTorque$ in \\unit{\\kilo\\newton\\meter}")

    for f in produces.values():
        fig.savefig(f)

    plt.close(fig)
