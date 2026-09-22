"""Arlington County residents by race/ethnicity (raw census counts, log-scale line chart), 1870-2020."""
import numpy as np, pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator, NullLocator

SRC = "/mnt/user-data/uploads/arlington_county_demographic_data.xlsx"
OUT = "/mnt/user-data/outputs/arlington_residents_by_race_log"

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8, "pdf.fonttype": 42,
})

c = pd.read_excel(SRC).iloc[:, :6]
c.columns = ["year", "total", "white", "black", "hisp", "aapi"]
c = c[pd.to_numeric(c["year"], errors="coerce").notna()].apply(pd.to_numeric, errors="coerce")
# blanks ("." in the sheet) stay NaN: a group's line starts when the census first reports it

series = [("total", "Total population",               "#555555", (0, (5, 2)), "o"),
          ("white", "White",                          "#A3997F", "-",         "o"),
          ("black", "Black",                          "#E69F00", "-",         "o"),
          ("hisp",  "Hispanic/Latino",                 "#009E73", "-",        "o"),
          ("aapi",  "Asian American/Pacific Islander",  "#CC79A7", "-",       "o")]

fig, ax = plt.subplots(figsize=(6.5, 4.6))
for col, lab, colr, ls, mk in series:
    ax.plot(c["year"], c[col], color=colr, ls=ls, lw=1.6, marker=mk, ms=4, label=lab, zorder=3)

ax.set_yscale("log")
ax.set_ylim(30, 400000); ax.set_xlim(1866, 2025)
ticks = [100, 1000, 10000, 100000]
ax.yaxis.set_major_locator(FixedLocator(ticks)); ax.yaxis.set_minor_locator(NullLocator())
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_xticks(range(1870, 2021, 10)); ax.tick_params(axis="x", labelsize=8)
ax.set_ylabel("Residents (log scale)"); ax.set_xlabel("Census year")
ax.grid(axis="y", color="#DDDDDD", lw=0.5, zorder=0)
for s in ("top", "right"): ax.spines[s].set_visible(False)

ax.legend(loc="upper left", frameon=False, handlelength=2.2, bbox_to_anchor=(0.0, 0.98))

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
print("ok")
