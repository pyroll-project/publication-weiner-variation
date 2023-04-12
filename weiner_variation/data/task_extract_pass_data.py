import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytask
from pathlib import Path
from weiner_variation.data.config import PASSES_FILES, RAW_DATA_FILES

from scipy import stats, signal

PEAK_DISTANCE = 100
WINDOW_LENGTH = 30
PROMINENCE_DUO = 0.8
PROMINENCE_F = 0.08

MIN_TEMP = 850

for in_file, out_file in zip(RAW_DATA_FILES, PASSES_FILES):
    @pytask.mark.task(id=in_file.stem)
    @pytask.mark.depends_on(in_file)
    @pytask.mark.produces(out_file)
    def task_extract_pass_data(depends_on: Path, produces: Path):
        raw_data = pd.read_csv(depends_on, header=0, index_col=0)
        raw_data.index = pd.to_datetime(raw_data.index)
        raw_data = raw_data.resample("10ms").mean()

        def _extract_force_and_torque(p: pd.DataFrame, key: str):
            p["roll_force"] = p.apply(
                lambda row: raw_data[f"roll_force_{key}"][
                    (raw_data.index > row.start) & (raw_data.index < row.end)].median(),
                axis=1
            )
            p["roll_torque"] = p.apply(
                lambda row: np.abs(raw_data[f"roll_torque_{key}"][
                                       (raw_data.index > row.start) & (raw_data.index < row.end)]).median(),
                axis=1
            )

        def _extract_duo_temperatures(row):
            if row.name % 2 == 0:
                t = raw_data["temp_3"]
            else:
                t = raw_data["temp_2"]

            return t[
                (raw_data.index > row.start - pd.Timedelta(500, "ms"))
                & (raw_data.index < row.start - pd.Timedelta(200, "ms"))
                & (t > MIN_TEMP)
                ].median()

        duo_passes = find_passes(raw_data["roll_torque_duo"], PROMINENCE_DUO)
        _extract_force_and_torque(duo_passes, "duo")

        duo_passes["out_temperature"] = duo_passes.apply(_extract_duo_temperatures, axis=1)

        f_passes = list(range(4))
        for i in range(4):
            f_passes[i] = find_passes(raw_data[f"roll_torque_f{i + 1}"], PROMINENCE_F, 1)
            if not f_passes[i].empty:
                _extract_force_and_torque(f_passes[i], f"f{i + 1}")
                f_passes[i]["in_temperature"] = f_passes[i].apply(
                    lambda row: raw_data[f"temp_{4 + i}"][
                        (raw_data.index > row.start) & (raw_data.index < row.end) & (raw_data[f"temp_{4 + i}"] > MIN_TEMP)
                        ].median(),
                    axis=1
                )
                f_passes[i]["out_temperature"] = f_passes[i].apply(
                    lambda row: raw_data[f"temp_{5 + i}"][
                        (raw_data.index > row.start) & (raw_data.index < row.end) & (raw_data[f"temp_{5 + i}"] > MIN_TEMP)
                        ].median(),
                    axis=1
                )

        f_passes = pd.concat(f_passes, ignore_index=True)

        duo_passes.index = [f"R{i + 1}" for i in duo_passes.index]
        f_passes.index = [f"F{i + 1}" for i in f_passes.index]
        passes = pd.concat([duo_passes, f_passes])
        passes.index.name = "index"
        passes.to_csv(produces)


def find_passes(torque_series, prominence, max_num=None):
    try:
        abs_data = np.abs(torque_series)
        resampled = abs_data
        smooth = np.correlate(resampled, np.full((10,), 1 / 10), mode="same")
        diff = np.correlate(smooth, [-2, 0, 2], mode="same")
        smooth_diff = np.correlate(diff, stats.norm.pdf(np.linspace(-1, 1, 5)), mode="same")

        peaks_start, peaks_start_props = signal.find_peaks(smooth_diff, distance=PEAK_DISTANCE, prominence=prominence,
                                                           wlen=WINDOW_LENGTH)
        peaks_end, peaks_end_props = signal.find_peaks(-smooth_diff, distance=PEAK_DISTANCE, prominence=prominence,
                                                       wlen=WINDOW_LENGTH)

        starts = resampled.index[peaks_start]
        ends = resampled.index[peaks_end]

        if len(starts) != len(ends):
            raise ValueError(f"len(starts) = {len(starts)} != {len(ends)} = len(ends)")

        if max_num and len(starts) > max_num:
            raise ValueError()

        return pd.DataFrame({"start": starts, "end": ends, "mid": starts + (ends - starts) / 2})

    except ValueError:
        fig: plt.Figure = plt.figure(dpi=300)
        ax: plt.Axes = fig.add_subplot()
        ax.grid(True)
        ax.plot(torque_series.index, abs_data, lw=1, alpha=0.5, label="roll torque signal")
        ax.plot(resampled.index, resampled, lw=1, alpha=0.5, label="roll torque signal resampled")
        ax.plot(resampled.index, smooth, lw=1, label="filtered signal smooth")
        ax.plot(resampled.index, diff, lw=1, label="filtered signal diff")
        ax.plot(resampled.index, smooth_diff, lw=1, label="filtered signal smooth diff")
        ax.scatter(resampled.index[peaks_start], diff[peaks_start], marker="x", c="k", label="starts of passes")
        ax.scatter(resampled.index[peaks_end], diff[peaks_end], marker="x", c="r", label="ends of passes")

        ax.legend()
        fig.show()
        plt.close(fig)

        raise
