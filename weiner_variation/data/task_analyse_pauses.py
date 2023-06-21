import numpy as np
import pandas as pd
import pytask
from pathlib import Path
from scipy import stats, optimize

from weiner_variation.data.config import PASSES_FILES, DATA_DIR, PAUSES_BINS, MAX_PAUSE


@pytask.mark.task()
@pytask.mark.depends_on(PASSES_FILES)
@pytask.mark.produces(DATA_DIR / "pauses.csv")
def task_analyse_pauses(produces: Path):
    dfs = {
        f.stem: pd.read_csv(f, index_col=0, header=0, parse_dates=[1, 2, 3]).convert_dtypes()
        for fs in PASSES_FILES.values() for f in fs
    }

    pauses = [
        pd.Series(
            (df.mid.values[1:] - df.mid.values[:-1]) / np.timedelta64(1, "s"),
            name=key,
            index=df.index.values[:-1] + "-" + df.index.values[1:],
        ) for key, df in dfs.items()
    ]
    pauses = pd.concat(pauses, axis=1)
    pauses.index.name = "index"

    pauses2 = pd.DataFrame({
        "mean": pauses.apply(np.mean, axis=1),
        "std": pauses.apply(np.std, axis=1),
    })

    pd.concat([pauses, pauses2], axis=1).to_csv(produces, date_format="iso")


@pytask.mark.depends_on({"data": DATA_DIR / "pauses.csv", "config": DATA_DIR / "config.py"})
@pytask.mark.produces({"data": DATA_DIR / "duo_pauses.csv", "dist": DATA_DIR / "duo_pauses_dist.csv"})
def task_analyse_duo_pauses(produces: dict[str, Path], depends_on: dict[str, Path]):
    df = pd.read_csv(depends_on["data"], index_col=0, header=0)

    data: pd.DataFrame = df.loc[df.index.str.match(r"R\d*-R\d*"), df.columns.str.match(r"Walz*")]
    data = pd.concat([
        data,
        pd.DataFrame({
            "R10-F1": df.loc["R10-F1", df.columns.str.match(r"Walz*")],
            "all": data.stack(),
        }).T
    ])
    data.to_csv(produces["data"])

    data_mean = data.mean(axis=1)
    data_std = data.std(axis=1)
    data_min = data.min(axis=1)
    data_max = data_mean + 3 * data_std

    shifted = data.sub(data_min, axis="index")
    shifted_mean = shifted.mean(axis=1)
    shifted_std = shifted.std(axis=1)
    shape = shifted_mean ** 2 / shifted_std ** 2
    scale = shifted_std ** 2 / shifted_mean

    for i, row in data.iterrows():
        def _error_fun(_pars):
            hist, bins = np.histogram(row, density=True, bins=PAUSES_BINS, range=(data_min[i], data_max[i]))
            x = (bins[1:] + bins[:-1]) / 2
            pdf = stats.weibull_min.pdf(x, c=_pars[0], scale=_pars[1])
            error = ((hist - pdf) ** 2).sum()
            return error

        result = optimize.minimize(
            _error_fun,
            x0=np.array([5, 5]),
            method="Nelder-Mead",
            bounds=[(0, None), (0, None)],
            tol=1e-4
        )

        if not result.success:
            raise ValueError(result.message)

        shape[i], scale[i] = result.x

    dist = pd.DataFrame({
        "mean": data_mean,
        "std": data_std,
        "max": data_max,
        "min": data_min,
        "shape": shape,
        "scale": scale,
    }, index=data.index)

    dist.to_csv(produces["dist"])
