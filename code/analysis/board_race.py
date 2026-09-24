"""Board seats by race/ethnicity, 1870-2026 -> figures/board_race.pdf, .png

The same size and scale as board_gender, so the two read as a pair.

A category holding no seat in any year gets no band and no legend entry: an
empty swatch reads as a sliver too small to see rather than as zero, and the
absence belongs in the prose. That no Asian American or Pacific Islander member
has served is a finding, and a finding is a sentence. The test is on the data
rather than the category name, so a future member restores the band with no
edit here.

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
    spans = charts.runs(d["white"].notna().to_numpy())
    held = [g for g in style.GROUP_ORDER if d[g].fillna(0).sum() > 0]
    assert held, "no seat is attributed to any race category - check the build"
    series = {style.GROUP_LABELS[g]: (d[g].fillna(0).to_numpy(), style.RACE_COLORS[g])
              for g in held}

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year")
    ax.set_xlim(1866, 2027)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS)
    charts.legend(fig, {style.GROUP_LABELS[g]: style.RACE_COLORS[g] for g in held})
    paths.save(fig, "board_race", profile)
