"""Residents by race/ethnicity, share of residents, stacked bars, 1870-2020.

The 1970 column is rescaled to sum to 100%; from 1980 the categories do not
overlap and nothing is rescaled. This figure and residents_by_race.py therefore
treat that one year's overlap differently - see docs/questions.md.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, PercentFormatter

import files
import style

files.build_stage_on_path()
from assumptions import not_reported_as_zero, rescale_to_100   # noqa: E402

style.apply()

c = pd.read_csv(files.RESIDENTS)
c = not_reported_as_zero(c)                        # not-reported read as zero
shares = c[style.GROUPS].div(c["total"], axis=0) * 100
other = (100 - shares.sum(axis=1)).clip(lower=0)   # computed before rescaling
shares = rescale_to_100(shares)                    # the 1970 overlap

fig, ax = plt.subplots(figsize=style.WIDE)
bottom = np.zeros(len(c))
for g, colr in zip(style.GROUPS, style.GROUP_COLORS):
    ax.bar(c["year"], shares[g], bottom=bottom, width=7, color=colr, edgecolor="white", linewidth=0.4)
    bottom += shares[g].to_numpy()
ax.bar(c["year"], other, bottom=bottom, width=7, color=style.OTHER,
       edgecolor=style.OTHER_EDGE, linewidth=0.4, hatch="////")

ax.set_xlim(1866, 2025); ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.set_xticks(range(1870, 2021, 10)); ax.tick_params(axis="x", labelsize=8)
ax.set_ylabel("Share of residents"); ax.set_xlabel("Census year")
style.despine(ax)

hand = [Patch(fc=col, label=lab) for col, lab in zip(style.GROUP_COLORS, style.GROUP_LABELS)]
hand.append(Patch(fc=style.OTHER, ec=style.OTHER_EDGE, hatch="////", lw=0.4,
                  label="Other/multiracial/unreported"))
ax.legend(handles=hand, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False,
          handlelength=1.2, columnspacing=1.0, handletextpad=0.4, fontsize=7.5)

files.save(fig, "residents_by_race_share")
