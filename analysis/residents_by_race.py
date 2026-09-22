"""Residents by race/ethnicity, census counts, stacked bars, 1870-2020.

Tall format (twice as high as wide) so the early decades have visible height.
Counts are plotted as reported, so the 1970 and 1990 bars sit slightly above
the county total. See docs/questions.md Q1.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator

import files
import style

files.build_stage_on_path()
from assumptions import not_reported_as_zero      # noqa: E402  (needs the path above)

style.apply()

c = pd.read_csv(files.RESIDENTS)
c = not_reported_as_zero(c)                       # Q2
c["sum"] = c[style.GROUPS].sum(axis=1)
c["other"] = (c["total"] - c["sum"]).clip(lower=0)

fig, ax = plt.subplots(figsize=style.TALL)
bottom = np.zeros(len(c))
for g, colr in zip(style.GROUPS, style.GROUP_COLORS):
    ax.bar(c["year"], c[g], bottom=bottom, width=7, color=colr, edgecolor="white", linewidth=0.4)
    bottom += c[g].to_numpy()
ax.bar(c["year"], c["other"], bottom=bottom, width=7, color=style.OTHER,
       edgecolor=style.OTHER_EDGE, linewidth=0.4, hatch="////")
top = bottom + c["other"].to_numpy()

for yr, tot, t in zip(c["year"], c["total"], top):
    ax.text(yr, t + 2500, f"{int(tot):,}", rotation=90, ha="center", va="bottom",
            fontsize=7, color="#444444")

ax.set_xlim(1866, 2025); ax.set_ylim(0, 285000)
ax.yaxis.set_major_locator(MultipleLocator(50000))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_xticks(range(1870, 2021, 10)); ax.tick_params(axis="x", labelsize=8, labelrotation=90)
ax.set_ylabel("Residents"); ax.set_xlabel("Census year")
style.despine(ax)

hand = [Patch(fc=col, label=lab) for col, lab in zip(style.GROUP_COLORS, style.GROUP_LABELS)]
hand.append(Patch(fc=style.OTHER, ec=style.OTHER_EDGE, hatch="////", lw=0.4,
                  label="Other/multiracial/unreported"))
ax.legend(handles=hand[::-1], loc="upper left", frameon=False, handlelength=1.2,
          bbox_to_anchor=(0.0, 1.0), fontsize=7.5)

files.save(fig, "residents_by_race")
