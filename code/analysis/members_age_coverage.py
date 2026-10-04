"""How many seat-years have a member with a birth year, 1900-2026
-> figures/members_age_coverage.pdf, .png

A stacked step area of the seat-years in each year, those held by a member
with a birth year and those without, with the 1932 rule. Seat-years are
counted as members_residence_coverage counts them (members.seat_years), so a
vacancy is a dip below the seats that exist.
"""

import charts
import members
import paths
import style

born = paths.read("members").drop_duplicates("name").set_index("name").birth_year.notna()
d = members.seat_years(lambda name: "known" if born[name] else "unknown")
d = d[d.year >= members.AGE_FIRST].reindex(columns=["year", "known", "unknown"], fill_value=0)
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
