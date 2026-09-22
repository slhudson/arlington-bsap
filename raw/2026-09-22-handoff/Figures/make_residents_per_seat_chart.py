"""Arlington County: residents per Board seat vs. cube-root-law benchmark, 1870-2020."""
import numpy as np, pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator, NullLocator, MultipleLocator

SRC = "/mnt/user-data/uploads/arlington_county_demographic_data.xlsx"
OUT = "/mnt/user-data/outputs/arlington_residents_per_seat"

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8.5, "pdf.fonttype": 42,
})

d = pd.read_excel(SRC).iloc[:, [0, 1, 6, 8, 10]]
d.columns = ["year", "pop", "seats", "rps", "benchmark"]
d = d.apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
assert np.allclose(d.rps, d["pop"] / d.seats)
assert np.allclose(d.benchmark, d["pop"] ** (2 / 3))     # residents/seat if seats = cube root of population

ACTUAL, BENCH, GAP = "#3B4A5A", "#C9794A", "#EFE6DC"

fig, ax = plt.subplots(figsize=(6.5, 4.4))

# shaded gap between actual and benchmark
ax.fill_between(d.year, d.benchmark, d.rps, color=GAP, lw=0, zorder=1)

for col, colr, ls, lab in [("rps", ACTUAL, "-", "Actual residents per seat"),
                           ("benchmark", BENCH, (0, (5, 2)), "Cube-root-law benchmark")]:
    ax.plot(d.year, d[col], color=colr, ls=ls, lw=1.6, marker="o", ms=4, label=lab, zorder=3)

ax.set_yscale("log")
ax.set_ylim(150, 70000); ax.set_xlim(1865, 2027)
ticks = [200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
ax.yaxis.set_major_locator(FixedLocator(ticks)); ax.yaxis.set_minor_locator(NullLocator())
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_xticks(range(1870, 2021, 10), minor=False)
ax.tick_params(axis="x", labelsize=8)
ax.set_ylabel("Residents per Board seat (log scale)"); ax.set_xlabel("Census year")
ax.grid(axis="y", color="#DDDDDD", lw=0.5, zorder=0)
for s in ("top", "right"): ax.spines[s].set_visible(False)

# end-point labels
last = d.iloc[-1]
ax.annotate(f"{int(round(last.rps)):,}", (last.year, last.rps), xytext=(-4, 6),
            textcoords="offset points", ha="right", fontsize=8, color=ACTUAL)
ax.annotate(f"{int(round(last.benchmark)):,}", (last.year, last.benchmark), xytext=(-4, -13),
            textcoords="offset points", ha="right", fontsize=8, color=BENCH)

# 1932 reference (same treatment as the Board figure)
ax.plot([1932, 1932], [0, 1.16], transform=ax.get_xaxis_transform(), color="black",
        lw=1.1, ls=(0, (4, 2)), clip_on=False, zorder=5)
ax.text(1936, 1.045, "1932: Board expands from 3 to 5 seats;\n"
        "magisterial districts replaced by at-large elections",
        transform=ax.get_xaxis_transform(), ha="left", va="bottom", fontsize=8.5, linespacing=1.3)

ax.legend(loc="lower right", frameon=False, handlelength=2.2)

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
print(d.assign(ratio=(d.rps / d.benchmark).round(1)).round(0).to_string())
