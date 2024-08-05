import itertools
from copy import deepcopy

import matplotlib.gridspec as gs
import matplotlib.pyplot as plt
import pyroll.core as pr

from weiner_variation.config import IMG_DIR, SIM_DIR
from weiner_variation.sim.process import IN_PROFILE, PASS_SEQUENCE

FILE_STEM = "plot_pass_sequence"
FILE_TYPES = ["png", "svg", "pdf"]


def task_plot_pass_sequence(
    process_file=SIM_DIR / "process.py",
    produces=[IMG_DIR / f"{FILE_STEM}.{t}" for t in FILE_TYPES],
):
    fig: plt.Figure = plt.figure(dpi=600, figsize=(6.4, 3), layout="constrained")

    gs_rows = gs.GridSpec(3, 1, figure=fig, height_ratios=[2, 1.5, 1])
    gs0 = gs.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs_rows[0])
    gs1 = gs.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs_rows[1])
    gs2 = gs.GridSpecFromSubplotSpec(1, 6, subplot_spec=gs_rows[2])

    cells = itertools.chain(gs0, gs1, gs2)

    axs: list[plt.Axes] = [fig.add_subplot(c) for c in cells]

    sequence = deepcopy(PASS_SEQUENCE)
    sequence.solve(IN_PROFILE)
    roll_passes = [u for u in sequence if isinstance(u, pr.RollPass)]

    for ax in axs:
        ax.set_adjustable("box")
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xmargin(0.05)
        ax.set_ymargin(0.05)

    for ax, rp in zip(axs, roll_passes, strict=False):
        ax.set_title(rp.label)

        for c in rp.contour_lines:
            ax.plot(*c.xy, c="k", lw=1)

        ax.fill(*rp.in_profile.cross_section.boundary.xy, c="r", alpha=0.5, lw=1)
        ax.fill(*rp.out_profile.cross_section.boundary.xy, c="b", alpha=0.5, lw=1)

    for ax in axs[:4]:
        ax.sharex(axs[2])
        ax.sharey(axs[3])

    for ax in axs[4:8]:
        ax.sharex(axs[2])
        ax.sharey(axs[5])

    for ax in axs[8:]:
        ax.sharex(axs[8])
        ax.sharey(axs[8])

    first_row_xlim = axs[0].get_xlim()
    axs[8].set_xlim(first_row_xlim[0] * 4 / 6, first_row_xlim[1] * 4 / 6)

    fig.subplots_adjust(wspace=0.1, hspace=0.1)

    for p in produces:
        fig.savefig(p)

    plt.close(fig)
