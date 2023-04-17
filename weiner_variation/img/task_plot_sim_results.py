from contextlib import contextmanager

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import pytask
import pyroll.core as pr
from matplotlib.colors import to_rgba

from weiner_variation.config import SIM_DIR, IMG_DIR, DATA_DIR, ROOT_DIR
from weiner_variation.data.config import PASSES_DIR
from weiner_variation.sim.process import PASS_SEQUENCE
from weiner_variation.sim.task_sim_temperature_stds import FACTORS as T_FACTORS
from weiner_variation.sim.task_sim_diameter_stds import FACTORS as D_FACTORS

PASSES = [u for u in PASS_SEQUENCE if isinstance(u, pr.RollPass)]

PASS_POSITIONS = np.arange(len(PASSES))
PASS_LABELS = [p.label for p in PASSES]

EXP_FILES = [PASSES_DIR / f"2022-09-26_0{i + 1}.csv" for i in range(4)]


def boxplot_props(c):
    return dict(
        flierprops=dict(
            marker="+",
            markersize="4",
        ),
        boxprops=dict(facecolor=to_rgba(c, 0.5)),
        medianprops=dict(color=c),
        patch_artist=True,
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
    fig: plt.Figure = plt.figure(figsize=figsize, dpi=600)
    ax: plt.Axes = fig.subplots()

    ax.set_xlabel("Roll Pass")
    ax.grid(True)

    yield fig, ax

    ax.xaxis.set_major_locator(plt.FixedLocator(range(len(PASSES))))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(PASS_LABELS))

    ax.legend()

    fig.tight_layout()
    for f in files.values():
        fig.savefig(f)

    plt.close(fig)


for sim, color in zip(["input", "durations", "elastic"], ["C0", "C1", "C2"]):
    @pytask.mark.task(id=sim)
    @pytask.mark.depends_on({
        "sim": DATA_DIR / f"sim_{sim}_results.csv",
        "exp": EXP_FILES,
        "config": ROOT_DIR / "config.py"
    })
    @pytask.mark.produces([
        IMG_DIR / f"{sim}_roll_force.{suffix}"
        for suffix in ["png", "pdf", "svg"]]
    )
    def task_plot_roll_force(produces, depends_on, color=color):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Roll Force $\\RollForce$ in \\unit{\\kilo\\newton}")
            ax.set_ylim(0, 400)

            ax.boxplot(df_sim.roll_force / 1e3, positions=PASS_POSITIONS, **boxplot_props(color))
            ax.bar(df_sim.roll_force.columns, df_sim.roll_force.loc[0] / 1e3, fill=color, alpha=0.5, label="nominal")

            for c in df_exp["roll_force"].columns:
                artist = ax.scatter(df_exp["roll_force"].index, df_exp["roll_force"][c], marker="x", c="r", lw=1)
            artist.set_label("experimental")


    @pytask.mark.task(id=sim)
    @pytask.mark.depends_on({
        "sim": DATA_DIR / f"sim_{sim}_results.csv",
        "exp": EXP_FILES,
        "config": ROOT_DIR / "config.py"
    })
    @pytask.mark.produces([
        IMG_DIR / f"{sim}_roll_torque.{suffix}"
        for suffix in ["png", "pdf", "svg"]]
    )
    def task_plot_roll_torque(produces, depends_on, color=color):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Roll Torque $\\RollTorque$ in \\unit{\\kilo\\newton\\meter}")
            ax.set_ylim(0, 9)

            ax.boxplot(df_sim.roll_torque / 1e3, positions=PASS_POSITIONS, **boxplot_props(color))
            ax.bar(df_sim.roll_torque.columns, df_sim.roll_torque.loc[0] / 1e3, fill=color, alpha=0.5, label="nominal")

            for c in df_exp["roll_torque"].columns:
                artist = ax.scatter(df_exp["roll_torque"].index, df_exp["roll_torque"][c], marker="x", c="r", lw=1)
            artist.set_label("experimental")


    @pytask.mark.task(id=sim)
    @pytask.mark.depends_on({
        "sim": DATA_DIR / f"sim_{sim}_results.csv",
        "exp": EXP_FILES,
        "config": ROOT_DIR / "config.py"
    })
    @pytask.mark.produces([
        IMG_DIR / f"{sim}_temperature.{suffix}"
        for suffix in ["png", "pdf", "svg"]]
    )
    def task_plot_temperature(produces, depends_on, color=color):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])

        with _plot(produces, (6.4, 3)) as (fig, ax):
            ax.set_ylabel("Workpiece Temperature $\\Temperature$ in \\unit{\\kelvin}")
            ax.set_ylim(1100, 1450)

            ax.boxplot(df_sim.in_temperature, positions=PASS_POSITIONS - 0.25, widths=0.25, **boxplot_props(color))
            ax.boxplot(df_sim.out_temperature, positions=PASS_POSITIONS + 0.25, widths=0.25, **boxplot_props(color))

            mean = pd.concat([
                _reindex_in(df_sim.in_temperature.mean()),
                _reindex_out(df_sim.out_temperature.mean())
            ]).sort_index()
            ax.plot(mean, c=color, alpha=0.5, label="mean", ls="--")

            nominal = pd.concat([
                _reindex_in(df_sim.in_temperature.loc[0]),
                _reindex_out(df_sim.out_temperature.loc[0])
            ]).sort_index()
            ax.plot(nominal, c=color, alpha=0.5, label="nominal")

            in_temperatures = _reindex_in(df_exp.in_temperature.copy()) + 273.15
            for c in in_temperatures.columns:
                ax.scatter(in_temperatures.index, in_temperatures[c], marker="x", c="r", lw=1)
            out_temperatures = _reindex_out(df_exp.out_temperature.copy()) + 273.15
            for c in out_temperatures.columns:
                artist = ax.scatter(out_temperatures.index, out_temperatures[c], marker="x", c="r", lw=1)
            artist.set_label("experimental")


    @pytask.mark.task(id=sim)
    @pytask.mark.depends_on({
        "sim": DATA_DIR / f"sim_{sim}_results.csv",
        "exp": EXP_FILES,
        "config": ROOT_DIR / "config.py"
    })
    @pytask.mark.produces([
        IMG_DIR / f"{sim}_filling_ratio.{suffix}"
        for suffix in ["png", "pdf", "svg"]]
    )
    def task_plot_filling_ratio(produces, depends_on, color=color):
        df_sim = _load_sim_data(depends_on["sim"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Filling Ratio $\\FillingRatio$")
            ax.set_ylim(0.7, 1.1)

            ax.boxplot(df_sim.filling_ratio, positions=PASS_POSITIONS, **boxplot_props(color))
            ax.bar(df_sim.filling_ratio.columns, df_sim.filling_ratio.loc[0], fill=color, alpha=0.5, label="nominal")


@pytask.mark.depends_on({
    "input": DATA_DIR / "sim_input_results.csv",
    "elastic": DATA_DIR / "sim_elastic_results.csv",
    "durations": DATA_DIR / "sim_durations_results.csv",
    "exp": EXP_FILES,
    "config": ROOT_DIR / "config.py"
})
@pytask.mark.produces([
    IMG_DIR / f"temperature_std.{suffix}"
    for suffix in ["png", "pdf", "svg"]]
)
def task_plot_temperature_std(produces, depends_on):
    df_input = _load_sim_data(depends_on["input"])
    df_durations = _load_sim_data(depends_on["durations"])

    with _plot(produces, (6, 3)) as (fig, ax):
        ax: plt.Axes
        ax.set_ylabel("Standard Deviation of\nWorkpiece Temperature \\Temperature in \\unit{\\kelvin}")

        std1 = pd.concat([
            _reindex_in(df_input.in_temperature.std()),
            _reindex_out(df_input.out_temperature.std())
        ]).sort_index()
        ax.plot(std1, label="Only Varied Input")

        std2 = pd.concat([
            _reindex_in(df_durations.in_temperature.std()),
            _reindex_out(df_durations.out_temperature.std())
        ]).sort_index()
        ax.plot(std2, label="With Varied Durations")

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


@pytask.mark.depends_on({
                            "exp": EXP_FILES,
                            "config": ROOT_DIR / "config.py"
                        } | {
                            ("input", f): DATA_DIR / "sim_temperature_stds_results" / f"{f}.csv"
                            for f in T_FACTORS
                        })
@pytask.mark.produces([
    IMG_DIR / f"temperature_stds.{suffix}"
    for suffix in ["png", "pdf", "svg"]]
)
def task_plot_temperature_stds(produces, depends_on):
    with _plot(produces, (6, 3)) as (fig, ax):
        ax: plt.Axes
        ax.set_ylabel("Standard Deviation of\nWorkpiece Temperature \\Temperature in \\unit{\\kelvin}")

        for i, f in enumerate(T_FACTORS):
            df_input = _load_sim_data(depends_on["input", f])
            std = pd.concat([
                _reindex_in(df_input.in_temperature.std()),
                _reindex_out(df_input.out_temperature.std())
            ]).sort_index()

            color = mpl.colormaps["twilight"]((i + 1) / (len(T_FACTORS) + 1))
            ax.plot(std, label=f"$\\num{{{f}}}\\Variance(\\Temperature)$", c=color)


@pytask.mark.depends_on({
                            "exp": EXP_FILES
                        } | {
                            ("input", f): DATA_DIR / "sim_diameter_stds_results" / f"{f}.csv"
                            for f in D_FACTORS
                        })
@pytask.mark.produces([
    IMG_DIR / f"filling_stds.{suffix}"
    for suffix in ["png", "pdf", "svg"]]
)
def task_plot_filling_stds(produces, depends_on):
    with _plot(produces, (6, 3)) as (fig, ax):
        ax: plt.Axes
        ax.set_ylabel("Standard Deviation of\nFilling Ratio $\\FillingRatio$")

        for i, f in enumerate(D_FACTORS):
            df_input = _load_sim_data(depends_on["input", f])

            color = mpl.colormaps["twilight"]((i + 1) / (len(D_FACTORS) + 1))
            ax.plot(
                PASS_POSITIONS, df_input.filling_ratio.std().dropna(),
                label=f"$\\num{{{f}}}\\Variance(\\Diameter)$", c=color
            )
