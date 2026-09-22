"""Arlington County residents by race/ethnicity (log-scale lines), 1870-2020.

Each line begins the year its category is first reported, rather than being
read as zero beforehand - the opposite of the stacked figures. See
docs/questions.md Q2.

The log scale is what makes the early crossover visible: Black residents
outnumbered White residents in 1870 and 1880.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

# Append, never insert: build/ also has a paths.py, and putting it first would
# shadow this directory's own paths.py - handing analysis a route to raw/.
sys.path.append(str(Path(__file__).resolve().parents[1] / "build"))
import style
from paths import DEMOGRAPHICS, out

style.apply()
OUT = out("arlington_residents_by_race_log")

# No not_reported_as_zero here: blanks stay missing, so each line starts when
# the census first reports that category.
c = pd.read_csv(DEMOGRAPHICS)

series = [("total", "Total population", style.TOTAL_LINE, (0, (5, 2))),
          ("white", "White", style.WHITE_LINE, "-"),
          ("black", "Black", style.BLACK, "-"),
          ("hisp", "Hispanic/Latino", style.HISP, "-"),
          ("aapi", "Asian American/Pacific Islander", style.AAPI, "-")]

fig, ax = plt.subplots(figsize=(6.5, 4.6))
for col, lab, colr, ls in series:
    ax.plot(c["year"], c[col], color=colr, ls=ls, lw=1.6, marker="o", ms=4, label=lab, zorder=3)

ax.set_yscale("log")
ax.set_ylim(30, 400000); ax.set_xlim(1866, 2025)
ax.yaxis.set_major_locator(FixedLocator([100, 1000, 10000, 100000]))
ax.yaxis.set_minor_locator(NullLocator())
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_xticks(range(1870, 2021, 10)); ax.tick_params(axis="x", labelsize=8)
ax.set_ylabel("Residents (log scale)"); ax.set_xlabel("Census year")
ax.grid(axis="y", color=style.GRID, lw=0.5, zorder=0)
style.despine(ax)
ax.legend(loc="upper left", frameon=False, handlelength=2.2, bbox_to_anchor=(0.0, 0.98))

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
print("ok")
