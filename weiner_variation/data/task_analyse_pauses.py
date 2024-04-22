import numpy as np
import pandas as pd
import pytask
from pathlib import Path
from scipy import stats, optimize

from weiner_variation.data.config import PASSES_FILES, DATA_DIR, PAUSES_BINS, MAX_PAUSE


def task_analyse_pauses(passes_files=PASSES_FILES, produces=DATA_DIR / "pauses.csv"):
    dfs = {
        f.stem: pd.read_csv(
            f, index_col=0, header=0, parse_dates=[1, 2, 3]
        ).convert_dtypes()
        for fs in passes_files.values()
        for f in fs
    }

    pauses = [
        pd.Series(
            (df.mid.values[1:] - df.mid.values[:-1]) / np.timedelta64(1, "s"),
            name=key,
            index=df.index.values[:-1] + "-" + df.index.values[1:],
        )
        for key, df in dfs.items()
    ]
    pauses = pd.concat(pauses, axis=1)
    pauses.index.name = "index"

    pauses2 = pd.DataFrame(
        {
            "mean": pauses.apply(np.mean, axis=1),
            "std": pauses.apply(np.std, axis=1),
        }
    )

    pd.concat([pauses, pauses2], axis=1).to_csv(produces, date_format="iso")


def task_analyse_duo_pauses(
    data_file=DATA_DIR / "pauses.csv",
    config_file=DATA_DIR / "config.py",
    produces={
        "data": DATA_DIR / "duo_pauses.csv",
        "dist": DATA_DIR / "duo_pauses_dist.csv",
    },
):
    df = pd.read_csv(data_file, index_col=0, header=0)

    data: pd.DataFrame = df.loc[
        df.index.str.match(r"R\d*-R\d*"), df.columns.str.match(r"Walz*")
    ]
    data = pd.concat(
        [
            data,
            pd.DataFrame(
                {
                    "R10-F1": df.loc["R10-F1", df.columns.str.match(r"Walz*")],
                    "all": data.stack(),
                }
            ).T,
        ]
    )
    data.to_csv(produces["data"])

    dist = pd.DataFrame(index=data.index)

    dist["mean"] = data.mean(axis=1)
    dist["median"] = data.median(axis=1)
    dist["std"] = data.std(axis=1)
    dist["min"] = data.min(axis=1)
    dist["max"] = data.max(axis=1)

    def find_fit(row: pd.Series):
        def _error_fun(_pars):
            hist, bins = np.histogram(
                data.loc[row.name],
                density=True,
                bins=PAUSES_BINS,
                range=(row["min"], row["max"]),
            )
            x = (bins[1:] + bins[:-1]) / 2
            pdf = stats.weibull_min.pdf(x, c=_pars[0], scale=_pars[1])
            error = ((hist - pdf) ** 2).sum()
            return error

        result = optimize.minimize(
            _error_fun,
            x0=(5, 5),
            method="Nelder-Mead",
            bounds=[(0, None), (0, None)],
            tol=1e-4,
        )

        if not result.success:
            raise ValueError(result.message)

        return pd.Series({"shape": result.x[0], "scale": result.x[1]})

    dist = dist.join(dist.apply(find_fit, axis=1))

    fits = dist.apply(lambda r: stats.weibull_min(r["shape"], scale=r["scale"]), axis=1)

    dist["fit_mean"] = fits.apply(lambda f: f.mean())
    dist["fit_std"] = fits.apply(lambda f: f.std())

    dist.to_csv(produces["dist"])
