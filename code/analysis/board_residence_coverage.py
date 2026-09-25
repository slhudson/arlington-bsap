"""How exactly the sitting Board's homes are known, 1870-2026
-> figures/board_residence_coverage.pdf, .png

A stacked step area of the members sitting on 1 July of each year, by the
most exact place any source gives for them, darkest for a house on a street
and lightest for a side of the County, with the 1932 rule. Years with no
roster are gaps. A place is counted whenever it is dated, so a member whose
only place comes from after their service still counts.
"""
import pandas as pd

import charts
import members
import paths
import style

ORDER = ["address", "street", "neighborhood", "side"]

claims = pd.read_csv(paths.BOARD_RESIDENCE, dtype=str).fillna("")
exactness = claims.precision.map(ORDER.index)
best = exactness.groupby(claims.name).min().map(lambda r: ORDER[int(r)])

rows = []
for year, s in members.by_year():
    found = s.name.map(best).fillna("none")
    rows.append({"year": year, **{k: int((found == k).sum()) for k in ORDER + ["none"]}})
d = pd.DataFrame(rows)
if d[ORDER].sum().sum() == 0:
    raise ValueError("no sitting member has a place; nothing to draw")

for profile in style.PROFILES:
    style.apply(profile)
    spans = charts.runs(((d[ORDER + ["none"]]).sum(axis=1) > 0).to_numpy())
    series = charts.series(d, style.RESIDENCE)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d.year.to_numpy(), series, spans)
    charts.seats(ax, label="members sitting")
    charts.years(ax, members.FIRST, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS)
    charts.legend(fig, series)
    paths.save(fig, "board_residence_coverage", profile)
