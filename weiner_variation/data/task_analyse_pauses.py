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
    dfs = {f.stem: pd.read_csv(f, index_col=0, header=0, parse_dates=[1, 2, 3]).convert_dtypes() for f in PASSES_FILES}

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

    data = pd.Series(
        df.loc[df.index.str.match(r"R\d*-R\d*"), df.columns.str.match(r"\d*-\d*-\d*_\d*")].values.flat
    ).dropna()

    data = data[data < MAX_PAUSE]

    data.to_csv(produces["data"], index=False, header=False)

    data_mean = data.mean()
    data_std = data.std()
    data_min = data.min()

    shifted = data - data_min
    shifted_mean = shifted.mean()
    shifted_std = shifted.std()
    alpha = shifted_mean ** 2 / shifted_std ** 2
    beta = shifted_std ** 2 / shifted_mean

    def _error_fun(_pars):
        hist, bins = np.histogram(data, density=True, bins=PAUSES_BINS, range=(_pars[2], MAX_PAUSE))
        x = (bins[1:] + bins[:-1]) / 2
        pdf = stats.gamma.pdf(x, a=_pars[0], scale=_pars[1], loc=_pars[2])
        error = ((hist - pdf) ** 2).sum()
        return error

    result = optimize.minimize(_error_fun, x0=np.array([alpha, beta, data_min]), method="Nelder-Mead", tol=1e-4)

    if not result.success:
        raise ValueError(result.message)

    alpha, beta, loc = result.x

    dist = pd.DataFrame({
        "mean": [data_mean],
        "std": [data_std],
        "max": [data.max()],
        "min": [data_min],
        "loc": [loc],
        "alpha": [alpha],
        "beta": [beta],
    })

    dist.to_csv(produces["dist"], index=False)
