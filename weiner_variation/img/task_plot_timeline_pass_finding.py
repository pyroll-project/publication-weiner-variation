import pytask
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from weiner_variation.config import ROOT_DIR, MATERIAL
from weiner_variation.data.config import RAW_DATA_FILES, PASSES_FILES

FILE_STEM = "plot_timeline_pass_finding"
FILE_TYPES = ["png", "svg", "pdf"]

INDEX = 1

@pytask.mark.task()
@pytask.mark.depends_on([RAW_DATA_FILES[MATERIAL][INDEX], PASSES_FILES[MATERIAL][INDEX], ROOT_DIR / "config.py"])
@pytask.mark.produces([f"{FILE_STEM}.{t}" for t in FILE_TYPES])
def task_plot_timeline_pass_finding(depends_on: dict[..., Path], produces: dict[..., Path]):
    fig: plt.Figure = plt.figure(figsize=(6.4, 2.5), dpi=600)
    ax: plt.Axes = fig.add_subplot()

    passes = pd.read_csv(depends_on[1], header=[0], index_col=0)
    passes.infer_objects()
    passes.start = pd.to_datetime(passes.start)
    passes.mid = pd.to_datetime(passes.mid)
    passes.end = pd.to_datetime(passes.end)

    raw_data: pd.DataFrame = pd.read_csv(depends_on[0], header=0, index_col=0)
    raw_data.index = pd.to_datetime(raw_data.index)
    raw_data = raw_data.resample("10ms").mean()[passes.start["R1"] - pd.Timedelta("10s"):passes.start["F1"]]

    zero = raw_data.index[0]

    def to_seconds(data):
        return (data - zero).map(lambda self: self.total_seconds())

    raw_data.index = to_seconds(raw_data.index)
    passes.start = to_seconds(passes.start)
    passes.mid = to_seconds(passes.mid)
    passes.end = to_seconds(passes.end)

    raw_data["roll_torque_duo"].plot(ax=ax, label="Roll Torque Signal", lw=1, c="k")

    spans = [
        ax.axvspan(p.start, p.end, alpha=0.5, fc="C0")
        for p in passes["R1":"R10"].itertuples()
    ]
    spans[0].set_label("Passes")

    mids = [
        ax.axvline(p.mid, ls="--", lw=1, c="C0")
        for p in passes["R1":"R10"].itertuples()
    ]
    mids[0].set_label("Middles")

    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time $\\Duration$ in \\unit{{\\second}}")
    ax.set_ylabel("Roll Torque $\\RollTorque$ in \\unit{\\kilo\\newton\\meter}")

    for f in produces.values():
        fig.savefig(f)

    plt.close(fig)
