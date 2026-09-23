"""Board seats by gender, 1870-2026 -> figures/board_gender.pdf, .png

Seat counts rather than shares, so the 1932 expansion from three to five seats
is legible: the stack tops out at 3 before it and 5 after.

Both bands are drawn. Men are not redundant with women here - they are the
denominator, and without them two seats of five and two of three look the same.

1931 is missing in the source and appears as a gap rather than a zero.
Half-height segments are genuine: a member left mid-year and was replaced.
"""
import pandas as pd
import matplotlib.pyplot as plt

import files
import seats
import style

style.apply()

d = pd.read_csv(files.BOARD_SEATS)
years = d["year"].to_numpy()
spans = seats.runs(d["women"].notna().to_numpy())

fig, ax = plt.subplots(figsize=style.SEATS)
seats.stacked_step(ax, years,
                   [d["women"].fillna(0).to_numpy(), d["men"].fillna(0).to_numpy()],
                   [style.WOMEN, style.MEN], ["women", "men"], spans)
seats.frame(ax, style)

ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False,
          handlelength=1.2, columnspacing=1.6, handletextpad=0.35)

files.save(fig, "board_gender")
