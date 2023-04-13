from contextlib import contextmanager

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytask
import pyroll.core as pr

from weiner_variation.config import SIM_DIR, IMG_DIR, DATA_DIR
from weiner_variation.data.config import PASSES_DIR
from weiner_variation.sim.process import PASS_SEQUENCE

PASSES = [u for u in PASS_SEQUENCE if isinstance(u, pr.RollPass)]

PASS_POSITIONS = np.arange(len(PASSES))
PASS_LABELS = [p.label for p in PASSES]

EXP_FILES = [PASSES_DIR / f"2022-09-26_0{i + 1}.csv" for i in range(4)]

FLIER = dict(
    marker="+",
    markersize="4"
)


def _reindex_in(data):
    data.index = PASS_POSITIONS - 0.25
    return data


def _reindex_out(data):
    data.index = PASS_POSITIONS + 0.25
    return data


def _load_sim_data(file):
    return pd.read_csv(file, index_col=0, header=[0, 1])


def _load_exp_data(files):
    return pd.concat(
        [pd.read_csv(f, index_col=0, header=0) for f in files.values()],
        keys=range(4), axis=1
    ).swaplevel(0, 1, axis=1)


@contextmanager
def _plot(files, figsize=None):
    fig: plt.Figure = plt.figure(figsize=figsize)
    ax: plt.Axes = fig.subplots()

    ax.set_xlabel("Roll Pass")
    ax.grid(True)

    yield fig, ax

    ax.xaxis.set_major_locator(plt.FixedLocator(range(len(PASSES))))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(PASS_LABELS))

    ax.legend()

    fig.tight_layout()
    for f in files.values():
        fig.savefig(f, dpi=300)

    plt.close(fig)


for sim in ["input", "elastic"]:
    @pytask.mark.task(id=sim)
    @pytask.mark.depends_on({"sim": DATA_DIR / f"sim_{sim}_results.csv", "exp": EXP_FILES})
    @pytask.mark.produces([
        IMG_DIR / f"{sim}_roll_force.{suffix}"
        for suffix in ["png", "pdf", "svg"]]
    )
    def task_plot_roll_force(produces, depends_on):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Roll Force in kN")
            ax.set_ylim(0, 400)

            ax.boxplot(df_sim.roll_force / 1e3, positions=PASS_POSITIONS, flierprops=FLIER)
            ax.bar(df_sim.roll_force.columns, df_sim.roll_force.loc[0] / 1e3, fill="C0", alpha=0.5, label="nominal")

            for c in df_exp["roll_force"].columns:
                artist = ax.scatter(df_exp["roll_force"].index, df_exp["roll_force"][c], marker="x", c="r", lw=1)
            artist.set_label("experimental")


    @pytask.mark.task(id=sim)
    @pytask.mark.depends_on({"sim": DATA_DIR / f"sim_{sim}_results.csv", "exp": EXP_FILES})
    @pytask.mark.produces([
        IMG_DIR / f"{sim}_roll_torque.{suffix}"
        for suffix in ["png", "pdf", "svg"]]
    )
    def task_plot_roll_torque(produces, depends_on):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Roll Torque in kNm")
            ax.set_ylim(0, 16)

            ax.boxplot(df_sim.roll_torque / 1e3, positions=PASS_POSITIONS, flierprops=FLIER)
            ax.bar(df_sim.roll_torque.columns, df_sim.roll_torque.loc[0] / 1e3, fill="C0", alpha=0.5, label="nominal")

            for c in df_exp["roll_torque"].columns:
                artist = ax.scatter(df_exp["roll_torque"].index, df_exp["roll_torque"][c], marker="x", c="r", lw=1)
            artist.set_label("experimental")


    @pytask.mark.task(id=sim)
    @pytask.mark.depends_on({"sim": DATA_DIR / f"sim_{sim}_results.csv", "exp": EXP_FILES})
    @pytask.mark.produces([
        IMG_DIR / f"{sim}_temperature.{suffix}"
        for suffix in ["png", "pdf", "svg"]]
    )
    def task_plot_temperature(produces, depends_on):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Workpiece Temperature in K")
            ax.set_ylim(1050, 1550)

            ax.boxplot(df_sim.in_temperature, positions=PASS_POSITIONS - 0.25, widths=0.25, flierprops=FLIER)
            ax.boxplot(df_sim.out_temperature, positions=PASS_POSITIONS + 0.25, widths=0.25, flierprops=FLIER)

            mean = pd.concat([
                _reindex_in(df_sim.in_temperature.mean()),
                _reindex_out(df_sim.out_temperature.mean())
            ]).sort_index()
            ax.plot(mean, c="C1", alpha=0.5, label="mean")

            nominal = pd.concat([
                _reindex_in(df_sim.in_temperature.loc[0]),
                _reindex_out(df_sim.out_temperature.loc[0])
            ]).sort_index()
            ax.plot(nominal, c="C0", alpha=0.5, label="nominal")

            in_temperatures = _reindex_in(df_exp.in_temperature.copy()) + 273.15
            for c in in_temperatures.columns:
                ax.scatter(in_temperatures.index, in_temperatures[c], marker="x", c="r", lw=1)
            out_temperatures = _reindex_out(df_exp.out_temperature.copy()) + 273.15
            for c in out_temperatures.columns:
                artist = ax.scatter(out_temperatures.index, out_temperatures[c], marker="x", c="r", lw=1)
            artist.set_label("experimental")


    @pytask.mark.task(id=sim)
    @pytask.mark.depends_on({"sim": DATA_DIR / f"sim_{sim}_results.csv", "exp": EXP_FILES})
    @pytask.mark.produces([
        IMG_DIR / f"{sim}_filling_ratio.{suffix}"
        for suffix in ["png", "pdf", "svg"]]
    )
    def task_plot_filling_ratio(produces, depends_on):
        df_sim = _load_sim_data(depends_on["sim"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Filling Ratio")
            ax.set_ylim(0.7, 1.1)

            ax.boxplot(df_sim.filling_ratio, positions=PASS_POSITIONS, flierprops=FLIER)
            ax.bar(df_sim.filling_ratio.columns, df_sim.filling_ratio.loc[0], fill="C0", alpha=0.5, label="nominal")


@pytask.mark.depends_on({
    "sim1": DATA_DIR / "sim_input_results.csv",
    "sim2": DATA_DIR / "sim_elastic_results.csv",
    "exp": EXP_FILES
})
@pytask.mark.produces([
    IMG_DIR / f"temperature_std.{suffix}"
    for suffix in ["png", "pdf", "svg"]]
)
def task_plot_temperature_std(produces, depends_on):
    df_sim1 = _load_sim_data(depends_on["sim1"])
    df_sim2 = _load_sim_data(depends_on["sim2"])

    with _plot(produces, (6, 2.5)) as (fig, ax):
        ax: plt.Axes
        ax.set_ylabel("Standard Deviation of\nWorkpiece Temperature in K")

        std1 = pd.concat([
            _reindex_in(df_sim1.in_temperature.std()),
            _reindex_out(df_sim1.out_temperature.std())
        ]).sort_index()
        ax.plot(std1, label="Case 1")

        std2 = pd.concat([
            _reindex_in(df_sim2.in_temperature.std()),
            _reindex_out(df_sim2.out_temperature.std())
        ]).sort_index()
        ax.plot(std2, label="Case 2")

        spans = [
            ax.axvspan(
                x + 0.25, x + 0.75,
                lw=0,
                color="C2" if x % 2 == 0 else "C3",
                alpha=0.4
            )
            for x in range(len(PASSES) - 1)
        ]
        spans[-1].set_label("Oval Shape")
        spans[-2].set_label("Round Shape")
