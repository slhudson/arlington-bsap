"""How exactly the sitting Board's homes are known, 1870-2026
-> figures/members_residence_coverage.pdf, .png

A stacked step area of seat-years, by the most exact place any source gives
for the person holding the seat, darkest for a house on a street and lightest
for a side of the County or a magisterial district of Alexandria County, with
the 1932 rule. Each year is the average, over the months the Board existed,
of the members seated that month, so a vacancy is a dip below the seats that
exist and a member who served part of a year counts that part; the yearly
total is the men + women of members_by_year. A place is counted whenever it
is dated, so a member whose only place comes from after their service still
counts. A seat-year is fractional wherever a member served part of a year, so
the bands carry fractions of a seat.
"""
import pandas as pd

import charts
import paths
import style

# The grades of precision data/clean/members_residence.csv records, most exact first.
ORDER = ["address", "street", "neighborhood", "side", "district"]
# The grades one shade shows. A side of the County and a magisterial
# district are the same grade of knowledge, told apart only by the era of
# the source, so they read as one; docs/figures.md.
SHOWN = {"address": ["address"], "street": ["street"], "neighborhood": ["neighborhood"],
         "side_or_district": ["side", "district"], "none": ["none"]}
PLACED = [k for k in SHOWN if k != "none"]

claims = paths.read("members_residence", dtype=str).fillna("")
exactness = claims.precision.map(ORDER.index)
best = exactness.groupby(claims.name).min().map(lambda r: ORDER[int(r)])

# One row per name, the months its terms held, read the way members_by_year
# reads them: a district seat ends when the Board went at large.
terms = paths.read("members")
by_year = paths.read("members_by_year")
end = (int(by_year.year.max()) + 1) * 12      # terms run past the year the roster was checked to
at_large_from = terms.loc[terms.district == "at large", "held_from"].min()
terms = terms.assign(held_to=terms.held_to.where(terms.district == "at large",
                                                 terms.held_to.clip(upper=at_large_from)))
terms["held_to"] = terms.held_to.clip(upper=end)
terms = terms[terms.held_to > terms.held_from]
first_month, last_month = int(terms.held_from.min()), int(terms.held_to.max())

grade = {k: [] for k in ORDER + ["none"]}
per_month = []
for month in range(first_month, last_month):
    sitting = terms[(terms.held_from <= month) & (month < terms.held_to)].drop_duplicates("name")
    found = sitting.name.map(best).fillna("none")
    per_month.append({"year": month // 12, **{k: int((found == k).sum()) for k in grade}})
monthly = pd.DataFrame(per_month)
# 1870 is averaged over the months the Board existed, every other year over twelve.
months_existing = monthly.groupby("year").size().clip(upper=12)
graded = monthly.groupby("year").sum().div(months_existing, axis=0).reset_index()

# The yearly totals are the seats members_by_year counts, men + women.
seats_held = by_year.set_index("year")[["men", "women"]].sum(axis=1)
total = graded.set_index("year")[list(grade)].sum(axis=1)
off = (total - seats_held.reindex(total.index)).abs() > 1e-9
if off.any() or set(total.index) != set(seats_held.index):
    raise AssertionError(
        "seat-years here and in members_by_year differ in "
        f"{list(total.index[off])}; the years differ by {set(total.index) ^ set(seats_held.index)}")

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
