"""Arlington County residents by race/ethnicity (share of residents), 1870-2020.

The 1970 and 1990 columns are rescaled to sum to 100%. This figure and the
count version therefore treat the same overlap differently - see
docs/questions.md Q1, which is unresolved.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, PercentFormatter

# Append, never insert: build/ also has a paths.py, and putting it first would
# shadow this directory's own paths.py - handing analysis a route to raw/.
sys.path.append(str(Path(__file__).resolve().parents[1] / "build"))
import style
from conventions import not_reported_as_zero, rescale_overlapping_years
from paths import DEMOGRAPHICS, out

style.apply()
OUT = out("arlington_residents_by_race_pct")

c = pd.read_csv(DEMOGRAPHICS)
c = not_reported_as_zero(c)                        # Q2
shares = c[style.GROUPS].div(c["total"], axis=0) * 100
other = (100 - shares.sum(axis=1)).clip(lower=0)   # before rescaling
shares = rescale_overlapping_years(shares)         # Q1

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

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
