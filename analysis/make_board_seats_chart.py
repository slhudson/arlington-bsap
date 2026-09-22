"""Arlington County Board seats by race/ethnicity and gender, 1871-2026.

Seat counts rather than shares, so the 1932 expansion from three to five seats
is legible. Half-height segments are genuine: a member left mid-year and was
replaced.

1883, 1884 and 1931 are not reported and appear as gaps rather than zeros. The
runs logic below is what produces those gaps: each unbroken stretch of reported
years is filled separately, so no band is drawn across a missing year.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# Append, never insert: build/ also has a paths.py, and putting it first would
# shadow this directory's own paths.py - handing analysis a route to raw/.
sys.path.append(str(Path(__file__).resolve().parents[1] / "build"))
import style
from paths import BOARD_COUNTS, out

style.apply()
OUT = out("board_seats_by_race_gender")

d = pd.read_csv(BOARD_COUNTS)
years = d["year"].to_numpy()
valid = d["white"].notna().to_numpy()

runs, start = [], None
for i, v in enumerate(valid):
    if v and start is None:
        start = i
    if (not v or i == len(valid) - 1) and start is not None:
        runs.append((start, i if v else i - 1)); start = None


def stacked_step(ax, cols, colors, labels):
    """Stacked step-area of seat counts; each year's value spans [year, year+1)."""
    cum_prev = np.zeros(len(d))
    for col, colr, lab in zip(cols, colors, labels):
        top = cum_prev + d[col].fillna(0).to_numpy()
        first = True
        for a, b in runs:
            x = np.append(years[a:b + 1], years[b] + 1)
            lo = np.append(cum_prev[a:b + 1], cum_prev[b])
            hi = np.append(top[a:b + 1], top[b])
            ax.fill_between(x, lo, hi, step="post", facecolor=colr, edgecolor="white",
                            linewidth=0.3, label=lab if first else None)
            first = False
        cum_prev = top


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=style.STACKED, sharex=True,
                               gridspec_kw={"hspace": 0.34})

stacked_step(ax1, style.GROUPS, style.GROUP_COLORS, style.GROUP_LABELS)
stacked_step(ax2, ["women", "men"], [style.WOMEN, style.MEN], ["Women", "Men"])

for ax, title in [(ax1, "(a) Race/ethnicity"), (ax2, "(b) Gender")]:
    ax.set_xlim(1866, 2027); ax.set_ylim(0, 5)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_axisbelow(False)
    ax.grid(axis="y", color="white", alpha=0.7, lw=0.5)       # seat guides over the fills
    ax.set_ylabel("Board seats"); ax.set_title(title, loc="left", fontsize=9.5, pad=4)
    ax.axvline(style.EXPANSION_YEAR, zorder=5, **style.EXPANSION_LINE)
    style.despine(ax)
ax2.set_xticks(range(1880, 2021, 20)); ax2.set_xlabel("Year")

ax1.plot([style.EXPANSION_YEAR, style.EXPANSION_YEAR], [1.0, 1.26],
         transform=ax1.get_xaxis_transform(), clip_on=False, zorder=5, **style.EXPANSION_LINE)
ax1.text(1936, 1.05, style.EXPANSION_NOTE, transform=ax1.get_xaxis_transform(),
         ha="left", va="bottom", fontsize=8.5, linespacing=1.3)

ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=4, frameon=False,
           handlelength=1.2, columnspacing=1.0, handletextpad=0.4, fontsize=7.5)
ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2, frameon=False, handlelength=1.2)

ax2.text(0.5, -0.36, style.HALF_SEAT_NOTE, transform=ax2.transAxes, ha="center", va="top",
         fontsize=7.5, style="italic", linespacing=1.3)

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
print("ok")
