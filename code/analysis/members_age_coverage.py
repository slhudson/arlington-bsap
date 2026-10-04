"""How many seat-years have a member with a birth year, 1900-2026
-> figures/members_age_coverage.pdf, .png

A stacked step area of the seat-years in each year, those held by a member
with a birth year and those without, with the 1932 rule. Seat-years are
read from members_by_year, like every figure on the seat axis, so a vacancy
is a dip below the seats that exist.
"""

import charts
import members
import paths
import style

d = paths.read("members_by_year")
d = d[d.year >= members.AGE_FIRST].rename(
    columns={"birth_year_known": "known", "birth_year_unknown": "unknown"})[["year", "known", "unknown"]]
d = d.reset_index(drop=True)
if d.known.sum() == 0:
    raise ValueError("no sitting member has a birth year; nothing to draw")

for profile in style.PROFILES:
    style.apply(profile)
    spans = charts.runs(((d.known + d.unknown) > 0).to_numpy())
    series = charts.series(d, style.AGE_COVERAGE)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d.year.to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, members.AGE_FIRST, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    charts.legend(fig, series)
    paths.save(fig, profile)
