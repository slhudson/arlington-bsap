"""Board seats by party, 1932-2026 -> figures/board_party.pdf, .png

The same frame, scale and 1932 rule as board_race and board_gender, so the
three read as a set. It begins where the record does: no source names a
party for the magisterial-district Board, so 1870-1931 is a gap rather than a
band, exactly as 1931 is on the other two.

What "party" means here is in docs/board.md. Party has never been
printed on the County Board ballot, so a band is whose candidate a member
was - the county's own record where it gives one, reporting where it does
not - and "not recorded" is a member for whom neither says.

A category holding no seat in any year gets no band and no legend entry, as
on board_race. Half-height segments are genuine: a member left mid-year and
was replaced.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.BOARD_SEATS)
    spans = charts.runs(d["dem"].notna().to_numpy())
    held = [g for g in style.PARTY_ORDER if d[g].fillna(0).sum() > 0]
    assert held, "no seat is attributed to any party category - check the build"
    series = {style.PARTY_LABELS[g]: (d[g].fillna(0).to_numpy(), style.PARTY_COLORS[g])
              for g in held}

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year", through=2027)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS)
    charts.legend(fig, {style.PARTY_LABELS[g]: style.PARTY_COLORS[g] for g in held})
    paths.save(fig, "board_party", profile)
