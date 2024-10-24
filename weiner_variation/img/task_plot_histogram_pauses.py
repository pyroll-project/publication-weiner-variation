import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytask
from scipy import stats

from weiner_variation.config import DATA_DIR, IMG_DIR, ROOT_DIR
from weiner_variation.data.config import PAUSES_BINS

for i in range(11):

    @pytask.task(id=str(i))
    def task_plot_histogram_pauses(
        data=DATA_DIR / "duo_pauses.csv",
        dist=DATA_DIR / "duo_pauses_dist.csv",
        config=ROOT_DIR / "config.py",
        produces=[IMG_DIR / f"plot_histogram_pauses{i}.{s}" for s in ["png", "pdf", "svg"]],
        row_index=i,
    ):
        fig: plt.Figure = plt.figure(dpi=600, figsize=(6.4, 4.5), layout="constrained")
        ax: list[plt.Axes] = fig.subplots(nrows=2, sharex="all")
        ax[0].grid(True)
        ax[0].set_ylabel("Probability Density")

        ax[1].grid(True)
        ax[1].set_ylabel("Cumulative Density")
        ax[1].set_xlabel("Pause Duration $\\Pause{\\Duration}$ in s")
        ax[1].set_ylim(0, 1.1)

        data = pd.read_csv(data, index_col=0).iloc[row_index]
        dist = pd.read_csv(dist, index_col=0).iloc[row_index]

        ax[0].hist(
            data,
            bins=PAUSES_BINS,
            alpha=0.5,
            density=True,
            range=(dist["min"], dist["max"]),
        )
        ax[1].hist(
            data,
            bins=PAUSES_BINS,
            alpha=0.5,
            density=True,
            cumulative=True,
            range=(dist["min"], dist["max"]),
        )

        wb = stats.weibull_min(c=dist["shape"], scale=dist["scale"])

        x = np.geomspace(dist["min"], dist["max"], 500)
        ax[0].plot(x, wb.pdf(x), c="C0")
        ax[1].plot(x, wb.cdf(x), c="C0")

        ax[0].text(
            dist["max"],
            wb.pdf(x).max(),
            "\n".join(
                [
                    rf"$\Estimated{{{s}}} = \num{{{dist[k]:.3f}}}$"
                    for s, k in [
                        (r"\Mean", "mean"),
                        (r"\StandardDeviation", "std"),
                        (r"\GammaDistributionAlpha", "shape"),
                        (r"\GammaDistributionBeta", "scale"),
                    ]
                ]
            ),
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(facecolor="white", boxstyle="round"),
        )

        fig.subplots_adjust(wspace=0.2)

        for p in produces:
            fig.savefig(p)


def task_plot_histogram_pauses_all(
    data=DATA_DIR / "duo_pauses.csv",
    dist=DATA_DIR / "duo_pauses_dist.csv",
    config=ROOT_DIR / "config.py",
    produces=[IMG_DIR / f"plot_histogram_pauses_all.{s}" for s in ["png", "pdf", "svg"]],
):
    fig: plt.Figure = plt.figure(dpi=600, figsize=(6.4, 4.5), layout="constrained")
    ax: list[plt.Axes] = fig.subplots(nrows=2, sharex="all")
    ax[0].grid(True)
    ax[0].set_ylabel("Probability Density")
    ax[0].set_xlim(2.5, 12)

    ax[1].grid(True)
    ax[1].set_ylabel("Cumulative Density")
    ax[1].set_xlabel("Pause Duration $\\Pause{\\Duration}$ in s")
    ax[1].set_ylim(0, 1.1)

    all_data = pd.read_csv(data, index_col=0)
    all_dist = pd.read_csv(dist, index_col=0)

    all_max = all_dist["max"].max()
    x = np.linspace(0, all_max, 500)

    for i in range(10):
        data = all_data.iloc[i]
        dist = all_dist.iloc[i]

        ax[0].hist(
            data,
            bins=PAUSES_BINS,
            alpha=0.5,
            density=True,
            range=(dist["min"], dist["max"]),
        )
        ax[1].hist(
            data,
            bins=PAUSES_BINS,
            alpha=0.5,
            density=True,
            cumulative=True,
            range=(dist["min"], dist["max"]),
        )

        wb = stats.weibull_min(c=dist["shape"], scale=dist["scale"])

        ax[0].plot(x, wb.pdf(x), c=f"C{i}", label=data.name)
        ax[1].plot(x, wb.cdf(x), c=f"C{i}")

    fig.legend(loc="upper right", framealpha=1)

    fig.subplots_adjust(hspace=0.1)

    for p in produces:
        fig.savefig(p)
