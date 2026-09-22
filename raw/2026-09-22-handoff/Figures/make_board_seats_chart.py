"""Arlington County Board seats by race/ethnicity and gender, 1871-2026."""
import numpy as np, pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

BOARD = "/mnt/user-data/uploads/arlington_board_-_descriptive_representation__1870-2026_.xlsx"
OUT = "/mnt/user-data/outputs/board_seats_by_race_gender"

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8, "pdf.fonttype": 42,
})

raw = pd.read_excel(BOARD)
raw.columns = ["year", "white", "black", "hisp", "aapi", "men", "women"]
d = raw.apply(pd.to_numeric, errors="coerce")           # "." -> NaN (1883, 1884, 1931)
years = d["year"].to_numpy()
valid = d["white"].notna().to_numpy()
runs, start = [], None
for i, v in enumerate(valid):
    if v and start is None: start = i
    if (not v or i == len(valid) - 1) and start is not None:
        runs.append((start, i if v else i - 1)); start = None

def stacked_step(ax, cols, colors, labels):
    """Stacked step-area of seat counts; each year's value spans [year, year+1)."""
    cum_prev = np.zeros(len(d))
    for col, colr, lab in zip(cols, colors, labels):
        top = cum_prev + d[col].fillna(0).to_numpy()
        first = True
        for a, b in runs:
            x  = np.append(years[a:b + 1], years[b] + 1)
            lo = np.append(cum_prev[a:b + 1], cum_prev[b])
            hi = np.append(top[a:b + 1], top[b])
            ax.fill_between(x, lo, hi, step="post", facecolor=colr, edgecolor="white",
                            linewidth=0.3, label=lab if first else None)
            first = False
        cum_prev = top

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.5, 6.4), sharex=True, gridspec_kw={"hspace": 0.34})

stacked_step(ax1, ["black", "hisp", "aapi", "white"],
             ["#E69F00", "#009E73", "#CC79A7", "#D9D3C4"],
             ["Black", "Hispanic/Latino", "Asian American/Pacific Islander", "White"])
stacked_step(ax2, ["women", "men"], ["#E8A598", "#A9BBCB"], ["Women", "Men"])

for ax, title in [(ax1, "(a) Race/ethnicity"), (ax2, "(b) Gender")]:
    ax.set_xlim(1866, 2027); ax.set_ylim(0, 5)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_axisbelow(False)
    ax.grid(axis="y", color="white", alpha=0.7, lw=0.5)       # seat guides over the fills
    ax.set_ylabel("Board seats"); ax.set_title(title, loc="left", fontsize=9.5, pad=4)
    ax.axvline(1932, color="black", lw=1.1, ls=(0, (4, 2)), zorder=5)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
ax2.set_xticks(range(1880, 2021, 20)); ax2.set_xlabel("Year")

# 1932 annotation above the top panel
ax1.plot([1932, 1932], [1.0, 1.26], transform=ax1.get_xaxis_transform(), color="black",
         lw=1.1, ls=(0, (4, 2)), clip_on=False, zorder=5)
ax1.text(1936, 1.05, "1932: Board expands from 3 to 5 seats;\n"
         "magisterial districts replaced by at-large elections",
         transform=ax1.get_xaxis_transform(), ha="left", va="bottom", fontsize=8.5, linespacing=1.3)

ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=4, frameon=False,
           handlelength=1.2, columnspacing=1.0, handletextpad=0.4, fontsize=7.5)
ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2, frameon=False, handlelength=1.2)

ax2.text(0.5, -0.36, "Note: Half seats occur when a Board member resigned or died before the end of the year\n"
         "and was subsequently replaced.", transform=ax2.transAxes, ha="center", va="top",
         fontsize=7.5, style="italic", linespacing=1.3)

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
print("ok")
