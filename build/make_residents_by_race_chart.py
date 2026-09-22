"""Arlington County residents by race/ethnicity (raw census counts, stacked bars), 1870-2020.
Tall format (figure is twice as high as it is wide) so the early decades are visible."""
import numpy as np, pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator

from paths import DEMOGRAPHICS as SRC, out

OUT = out("arlington_residents_by_race")

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8, "pdf.fonttype": 42,
})

c = pd.read_excel(SRC).iloc[:, :6]
c.columns = ["year", "total", "white", "black", "hisp", "aapi"]
c = c[pd.to_numeric(c["year"], errors="coerce").notna()].apply(pd.to_numeric, errors="coerce")

groups = ["black", "hisp", "aapi", "white"]
colors = ["#E69F00", "#009E73", "#CC79A7", "#D9D3C4"]
labels = ["Black", "Hispanic/Latino", "Asian American/Pacific Islander", "White"]
for g in groups:
    c[g + "_n"] = c[g].fillna(0)                        # blank = not separately reported
c["sum"] = c[[g + "_n" for g in groups]].sum(axis=1)
c["other_n"] = (c["total"] - c["sum"]).clip(lower=0)    # multiracial / other / unreported
# Counts are plotted as reported. In 1970 and 1990 the categories overlap slightly,
# so those stacks exceed the total population (by ~2.8% and ~0.2%).

W, H = 4.0, 8.0                                         # 1 : 2  (width : height), inches
fig, ax = plt.subplots(figsize=(W, H))
bottom = np.zeros(len(c))
for g, colr in zip(groups, colors):
    ax.bar(c["year"], c[g + "_n"], bottom=bottom, width=7, color=colr, edgecolor="white", linewidth=0.4)
    bottom += c[g + "_n"].to_numpy()
ax.bar(c["year"], c["other_n"], bottom=bottom, width=7, color="#E6E6E6",
       edgecolor="#8C8C8C", linewidth=0.4, hatch="////")
top = bottom + c["other_n"].to_numpy()

# total population printed above each bar
for yr, tot, t in zip(c["year"], c["total"], top):
    ax.text(yr, t + 2500, f"{int(tot):,}", rotation=90, ha="center", va="bottom",
            fontsize=7, color="#444444")

ax.set_xlim(1866, 2025); ax.set_ylim(0, 285000)
ax.yaxis.set_major_locator(MultipleLocator(50000))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_xticks(range(1870, 2021, 10)); ax.tick_params(axis="x", labelsize=8, labelrotation=90)
ax.set_ylabel("Residents"); ax.set_xlabel("Census year")
for s in ("top", "right"): ax.spines[s].set_visible(False)

hand = [Patch(fc=col, label=lab) for col, lab in zip(colors, labels)]
hand.append(Patch(fc="#E6E6E6", ec="#8C8C8C", hatch="////", lw=0.4, label="Other/multiracial/unreported"))
ax.legend(handles=hand[::-1], loc="upper left", frameon=False, handlelength=1.2,
          bbox_to_anchor=(0.0, 1.0), fontsize=7.5)

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
