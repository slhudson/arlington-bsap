"""Residents by race/ethnicity, log-scale lines, 1870-2020.

No assumption from code/build/assumptions.py is applied here: blanks stay missing,
so each line begins the year its category is first reported. That is the
opposite of the stacked figures - see docs/questions.md.

The log scale is what makes the early crossover visible: Black residents
outnumbered White residents in 1870 and 1880.
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

import files
import style

style.apply()

c = pd.read_csv(files.RESIDENTS)

series = [("total", "Total population", style.TOTAL_LINE, (0, (5, 2))),
          ("white", "White", style.WHITE_LINE, "-"),
          ("black", "Black", style.BLACK, "-"),
          ("hisp", "Hispanic/Latino", style.HISP, "-"),
          ("aapi", "Asian American/Pacific Islander", style.AAPI, "-")]

fig, ax = plt.subplots(figsize=style.WIDE)
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

files.save(fig, "residents_by_race_log")
