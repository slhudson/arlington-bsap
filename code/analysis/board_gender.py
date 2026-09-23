"""Board seats by gender, 1870-2026 -> figures/board_gender.pdf, .png

Seat counts rather than shares, so the 1932 expansion from three to five seats
is legible: the stack tops out at 3 before it and 5 after.

Both bands are drawn. Men are not redundant with women here - they are the
denominator, and without them two seats of five and two of three look the same.
The neutral goes to the larger group, as it does on the race figures.

1931 is missing in the source and appears as a gap rather than a zero.
Half-height segments are genuine: a member left mid-year and was replaced.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.BOARD_SEATS)
    spans = charts.runs(d["women"].notna().to_numpy())
    series = {style.GENDER_LABELS[g]: (d[g].fillna(0).to_numpy(), style.GENDER_COLORS[g])
              for g in style.GENDER_ORDER}

    fig, ax = charts.figure(style.SEATS, profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, 1880, 2020, step=20, label="year")
    ax.set_xlim(1866, 2027)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS)
    charts.legend(fig, {style.GENDER_LABELS[g]: style.GENDER_COLORS[g]
                        for g in style.GENDER_ORDER})
    paths.save(fig, "board_gender", profile)
