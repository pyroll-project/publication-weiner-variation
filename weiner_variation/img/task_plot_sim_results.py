from contextlib import contextmanager

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyroll.core as pr
import pytask
from matplotlib.colors import to_rgba
from scipy.stats import linregress

from weiner_variation.config import DATA_DIR, IMG_DIR, MATERIAL, ROOT_DIR
from weiner_variation.data.config import PASSES_FILES
from weiner_variation.sim.process import PASS_SEQUENCE
from weiner_variation.sim.task_sim_stds import FACTORS

UNIT_POSITIONS = np.arange(len(PASS_SEQUENCE))
PASS_POSITIONS = UNIT_POSITIONS[[isinstance(u, pr.RollPass) for u in PASS_SEQUENCE]]
PASS_COLUMNS = [str(i) for i in PASS_POSITIONS]
PASS_LABELS = [p.label for p in PASS_SEQUENCE.roll_passes]
TRANSPORT_POSITIONS = UNIT_POSITIONS[
    [isinstance(u, pr.Transport) for u in PASS_SEQUENCE]
]

EXP_FILES = PASSES_FILES[MATERIAL]

NOMINAL_COLOR = "C4"
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
    data.index = [int(i) - 0.5 for i in data.index]
    return data


def _reindex_out(data):
    data.index = [int(i) + 0.5 for i in data.index]
    return data


def _load_sim_data(file):
    return pd.read_csv(file, index_col=0, header=[0, 1])


def _load_nominal_data(file):
    return pd.read_csv(file, index_col=0, header=[0, 1])


def _load_exp_data(files):
    def _load_file(file):
        df = pd.read_csv(file, index_col=0, header=0)
        df.index = PASS_POSITIONS
        return df

    return pd.concat(
        [_load_file(f).stack(dropna=False).swaplevel(0, 1) for f in files],
        axis=1,
    ).T


@contextmanager
def _plot(files, figsize=(6.4, 2.5)):
    fig: plt.Figure = plt.figure(figsize=figsize, dpi=600)
    ax: plt.Axes = fig.subplots()

    ax.set_xlabel("Roll Pass")
    ax.grid(True)

    yield fig, ax

    ax.xaxis.set_major_locator(plt.FixedLocator(PASS_POSITIONS))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(PASS_LABELS))

    fig.tight_layout()
    for f in files:
        fig.savefig(f)

    plt.close(fig)


for sim, color in zip(
    ["input", "durations"], [INPUT_COLOR, DURATIONS_COLOR, ELASTIC_COLOR], strict=False
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
                df_nominal.roll_force.T / 1e3,
                fill=NOMINAL_COLOR,
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
                df_sim.roll_roll_torque / 1e3,
                positions=PASS_POSITIONS,
                **boxplot_props(color),
            )
            nom = ax.bar(
                PASS_POSITIONS,
                df_nominal.roll_roll_torque.T / 1e3,
                fill=NOMINAL_COLOR,
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
                df_sim.in_profile_temperature,
                positions=UNIT_POSITIONS - 0.5,
                widths=0.25,
                **boxplot_props(color),
            )
            sim_boxes = ax.boxplot(
                df_sim.out_profile_temperature,
                positions=UNIT_POSITIONS + 0.5,
                widths=0.25,
                **boxplot_props(color),
            )

            sim_mean = pd.concat(
                [
                    _reindex_in(df_sim.in_profile_temperature.mean()),
                    _reindex_out(df_sim.out_profile_temperature.mean()),
                ]
            ).sort_index()
            sim_mean_line = ax.plot(sim_mean, c=color, alpha=0.5, label="mean", ls="--")

            nominal = pd.concat(
                [
                    _reindex_in(df_nominal.in_profile_temperature.T),
                    _reindex_out(df_nominal.out_profile_temperature.T),
                ]
            ).sort_index()
            nominal_line = ax.plot(nominal, c=NOMINAL_COLOR, alpha=0.5, label="nominal")

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
                    sim_mean_line[0],
                    nominal_line[0],
                    exp_boxes["boxes"][0],
                    exp_mean_line[0],
                ],
                labels=[
                    "Simulation",
                    "Sim. Mean",
                    "Sim. Nominal",
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
                df_sim.in_profile_grain_size * 1e6,
                positions=UNIT_POSITIONS - 0.5,
                widths=0.25,
                **boxplot_props(color),
            )
            
            sim_boxes = ax.boxplot(
                df_sim.out_profile_grain_size * 1e6,
                positions=UNIT_POSITIONS + 0.5,
                widths=0.25,
                **boxplot_props(color),
            )

            sim_mean = pd.concat(
                [
                    _reindex_in(df_sim.in_profile_grain_size.mean()),
                    _reindex_out(df_sim.out_profile_grain_size.mean()),
                ]
            ).sort_index()
            sim_mean_line = ax.plot(
                sim_mean * 1e6, c=color, alpha=0.5, label="mean", ls="--"
            )

            nominal = pd.concat(
                [
                    _reindex_in(df_nominal.in_profile_grain_size.T),
                    _reindex_out(df_nominal.out_profile_grain_size.T),
                ]
            ).sort_index()
            nominal_line = ax.plot(
                nominal * 1e6, c=NOMINAL_COLOR, alpha=0.5, label="nominal"
            )

            ax.legend(
                handles=[
                    sim_boxes["boxes"][0],
                    sim_mean_line[0],
                    nominal_line[0],
                ],
                labels=[
                    "Simulation",
                    "Sim. Mean",
                    "Sim. Nominal",
                ],
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
                df_sim.out_profile_filling_ratio,
                positions=UNIT_POSITIONS,
                **boxplot_props(color),
            )
            nom = ax.bar(
                UNIT_POSITIONS,
                df_nominal.out_profile_filling_ratio.T,
                fill=NOMINAL_COLOR,
                alpha=0.5,
                label="Nominal",
            )

            ax.legend(
                handles=[
                    nom,
                    sim_boxes["boxes"][0],
                ],
                labels=[
                    "Nominal",
                    "Simulation",
                ],
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

        df = _load_sim_data(results)
        temperature_changes = df.temperature_change.mean().abs()
        temperature_changes.iloc[PASS_POSITIONS] += (
            df.temperature_change_by_deformation.mean().abs().dropna()
        )
        std_changes = (
            df["out_profile_temperature"].std() - df["in_profile_temperature"].std()
        ).abs() / df["in_profile_temperature"].std()

        fig: plt.Figure = plt.figure(figsize=(6.4, 2.5), dpi=600)
        ax: plt.Axes = fig.add_subplot()
        ax.set_xlabel(
            "Absolute Change in Workpiece Temperature $\\Delta\\Temperature$ in \\unit{\\kelvin}"
        )
        ax.set_ylabel(
            "Relative Depression of Workpiece\\\\Temperature Standard Deviation $\\RelativeStandardDeviationDepression$ in \\unit{\\kelvin}"
        )

        ax.scatter(
            temperature_changes.iloc[PASS_POSITIONS],
            std_changes.iloc[PASS_POSITIONS],
            label="Roll Passes",
            c="C0",
            marker="+",
        )
        ax.scatter(
            temperature_changes.iloc[TRANSPORT_POSITIONS],
            std_changes.iloc[TRANSPORT_POSITIONS],
            label="Transports",
            c="C1",
            marker="x",
        )

        rp_regr = linregress(
            temperature_changes.iloc[PASS_POSITIONS], std_changes.iloc[PASS_POSITIONS]
        )
        t_regr = linregress(
            temperature_changes.iloc[TRANSPORT_POSITIONS],
            std_changes.iloc[TRANSPORT_POSITIONS],
        )

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
            "Standard Deviation of\nWorkpiece Temperature $\\Temperature$ in \\unit{\\kelvin}"
        )
        ax.set_ylim(0, 20)

        std1 = pd.concat(
            [
                _reindex_in(df_input.in_profile_temperature.std()),
                _reindex_out(df_input.out_profile_temperature.std()),
            ]
        ).sort_index()
        ax.plot(std1, label="Only Varied Input", c=INPUT_COLOR)

        std2 = pd.concat(
            [
                _reindex_in(df_durations.in_profile_temperature.std()),
                _reindex_out(df_durations.out_profile_temperature.std()),
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
                x + 0.5, x + 1.5, lw=0, color="C2" if x % 4 == 0 else "C3", alpha=0.4
            )
            for x in PASS_POSITIONS[:-1]
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
                    _reindex_in(df_input.in_profile_temperature.std()),
                    _reindex_out(df_input.out_profile_temperature.std()),
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
                df_input.out_profile_filling_ratio.std().iloc[PASS_POSITIONS],
                label=f"$\\StandardDeviation(\\Diameter) = \\num{{{f:.2f}}}\\,\\Expectation(\\Diameter)$",
                c=color,
            )

        ax.legend()


def task_plot_roll_torque_std(
    produces=[
        IMG_DIR / f"plot_roll_torque_std.{suffix}" for suffix in ["png", "pdf", "svg"]
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
            "Standard Deviation of\nRoll Torque $\\RollTorque$ in \\unit{\\kilo\\newton\\meter}"
        )
        ax.set_ylim(0, 0.7)

        ax.plot(
            PASS_POSITIONS,
            df_input.roll_roll_torque.std() / 1e3,
            label="Only Varied Input",
            c=INPUT_COLOR,
        )

        ax.plot(
            PASS_POSITIONS,
            df_durations.roll_roll_torque.std() / 1e3,
            label="With Varied Durations",
            c=DURATIONS_COLOR,
        )

        ax.plot(
            PASS_POSITIONS, df_exp.roll_torque.std(), label="Experimental", c=EXP_COLOR
        )

        ax.legend(ncols=2, loc="upper right")


def task_plot_grain_size_std(
        produces=[
            IMG_DIR / f"plot_grain_size_std.{suffix}" for suffix in ["png", "pdf", "svg"]
        ],
        input=DATA_DIR / "sim_input_results.csv",
        durations=DATA_DIR / "sim_durations_results.csv",
        config=ROOT_DIR / "config.py",
):
    df_input = _load_sim_data(input)
    df_durations = _load_sim_data(durations)

    with _plot(produces, (6.4, 2.5)) as (fig, ax):
        ax: plt.Axes
        ax.set_ylabel(
            "Standard Deviation of\nMean Grain Size $\\GrainSize$ in \\unit{\\micro\\meter}"
        )
        ax.set_ylim(0, 7)

        std1 = pd.concat(
            [
                _reindex_in(df_input.in_profile_grain_size.std() * 1e6),
                _reindex_out(df_input.out_profile_grain_size.std() * 1e6),
            ]
        ).sort_index()
        ax.plot(std1, label="Only Varied Input", c=INPUT_COLOR)

        std2 = pd.concat(
            [
                _reindex_in(df_durations.in_profile_grain_size.std() * 1e6),
                _reindex_out(df_durations.out_profile_grain_size.std() * 1e6),
            ]
        ).sort_index()
        ax.plot(std2, label="With Varied Durations", c=DURATIONS_COLOR)

        ax.legend(ncols=1, loc="upper left")
