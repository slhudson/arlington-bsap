"""Board seats by race/ethnicity, 1870-2026 -> figures/board_race.pdf, .png

Was the first panel of board_seats; gender is now board_gender, the same size
and scale, so the two read as a pair rather than as one figure asking two
questions.

Seat counts rather than shares, so the 1932 expansion from three to five seats
is legible: the stack tops out at 3 before it and 5 after.

A category that holds no seat in any year gets no band and no legend entry: an
empty swatch reads as a sliver too small to see rather than as zero, and the
absence belongs in the prose. That no Asian American or Pacific Islander member
has served is a finding, and a finding is a sentence, not a blank key. The test
is on the data rather than on the category name, so a future member restores
the band without an edit here.

1931 is missing in the source and appears as a gap rather than a zero. The gap
logic is in seats.py, shared with board_gender. Half-height segments are
genuine: a member left mid-year and was replaced.
"""
import pandas as pd
import matplotlib.pyplot as plt

import files
import seats
import style

style.apply()

d = pd.read_csv(files.BOARD_SEATS)
years = d["year"].to_numpy()
spans = seats.runs(d["white"].notna().to_numpy())

held = [(g, c, l) for g, c, l in zip(style.GROUPS, style.GROUP_COLORS, style.GROUP_LABELS)
        if d[g].fillna(0).sum() > 0]
assert held, "no seat is attributed to any race category - check the build"

fig, ax = plt.subplots(figsize=style.SEATS)
seats.stacked_step(ax, years,
                   [d[g].fillna(0).to_numpy() for g, _, _ in held],
                   [c for _, c, _ in held], [l for _, _, l in held], spans)
seats.frame(ax, style)

ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=len(held),
          frameon=False, handlelength=1.2, columnspacing=1.6, handletextpad=0.35)

files.save(fig, "board_race")
