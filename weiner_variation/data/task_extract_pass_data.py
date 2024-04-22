import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytask
from pathlib import Path
from weiner_variation.data.config import (
    PASSES_FILES,
    RAW_DATA_FILES,
    PASSES_DIR,
    MATERIALS,
)

from scipy import stats, signal

PEAK_DISTANCE = 100
WINDOW_LENGTH = 30
PROMINENCE_DUO = (0.8, 0.8)
PROMINENCE_F = (0.3, 0.1)

MIN_TEMP = 850

for material in MATERIALS:
    for in_file, out_file in zip(RAW_DATA_FILES[material], PASSES_FILES[material]):

        @pytask.task(id=f"{material}/{in_file.stem}")
        def task_extract_pass_data(
            depends_on=in_file, produces=out_file, id=in_file.stem
        ):
            raw_data = pd.read_csv(depends_on, header=0, index_col=0)
            raw_data.index = pd.to_datetime(raw_data.index)
            raw_data = raw_data.resample("10ms").mean()

            def _extract_force_or_torque(
                key: str,
                delta1=pd.Timedelta("-50ms"),
                delta2=pd.Timedelta("-50ms"),
                delta3=pd.Timedelta("500ms"),
            ):
                def _get(row):
                    idx_plateau = (raw_data.index > row.start - delta1) & (
                        raw_data.index < row.end + delta2
                    )
                    plateau = raw_data[key][idx_plateau].median()
                    idx_base = (raw_data.index > row.start - delta3) & (
                        raw_data.index < row.start
                    )
                    base = raw_data[key][idx_base].median()
                    return np.abs(plateau - base)

                return _get

            def _extract_duo_temperature_in(
                delta1=pd.Timedelta("100ms"), delta2=pd.Timedelta("300ms")
            ):
                def _get(row):
                    if row.name % 2 == 0:
                        t_in = raw_data["temp_3"]
                    else:
                        t_in = raw_data["temp_2"]

                    idx_in = (raw_data.index < row.start - delta1) & (
                        raw_data.index > row.start - delta2
                    )
                    return t_in[idx_in & (t_in > MIN_TEMP)].median()

                return _get

            def _extract_duo_temperature_out(
                delta1=pd.Timedelta("100ms"), delta2=pd.Timedelta("300ms")
            ):
                def _get(row):
                    if row.name % 2 == 0:
                        t_out = raw_data["temp_2"]
                    else:
                        t_out = raw_data["temp_3"]

                    idx_out = (raw_data.index > row.end + delta1) & (
                        raw_data.index < row.end + delta2
                    )
                    return t_out[idx_out & (t_out > MIN_TEMP)].median()

                return _get

            def _extract_f_temperature_in(
                i, delta1=pd.Timedelta("-300ms"), delta2=pd.Timedelta("-100ms")
            ):
                def _get(row):
                    t_in = raw_data[f"temp_{4 + i}"]
                    idx_in = (raw_data.index < row.start - delta1) & (
                        raw_data.index > row.start - delta2
                    )
                    return t_in[idx_in & (t_in > MIN_TEMP)].median()

                return _get

            def _extract_f_temperature_out(
                i, delta1=pd.Timedelta("-300ms"), delta2=pd.Timedelta("-100ms")
            ):
                def _get(row):
                    t_out = raw_data[f"temp_{5 + i}"]
                    idx_out = (raw_data.index > row.end + delta1) & (
                        raw_data.index < row.end + delta2
                    )
                    return t_out[idx_out & (t_out > MIN_TEMP)].median()

                return _get

            duo_passes = find_passes(
                id, raw_data["roll_torque_duo"], PROMINENCE_DUO, 10
            )
            duo_passes["roll_force"] = duo_passes.apply(
                _extract_force_or_torque("roll_force_duo"), axis=1
            )
            duo_passes["roll_torque"] = duo_passes.apply(
                _extract_force_or_torque("roll_torque_duo"), axis=1
            )

            duo_passes["in_temperature"] = duo_passes.apply(
                _extract_duo_temperature_in(), axis=1
            )
            duo_passes["out_temperature"] = duo_passes.apply(
                _extract_duo_temperature_out(), axis=1
            )

            f_passes = list(range(4))
            for i in range(4):
                f_passes[i] = find_passes(
                    id, raw_data[f"roll_torque_f{i + 1}"], PROMINENCE_F, 1
                )
                if not f_passes[i].empty:
                    f_passes[i]["roll_force"] = f_passes[i].apply(
                        _extract_force_or_torque(f"roll_force_f{i + 1}"), axis=1
                    )
                    f_passes[i]["roll_torque"] = f_passes[i].apply(
                        _extract_force_or_torque(f"roll_torque_f{i + 1}"), axis=1
                    )
                    f_passes[i]["in_temperature"] = f_passes[i].apply(
                        _extract_f_temperature_in(i), axis=1
                    )
                    f_passes[i]["out_temperature"] = f_passes[i].apply(
                        _extract_f_temperature_out(i), axis=1
                    )

            f_passes = pd.concat(f_passes, ignore_index=True)

            duo_passes.index = [f"R{i + 1}" for i in duo_passes.index]
            f_passes.index = [f"F{i + 1}" for i in f_passes.index]
            passes = pd.concat([duo_passes, f_passes])
            passes.index.name = "index"
            passes.to_csv(produces)


def find_passes(id: str, torque_series: pd.Series, prominence, num):
    abs_data = np.abs(torque_series)
    smooth = np.correlate(abs_data, np.full((10,), 1 / 10), mode="same")
    diff = np.correlate(smooth, [-2, 0, 2], mode="same")
    smooth_diff = np.correlate(diff, stats.norm.pdf(np.linspace(-1, 1, 5)), mode="same")

    peaks_start, peaks_start_props = signal.find_peaks(
        smooth_diff,
        distance=PEAK_DISTANCE,
        prominence=prominence[0],
        wlen=WINDOW_LENGTH,
    )
    peaks_end, peaks_end_props = signal.find_peaks(
        -smooth_diff,
        distance=PEAK_DISTANCE,
        prominence=prominence[1],
        wlen=WINDOW_LENGTH,
    )

    starts = torque_series.index[peaks_start]
    ends = torque_series.index[peaks_end]

    fig: plt.Figure = plt.figure(dpi=300)
    ax: plt.Axes = fig.add_subplot()
    ax.grid(True)
    ax.plot(torque_series.index, abs_data, lw=1, alpha=0.5, label="abs signal")
    ax.plot(torque_series.index, smooth, lw=1, label="smooth")
    ax.plot(torque_series.index, diff, lw=1, label="smooth diff")
    ax.plot(torque_series.index, smooth_diff, lw=1, label="smooth diff smooth")
    ax.scatter(
        torque_series.index[peaks_start],
        diff[peaks_start],
        marker="x",
        c="k",
        label="starts of passes",
    )
    ax.scatter(
        torque_series.index[peaks_end],
        diff[peaks_end],
        marker="x",
        c="r",
        label="ends of passes",
    )

    ax.legend()
    path = PASSES_DIR / "plots" / id / f"{torque_series.name}.png"
    path.parent.mkdir(exist_ok=True, parents=True)
    fig.savefig(path)
    plt.close(fig)

    if len(starts) != len(ends):
        raise ValueError(f"len(starts) = {len(starts)} != {len(ends)} = len(ends)")

    if not len(starts) == num:
        raise ValueError()

    if len(starts) == 0:
        raise ValueError()

    return pd.DataFrame(
        {"start": starts, "end": ends, "mid": starts + (ends - starts) / 2}
    )
