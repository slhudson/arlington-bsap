"""Residents per Board seat against the cube-root-law benchmark, 1870-2020.

The benchmark is population divided by the cube root of population - the
residents per seat that would obtain if the Board's size followed the cube-root
law. The log axis is necessary because the benchmark is roughly a tenth of the
actual figure; a linear axis would flatten it.
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

style.apply(legend_fontsize=8.5)
OUT = out("arlington_residents_per_seat")

d = pd.read_csv(DEMOGRAPHICS)[
    ["year", "total", "board_seats", "residents_per_seat", "cube_root_resident_ratio"]
].dropna().reset_index(drop=True)
d.columns = ["year", "pop", "seats", "rps", "benchmark"]

fig, ax = plt.subplots(figsize=style.PER_SEAT)
ax.fill_between(d.year, d.benchmark, d.rps, color=style.GAP, lw=0, zorder=1)

for col, colr, ls, lab in [("rps", style.ACTUAL, "-", "Actual residents per seat"),
                           ("benchmark", style.BENCHMARK, (0, (5, 2)), "Cube-root-law benchmark")]:
    ax.plot(d.year, d[col], color=colr, ls=ls, lw=1.6, marker="o", ms=4, label=lab, zorder=3)

ax.set_yscale("log")
ax.set_ylim(150, 70000); ax.set_xlim(1865, 2027)
ax.yaxis.set_major_locator(FixedLocator([200, 500, 1000, 2000, 5000, 10000, 20000, 50000]))
ax.yaxis.set_minor_locator(NullLocator())
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_xticks(range(1870, 2021, 10), minor=False)
ax.tick_params(axis="x", labelsize=8)
ax.set_ylabel("Residents per Board seat (log scale)"); ax.set_xlabel("Census year")
ax.grid(axis="y", color=style.GRID, lw=0.5, zorder=0)
style.despine(ax)

last = d.iloc[-1]
ax.annotate(f"{int(round(last.rps)):,}", (last.year, last.rps), xytext=(-4, 6),
            textcoords="offset points", ha="right", fontsize=8, color=style.ACTUAL)
ax.annotate(f"{int(round(last.benchmark)):,}", (last.year, last.benchmark), xytext=(-4, -13),
            textcoords="offset points", ha="right", fontsize=8, color=style.BENCHMARK)

ax.plot([style.EXPANSION_YEAR, style.EXPANSION_YEAR], [0, 1.16],
        transform=ax.get_xaxis_transform(), clip_on=False, zorder=5, **style.EXPANSION_LINE)
ax.text(1936, 1.045, style.EXPANSION_NOTE, transform=ax.get_xaxis_transform(),
        ha="left", va="bottom", fontsize=8.5, linespacing=1.3)

ax.legend(loc="lower right", frameon=False, handlelength=2.2)

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
print(d.assign(ratio=(d.rps / d.benchmark).round(1)).round(0).to_string())
