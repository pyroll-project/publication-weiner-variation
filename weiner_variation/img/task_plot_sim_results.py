from contextlib import contextmanager

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import pytask
import pyroll.core as pr
from matplotlib.colors import to_rgba
from matplotlib.patches import Patch
from scipy.stats import linregress

from weiner_variation.config import SIM_DIR, IMG_DIR, DATA_DIR, ROOT_DIR, MATERIAL
from weiner_variation.data.config import PASSES_DIR, PASSES_FILES
from weiner_variation.sim.process import PASS_SEQUENCE
from weiner_variation.sim.task_sim_stds import FACTORS

PASSES = [u for u in PASS_SEQUENCE if isinstance(u, pr.RollPass)]

PASS_POSITIONS = np.arange(len(PASSES))
PASS_LABELS = [p.label for p in PASSES]

EXP_FILES = PASSES_FILES[MATERIAL]

EXP_COLOR = "C3"
INPUT_COLOR = "C0"
DURATIONS_COLOR = "C1"
ELASTIC_COLOR = "C2"


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


def _load_nominal_data(file):
    return pd.read_csv(file, index_col=[0, 1], header=None).iloc[:, 0]


def _load_exp_data(files):
    return pd.concat(
        [
            pd.read_csv(f, index_col=0, header=0).stack(dropna=False).swaplevel(0, 1)
            for f in files
        ],
        axis=1,
    ).T


@contextmanager
def _plot(files, figsize=(6.4, 2.5)):
    fig: plt.Figure = plt.figure(figsize=figsize, dpi=600)
    ax: plt.Axes = fig.subplots()

    ax.set_xlabel("Roll Pass")
    ax.grid(True)

    yield fig, ax

    ax.xaxis.set_major_locator(plt.FixedLocator(range(len(PASSES))))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(PASS_LABELS))

    fig.tight_layout()
    for f in files:
        fig.savefig(f)

    plt.close(fig)


for sim, color in zip(
    ["input", "durations", "elastic"], [INPUT_COLOR, DURATIONS_COLOR, ELASTIC_COLOR]
):
    dep_files = {
        "nominal": DATA_DIR / "sim_nominal_results.csv",
        "sim": DATA_DIR / f"sim_{sim}_results.csv",
        "exp": EXP_FILES,
        "config": ROOT_DIR / "config.py",
    }

    @pytask.task(id=sim)
    def task_plot_roll_force(
        produces=[
            IMG_DIR / f"plot_{sim}_roll_force.{suffix}"
            for suffix in ["png", "pdf", "svg"]
        ],
        depends_on=dep_files,
        color=color,
    ):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])
        df_nominal = _load_nominal_data(depends_on["nominal"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Roll Force $\\RollForce$ in \\unit{\\kilo\\newton}")
            ax.set_ylim(0, 400)

            sim_boxes = ax.boxplot(
                df_sim.roll_force / 1e3,
                positions=PASS_POSITIONS,
                **boxplot_props(color),
            )
            nom = ax.bar(
                PASS_POSITIONS,
                df_nominal.roll_force / 1e3,
                fill=color,
                alpha=0.5,
                label="Nominal",
            )
            exp_boxes = ax.boxplot(
                df_exp.roll_force, positions=PASS_POSITIONS, **boxplot_props(EXP_COLOR)
            )

            ax.legend(
                handles=[nom, sim_boxes["boxes"][0], exp_boxes["boxes"][0]],
                labels=["Nominal", "Simulation", "Experiment"],
            )

    @pytask.task(id=sim)
    def task_plot_roll_torque(
        produces=[
            IMG_DIR / f"plot_{sim}_roll_torque.{suffix}"
            for suffix in ["png", "pdf", "svg"]
        ],
        depends_on=dep_files,
        color=color,
    ):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])
        df_nominal = _load_nominal_data(depends_on["nominal"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Roll Torque $\\RollTorque$ in \\unit{\\kilo\\newton\\meter}")
            ax.set_ylim(0, 12)

            sim_boxes = ax.boxplot(
                df_sim.roll_torque / 1e3,
                positions=PASS_POSITIONS,
                **boxplot_props(color),
            )
            nom = ax.bar(
                PASS_POSITIONS,
                df_nominal.roll_torque / 1e3,
                fill=color,
                alpha=0.5,
                label="Nominal",
            )
            exp_boxes = ax.boxplot(
                df_exp.roll_torque / 2,
                positions=PASS_POSITIONS,
                **boxplot_props(EXP_COLOR),
            )

            ax.legend(
                handles=[nom, sim_boxes["boxes"][0], exp_boxes["boxes"][0]],
                labels=["Nominal", "Simulation", "Experiment"],
            )

    @pytask.task(id=sim)
    def task_plot_temperature(
        produces=[
            IMG_DIR / f"plot_{sim}_temperature.{suffix}"
            for suffix in ["png", "pdf", "svg"]
        ],
        depends_on=dep_files,
        color=color,
    ):
        df_sim = _load_sim_data(depends_on["sim"])
        df_exp = _load_exp_data(depends_on["exp"])
        df_nominal = _load_nominal_data(depends_on["nominal"])

        with _plot(produces, (6.4, 2.5)) as (fig, ax):
            ax.set_ylabel("Workpiece Temperature $\\Temperature$ in \\unit{\\kelvin}")
            ax.set_ylim(1100, 1500)

            ax.boxplot(
                df_sim.in_temperature,
                positions=PASS_POSITIONS - 0.25,
                widths=0.25,
                **boxplot_props(color),
            )
            sim_boxes = ax.boxplot(
                df_sim.out_temperature,
                positions=PASS_POSITIONS + 0.25,
                widths=0.25,
                **boxplot_props(color),
            )

            sim_mean = pd.concat(
                [
                    _reindex_in(df_sim.in_temperature.mean()),
                    _reindex_out(df_sim.out_temperature.mean()),
                ]
            ).sort_index()
            sim_mean_line = ax.plot(sim_mean, c=color, alpha=0.5, label="mean", ls="--")

            nominal = pd.concat(
                [
                    _reindex_in(df_nominal.in_temperature),
                    _reindex_out(df_nominal.out_temperature),
                ]
            ).sort_index()
            nominal_line = ax.plot(nominal, c=color, alpha=0.5, label="nominal")

            ax.boxplot(
                df_exp.in_temperature + 273.15,
                positions=PASS_POSITIONS - 0.25,
                widths=0.25,
                **boxplot_props(EXP_COLOR),
            )
            exp_boxes = ax.boxplot(
                df_exp.out_temperature + 273.15,
                positions=PASS_POSITIONS + 0.25,
                widths=0.25,
                **boxplot_props(EXP_COLOR),
            )
            exp_mean = (
                pd.concat(
                    [
                        _reindex_in(df_exp.in_temperature.mean()),
                        _reindex_out(df_exp.out_temperature.mean()),
                    ]
                )
                .sort_index()
                .dropna()
            )
            exp_mean_line = ax.plot(
                exp_mean + 273.15, c=EXP_COLOR, alpha=0.5, label="mean", ls="--"
            )

            ax.legend(
                handles=[
                    sim_boxes["boxes"][0],
                    nominal_line[0],
                    sim_mean_line[0],
                    exp_boxes["boxes"][0],
                    exp_mean_line[0],
                ],
                labels=[
                    "Simulation",
                    "Sim. Nominal",
                    "Sim. Mean",
                    "Experiment",
                    "Exp. Mean",
                ],
                loc="lower left",
                ncols=2,
            )

    @pytask.task(id=sim)
    def task_plot_grain_size(
        produces=[
            IMG_DIR / f"plot_{sim}_grain_size.{suffix}"
            for suffix in ["png", "pdf", "svg"]
        ],
        depends_on=dep_files,
        color=color,
    ):
        df_sim = _load_sim_data(depends_on["sim"])
        df_nominal = _load_nominal_data(depends_on["nominal"])

        with _plot(produces, (6.4, 2.5)) as (fig, ax):
            ax.set_ylabel("Mean Grain Size $\\GrainSize$ in \\unit{\\micro\\meter}")
            # ax.set_ylim(1100, 1500)

            ax.boxplot(
                df_sim.in_grain_size * 1e6,
                positions=PASS_POSITIONS - 0.25,
                widths=0.25,
                **boxplot_props(color),
            )
            sim_boxes = ax.boxplot(
                df_sim.out_grain_size * 1e6,
                positions=PASS_POSITIONS + 0.25,
                widths=0.25,
                **boxplot_props(color),
            )

            sim_mean = pd.concat(
                [
                    _reindex_in(df_sim.in_grain_size.mean()),
                    _reindex_out(df_sim.out_grain_size.mean()),
                ]
            ).sort_index()
            sim_mean_line = ax.plot(
                sim_mean * 1e6, c=color, alpha=0.5, label="mean", ls="--"
            )

            nominal = pd.concat(
                [
                    _reindex_in(df_nominal.in_grain_size),
                    _reindex_out(df_nominal.out_grain_size),
                ]
            ).sort_index()
            nominal_line = ax.plot(nominal * 1e6, c=color, alpha=0.5, label="nominal")

            ax.legend(
                handles=[
                    sim_boxes["boxes"][0],
                    nominal_line[0],
                    sim_mean_line[0],
                ],
                labels=["Simulation", "Sim. Nominal", "Sim. Mean"],
                loc="lower left",
                ncols=2,
            )

    @pytask.task(id=sim)
    def task_plot_filling_ratio(
        produces=[
            IMG_DIR / f"plot_{sim}_filling_ratio.{suffix}"
            for suffix in ["png", "pdf", "svg"]
        ],
        depends_on=dep_files,
        color=color,
    ):
        df_sim = _load_sim_data(depends_on["sim"])
        df_nominal = _load_nominal_data(depends_on["nominal"])

        with _plot(produces) as (fig, ax):
            ax.set_ylabel("Filling Ratio $\\FillingRatio$")
            ax.set_ylim(0.7, 1.1)

            sim_boxes = ax.boxplot(
                df_sim.filling_ratio, positions=PASS_POSITIONS, **boxplot_props(color)
            )
            nom = ax.bar(
                PASS_POSITIONS,
                df_nominal.filling_ratio,
                fill=color,
                alpha=0.5,
                label="Nominal",
            )

            ax.legend(
                handles=[nom, sim_boxes["boxes"][0]], labels=["Nominal", "Simulation"]
            )

    @pytask.task(id=sim)
    def task_plot_temperature_correlation(
        produces=[
            IMG_DIR / f"plot_{sim}_temperature_correlation.{suffix}"
            for suffix in ["png", "pdf", "svg"]
        ],
        results=DATA_DIR / f"sim_{sim}_results.csv",
        config=ROOT_DIR / "config.py",
    ):
        XMAX = 70

        df_passes = _load_sim_data(results)
        df_transports = pd.DataFrame(
            {
                ("in_temperature", f"T{i}"): df_passes["out_temperature"].iloc[:, i]
                for i in range(len(df_passes["out_temperature"].columns) - 1)
            }
            | {
                ("out_temperature", f"T{i}"): df_passes["in_temperature"].iloc[:, i + 1]
                for i in range(len(df_passes["in_temperature"].columns) - 1)
            }
        )

        temperature_changes_rp = (df_passes["heat_turnover"]).mean().abs()
        temperature_changes_t = (
            (df_transports["out_temperature"] - df_transports["in_temperature"])
            .mean()
            .abs()
        )
        std_changes_rp = (
            df_passes["out_temperature"].std() - df_passes["in_temperature"].std()
        ).abs() / df_passes["in_temperature"].std()
        std_changes_t = (
            df_transports["out_temperature"].std()
            - df_transports["in_temperature"].std()
        ).abs() / df_transports["in_temperature"].std()

        fig: plt.Figure = plt.figure(figsize=(6.4, 3.0), dpi=600)
        ax: plt.Axes = fig.add_subplot()
        ax.set_xlabel(
            "Absolute Change in Workpiece Temperature $\\Delta\\Temperature$ in \\unit{\\kelvin}"
        )
        ax.set_ylabel(
            "Relative Depression of Workpiece\\\\Temperature Standard Deviation $\\RelativeStandardDeviationDepression$ in \\unit{\\kelvin}"
        )

        ax.scatter(
            temperature_changes_rp,
            std_changes_rp,
            label="Roll Passes",
            c="C0",
            marker="+",
        )
        ax.scatter(
            temperature_changes_t, std_changes_t, label="Transports", c="C1", marker="x"
        )

        rp_regr = linregress(temperature_changes_rp, std_changes_rp)
        t_regr = linregress(temperature_changes_t, std_changes_t)

        x = np.linspace(0, XMAX)
        ax.plot(x, rp_regr.slope * x + rp_regr.intercept, c="C0", ls="--")
        ax.plot(x, t_regr.slope * x + t_regr.intercept, c="C1", ls="--")

        ax.legend()
        ax.grid(True)
        ax.set_xlim(0, XMAX)
        ax.set_ylim(0, None)

        fig.tight_layout()
        for f in produces:
            fig.savefig(f)

        plt.close(fig)


def task_plot_temperature_std(
    produces=[
        IMG_DIR / f"plot_temperature_std.{suffix}" for suffix in ["png", "pdf", "svg"]
    ],
    input=DATA_DIR / "sim_input_results.csv",
    durations=DATA_DIR / "sim_durations_results.csv",
    exp=EXP_FILES,
    config=ROOT_DIR / "config.py",
):
    df_input = _load_sim_data(input)
    df_durations = _load_sim_data(durations)
    df_exp = _load_exp_data(exp)

    with _plot(produces, (6.4, 2.5)) as (fig, ax):
        ax: plt.Axes
        ax.set_ylabel(
            "Standard Deviation of\nWorkpiece Temperature \\Temperature in \\unit{\\kelvin}"
        )
        ax.set_ylim(0, 18)

        std1 = pd.concat(
            [
                _reindex_in(df_input.in_temperature.std()),
                _reindex_out(df_input.out_temperature.std()),
            ]
        ).sort_index()
        ax.plot(std1, label="Only Varied Input", c=INPUT_COLOR)

        std2 = pd.concat(
            [
                _reindex_in(df_durations.in_temperature.std()),
                _reindex_out(df_durations.out_temperature.std()),
            ]
        ).sort_index()
        ax.plot(std2, label="With Varied Durations", c=DURATIONS_COLOR)

        std3 = pd.concat(
            [
                _reindex_in(
                    df_exp.in_temperature[
                        df_exp.in_temperature > df_exp.in_temperature.median() - 30
                    ].std()
                ),
                _reindex_out(
                    df_exp.out_temperature[
                        df_exp.out_temperature > df_exp.out_temperature.median() - 30
                    ].std()
                ),
            ]
        ).sort_index()
        std3.dropna()
        ax.plot(std3, label="Experimental", c=EXP_COLOR)

        spans = [
            ax.axvspan(
                x + 0.25, x + 0.75, lw=0, color="C2" if x % 2 == 0 else "C3", alpha=0.4
            )
            for x in range(len(PASSES) - 1)
        ]
        spans[-1].set_label("Oval Shape")
        spans[-2].set_label("Round Shape")

        ax.legend(ncols=2, loc="lower left")


def task_plot_temperature_stds(
    produces=[
        IMG_DIR / f"plot_temperature_stds.{suffix}" for suffix in ["png", "pdf", "svg"]
    ],
    depends_on={"exp": EXP_FILES, "config": ROOT_DIR / "config.py"}
    | {
        ("input", f): DATA_DIR / "sim_temperature_stds_results" / f"{f}.csv"
        for f in FACTORS
    },
):
    with _plot(produces, (6.4, 2.5)) as (fig, ax):
        ax: plt.Axes
        ax.set_ylabel(
            "Standard Deviation of\nWorkpiece Temperature $\\StandardDeviation(\\Temperature)$ in \\unit{\\kelvin}"
        )

        for i, f in enumerate(FACTORS):
            df_input = _load_sim_data(depends_on["input", f])
            std = pd.concat(
                [
                    _reindex_in(df_input.in_temperature.std()),
                    _reindex_out(df_input.out_temperature.std()),
                ]
            ).sort_index()

            color = mpl.colormaps["twilight"]((i + 1) / (len(FACTORS) + 1))
            ax.plot(
                std,
                label=f"$\\StandardDeviation(\\Temperature) = \\num{{{f:.2f}}}\\,\\Expectation(\\Temperature)$",
                c=color,
            )

        ax.legend()


def task_plot_filling_stds(
    produces=[
        IMG_DIR / f"plot_filling_stds.{suffix}" for suffix in ["png", "pdf", "svg"]
    ],
    depends_on={"exp": EXP_FILES}
    | {
        ("input", f): DATA_DIR / "sim_diameter_stds_results" / f"{f}.csv"
        for f in FACTORS
    },
):
    with _plot(produces, (6.4, 2.5)) as (fig, ax):
        ax: plt.Axes
        ax.set_ylabel(
            "Standard Deviation of\nFilling Ratio $\\StandardDeviation(\\FillingRatio)$"
        )

        for i, f in enumerate(FACTORS):
            df_input = _load_sim_data(depends_on["input", f])

            color = mpl.colormaps["twilight"]((i + 1) / (len(FACTORS) + 1))
            ax.plot(
                PASS_POSITIONS,
                df_input.filling_ratio.std().dropna(),
                label=f"$\\StandardDeviation(\\Diameter) = \\num{{{f:.2f}}}\\,\\Expectation(\\Diameter)$",
                c=color,
            )

        ax.legend()
