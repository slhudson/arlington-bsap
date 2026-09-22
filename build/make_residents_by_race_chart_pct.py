"""Arlington County residents by race/ethnicity (share of residents, stacked bars), 1870-2020."""
import numpy as np, pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter, MultipleLocator

from paths import DEMOGRAPHICS as SRC, out

OUT = out("arlington_residents_by_race_pct")

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
    c[g + "_pct"] = 100 * c[g].fillna(0) / c["total"]    # blank = not separately reported
c["sum"] = c[[g + "_pct" for g in groups]].sum(axis=1)
c["other_pct"] = (100 - c["sum"]).clip(lower=0)          # multiracial / other / unreported
over = c["sum"] > 100                                    # 1970, 1990: categories overlap slightly
for g in groups:
    c.loc[over, g + "_pct"] *= 100 / c.loc[over, "sum"]  # rescale so bar totals 100%

fig, ax = plt.subplots(figsize=(6.5, 4.6))
bottom = np.zeros(len(c))
for g, colr in zip(groups, colors):
    ax.bar(c["year"], c[g + "_pct"], bottom=bottom, width=7, color=colr, edgecolor="white", linewidth=0.4)
    bottom += c[g + "_pct"].to_numpy()
ax.bar(c["year"], c["other_pct"], bottom=bottom, width=7, color="#E6E6E6",
       edgecolor="#8C8C8C", linewidth=0.4, hatch="////")

ax.set_xlim(1866, 2025); ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.set_xticks(range(1870, 2021, 10)); ax.tick_params(axis="x", labelsize=8)
ax.set_ylabel("Share of residents"); ax.set_xlabel("Census year")
for s in ("top", "right"): ax.spines[s].set_visible(False)

hand = [Patch(fc=col, label=lab) for col, lab in zip(colors, labels)]
hand.append(Patch(fc="#E6E6E6", ec="#8C8C8C", hatch="////", lw=0.4, label="Other/multiracial/unreported"))
ax.legend(handles=hand, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False,
          handlelength=1.2, columnspacing=1.0, handletextpad=0.4, fontsize=7.5)

fig.savefig(OUT + ".pdf", bbox_inches="tight")
fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
print("ok")
