"""How exactly the sitting Board's homes are known, 1870-2026
-> figures/board_residence_coverage.pdf, .png

A stacked step area of the members sitting on 1 July of each year, by the
most exact place any source gives for them, darkest for a house on a street
and lightest for a side of the County or a magisterial district of
Alexandria County, with the 1932 rule. Years with no roster are filled from
the seat table: the Board had three seats, one per magisterial district,
and nobody is known to sit in them, so they count at district precision
(docs/board.md, Residence in the district). A place is counted whenever it is
dated, so a member whose only place comes from after their service still
counts.
"""
import pandas as pd

import charts
import members
import paths
import style

# The grades of precision data/clean/board_residence.csv records, most exact first.
ORDER = ["address", "street", "neighborhood", "side", "district"]
# The grades one shade shows. A side of the County and a magisterial
# district are the same grade of knowledge, told apart only by the era of
# the source, so they read as one; docs/figures.md.
SHOWN = {"address": ["address"], "street": ["street"], "neighborhood": ["neighborhood"],
         "side_or_district": ["side", "district"], "none": ["none"]}
PLACED = [k for k in SHOWN if k != "none"]

claims = pd.read_csv(paths.BOARD_RESIDENCE, dtype=str).fillna("")
exactness = claims.precision.map(ORDER.index)
best = exactness.groupby(claims.name).min().map(lambda r: ORDER[int(r)])

seats = pd.read_csv(paths.BOARD_SEATS).set_index("year")
seats = (seats.men + seats.women).fillna(0).astype(int)

rows = []
for year, s in members.by_year():
    found = s.name.map(best).fillna("none")
    row = {"year": year, **{k: int((found == k).sum()) for k in ORDER + ["none"]}}
    if s.empty:
        row["district"] = int(seats.get(year, 0))
    rows.append(row)
graded = pd.DataFrame(rows)
d = pd.DataFrame({"year": graded.year, **{k: graded[cols].sum(axis=1) for k, cols in SHOWN.items()}})
if d[PLACED].sum().sum() == 0:
    raise ValueError("no sitting member has a place; nothing to draw")

for profile in style.PROFILES:
    style.apply(profile)
    spans = charts.runs((d[list(SHOWN)].sum(axis=1) > 0).to_numpy())
    series = charts.series(d, style.RESIDENCE)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d.year.to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, members.FIRST, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    charts.legend(fig, series, ncol=3)
    paths.save(fig, "board_residence_coverage", profile)
