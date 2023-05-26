from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytask
from pathlib import Path

from scipy import stats

from weiner_variation.config import DATA_DIR, IMG_DIR, ROOT_DIR
from weiner_variation.data.config import PAUSES_BINS


for i in range(10):
    @pytask.mark.task(id=i)
    @pytask.mark.depends_on({
        "data": DATA_DIR / "duo_pauses.csv",
        "dist": DATA_DIR / "duo_pauses_dist.csv",
        "config": ROOT_DIR / "config.py"
    })
    @pytask.mark.produces([IMG_DIR / f"plot_histogram_pauses{i}.{s}" for s in ["png", "pdf", "svg"]])
    def task_plot_histogram_pauses(depends_on: dict[str, Path], produces: dict[Any, Path], row_index=i):
        fig: plt.Figure = plt.figure(dpi=600, figsize=(6.4, 4.5))
        ax: list[plt.Axes] = fig.subplots(nrows=2, sharex="all")
        ax[0].grid(True)
        ax[0].set_ylabel("Probability Density")

        ax[1].grid(True)
        ax[1].set_ylabel("Cumulative Density")
        ax[1].set_xlabel("Pause Duration $\\Pause{\\Duration}$ in s")
        ax[1].set_ylim(0, 1.1)

        data = pd.read_csv(depends_on["data"], index_col=0).iloc[row_index]
        dist = pd.read_csv(depends_on["dist"], index_col=0).iloc[row_index]

        ax[0].hist(data, bins=PAUSES_BINS, alpha=0.5, density=True, range=(dist["loc"], dist["max"]))
        ax[1].hist(data, bins=PAUSES_BINS, alpha=0.5, density=True, cumulative=True, range=(dist["loc"], dist["max"]))

        gamma = stats.gamma(a=dist["alpha"], scale=dist["beta"], loc=dist["loc"])

        x = np.geomspace(dist["loc"], dist["max"], 500)
        ax[0].plot(x, gamma.pdf(x), c="C0")
        ax[1].plot(x, gamma.cdf(x), c="C0")

        ax[0].text(dist["max"], gamma.pdf(x).max(), "\n".join(
            [
                rf"$\Estimated{{{s}}} = \num{{{dist[k]:.3f}}}$"
                for s, k in [
                    (r"\Mean", "mean"),
                    (r"\StandardDeviation", "std"),
                    (r"\GammaDistributionAlpha", "alpha"),
                    (r"\GammaDistributionBeta", "beta"),
                    (r"\Min{\Pause{\Duration}}", "loc")
                ]
            ]
        ), verticalalignment="top", horizontalalignment="right", bbox=dict(facecolor="white", boxstyle="round"))

        fig.tight_layout()
        fig.subplots_adjust(wspace=0.2)

        for p in produces.values():
            fig.savefig(p)
