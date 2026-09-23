"""Residents and residents per Board seat, 1870-2020 -> figures/residents_per_seat.pdf, .png

Two series on one linear axis. Both are counts of people, so the vertical
distance between them means the same thing everywhere on the page - which a
second y-axis would not give: the Board held three seats before 1932 and five
after, so no single right-hand scale is right for the whole series, and the
choice of one would decide which era looks like the exception.

Levels, not logs. The cube-root-law benchmark this figure used to carry is in
the history of this file; whether it belongs anywhere in the report is open,
and the reference class - national parliaments - is the objection to it.

Each line is named at its own end with its final value, so the figure needs no
legend and no axis label repeating what the lines already say.
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import files
import style

style.apply()

d = pd.read_csv(files.RESIDENTS)[["year", "total", "residents_per_seat"]].dropna()
d.columns = ["year", "pop", "rps"]
last = d.iloc[-1]

POP = "#8C6E54"

fig, ax = plt.subplots(figsize=style.PER_SEAT)
for col, colr in (("pop", POP), ("rps", style.ACTUAL)):
    ax.plot(d.year, d[col], color=colr, lw=1.8, marker="o", ms=4, zorder=3)

# Room on the right for the end labels, which sit outside the data.
ax.set_xlim(1865, 2046)
ax.set_ylim(0, 250000)                      # a round top, rather than a bare one
ax.set_xticks(range(1870, 2021, 10))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_ylabel("residents"); ax.set_xlabel("census year")
ax.grid(axis="y", color=style.GRID, lw=0.5, zorder=0); ax.set_axisbelow(True)
style.despine(ax)

for y, colr, name in ((last["pop"], POP, "total population"),
                      (last.rps, style.ACTUAL, "residents per\nBoard seat")):
    ax.text(2023, y, f"{name}\n{int(round(y)):,}", color=colr, fontsize=style.NOTE,
            ha="left", va="center", linespacing=1.3)

ax.plot([style.EXPANSION_YEAR] * 2, [0, 0.98], transform=ax.get_xaxis_transform(),
        clip_on=False, zorder=5, **style.EXPANSION_LINE)
ax.text(1936, 0.975, style.EXPANSION_NOTE, transform=ax.get_xaxis_transform(),
        ha="left", va="top", fontsize=style.NOTE)

files.save(fig, "residents_per_seat")
