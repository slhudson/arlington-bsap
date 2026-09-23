"""Residents by race/ethnicity, 1870-2020 -> figures/residents_by_race.pdf, .png

Two panels, left and right: (a) how many residents, (b) what share of them.
Side by side rather than stacked because the levels panel needs to be taller
than it is wide for the decades before 1940 to have any height at all -
Arlington had under 27,000 residents until 1940 and 238,643 by 2020.

Was two figures. The share panel was residents_by_race_share, and the two were
always read together.

The 1970 and 1990 columns are treated differently in the two panels: (a) plots
the counts as reported, so those bars sit slightly above the county total,
while (b) rescales them to sum to 100%. Both treatments are in
code/build/assumptions.py and the disagreement is Q1 in docs/questions.md,
open pending Alex. It is not settled here.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator, PercentFormatter

import files
import style

files.build_stage_on_path()
from assumptions import not_reported_as_zero, rescale_to_100   # noqa: E402

style.apply()

c = not_reported_as_zero(pd.read_csv(files.RESIDENTS))         # not-reported read as zero
c["other"] = (c["total"] - c[style.GROUPS].sum(axis=1)).clip(lower=0)

shares = c[style.GROUPS].div(c["total"], axis=0) * 100
other_share = (100 - shares.sum(axis=1)).clip(lower=0)         # computed before rescaling
shares = rescale_to_100(shares)                                # the 1970/1990 overlap

OTHER_LABEL = "other/multiracial/unreported"


def stack(ax, frame, residual):
    bottom = np.zeros(len(c))
    for g, colr in zip(style.GROUPS, style.GROUP_COLORS):
        ax.bar(c["year"], frame[g], bottom=bottom, width=7, color=colr,
               edgecolor="white", linewidth=0.4)
        bottom += frame[g].to_numpy()
    ax.bar(c["year"], residual, bottom=bottom, width=7, color=style.OTHER,
           edgecolor=style.OTHER_EDGE, linewidth=0.4, hatch="////")


def frame(ax, title):
    ax.set_xlim(1866, 2025)
    ax.set_xticks(range(1870, 2021, 10))
    ax.tick_params(axis="x", labelrotation=90)
    ax.set_xlabel("")            # the rotated years say what the axis is
    ax.set_title(title, pad=6)
    style.despine(ax)


fig, (a, b) = plt.subplots(1, 2, figsize=style.SIDE_BY_SIDE,
                           gridspec_kw={"wspace": 0.30})

stack(a, c, c["other"])
a.set_ylim(0, 250000)            # a round top, rather than one just clear of 2020
a.yaxis.set_major_locator(MultipleLocator(50000))
a.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
a.set_ylabel("residents")
frame(a, "(a) number of residents")

stack(b, shares, other_share)
b.set_ylim(0, 100)
b.yaxis.set_major_locator(MultipleLocator(20))
b.yaxis.set_major_formatter(PercentFormatter(decimals=0))
b.set_ylabel("share of residents")
frame(b, "(b) share of residents")

hand = [Patch(fc=col, label=lab) for col, lab in zip(style.GROUP_COLORS, style.GROUP_LABELS)]
hand.append(Patch(fc=style.OTHER, ec=style.OTHER_EDGE, hatch="////", lw=0.4,
                  label=OTHER_LABEL))
fig.legend(handles=hand, loc="upper center", bbox_to_anchor=(0.5, 0.055), ncol=5,
           frameon=False, handlelength=1.0, columnspacing=1.1, handletextpad=0.35)

files.save(fig, "residents_by_race")
