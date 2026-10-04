"""How exactly the sitting Board's homes are known, 1870-2026
-> figures/members_residence_coverage.pdf, .png

A stacked step area of seat-years, by the most exact place any source gives
for the person holding the seat, darkest for a house on a street and lightest
for a side of the County or a magisterial district of Alexandria County, with
the 1932 rule. Seat-years are read from members_by_year, like every figure on
the seat axis, so a vacancy is a dip below the seats that exist and a member
who served part of a year counts that part. A place is counted whenever it
is dated, so a member whose only place comes from after their service still
counts. A seat-year is fractional wherever a member served part of a year, so
the bands carry fractions of a seat.
"""
import pandas as pd

import charts
import paths
import style

# The grades one shade shows. A side of the County and a magisterial
# district are the same grade of knowledge, told apart only by the era of
# the source, so they read as one; docs/figures.md.
SHOWN = {"address": ["address"], "street": ["street"], "neighborhood": ["neighborhood"],
         "side_or_district": ["side", "district"], "none": ["no_place"]}
PLACED = [k for k in SHOWN if k != "none"]

graded = paths.read("members_by_year")

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
    charts.years(ax, int(graded.year.min()), 2020, step=20, label="year", through=int(graded.year.max()) + 1)
    charts.rule(ax)
    charts.legend(fig, series, ncol=3)
    paths.save(fig, profile)
