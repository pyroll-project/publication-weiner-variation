import matplotlib.pyplot as plt
import pandas as pd

from weiner_variation.config import IMG_DIR, MATERIAL, ROOT_DIR
from weiner_variation.data.config import PASSES_FILES, RAW_DATA_FILES

FILE_STEM = "plot_timeline_pass_finding"
FILE_TYPES = ["png", "svg", "pdf"]

INDEX = 1


def task_plot_timeline_pass_finding(
    raw_data_file=RAW_DATA_FILES[MATERIAL][INDEX],
    passes_file=PASSES_FILES[MATERIAL][INDEX],
    config=ROOT_DIR / "config.py",
    produces=[IMG_DIR / f"{FILE_STEM}.{t}" for t in FILE_TYPES],
):
    fig: plt.Figure = plt.figure(figsize=(6.4, 2.5), dpi=600, layout="constrained")
    ax: plt.Axes = fig.add_subplot()

    passes = pd.read_csv(passes_file, header=[0], index_col=0)
    passes.infer_objects()
    passes.start = pd.to_datetime(passes.start)
    passes.mid = pd.to_datetime(passes.mid)
    passes.end = pd.to_datetime(passes.end)

    raw_data: pd.DataFrame = pd.read_csv(raw_data_file, header=0, index_col=0)
    raw_data.index = pd.to_datetime(raw_data.index)
    raw_data = raw_data.resample("10ms").mean()[passes.start["R1"] - pd.Timedelta("10s") : passes.start["F1"]]

    zero = raw_data.index[0]

    def to_seconds(data):
        return (data - zero).map(lambda self: self.total_seconds())

    raw_data.index = to_seconds(raw_data.index)
    passes.start = to_seconds(passes.start)
    passes.mid = to_seconds(passes.mid)
    passes.end = to_seconds(passes.end)

    raw_data["roll_torque_duo"].plot(ax=ax, label="Roll Torque Signal", lw=1, c="k")

    spans = [ax.axvspan(p.start, p.end, alpha=0.5, fc="C0") for p in passes["R1":"R10"].itertuples()]
    spans[0].set_label("Passes")

    mids = [ax.axvline(p.mid, ls="--", lw=1, c="C0") for p in passes["R1":"R10"].itertuples()]
    mids[0].set_label("Middles")

    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time $\\Duration$ in \\unit{{\\second}}")
    ax.set_ylabel("Roll Torque $\\RollTorque$ in \\unit{\\kilo\\newton\\meter}")

    for f in produces:
        fig.savefig(f)

    plt.close(fig)
