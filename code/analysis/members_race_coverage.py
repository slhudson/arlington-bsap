"""How many seat-years rest on the era default for race, 1870-2026
-> figures/members_race_coverage.pdf, .png

A stacked step area of the seat-years in each year, those held by a member
whose race comes from a source and those held by one whose race is the era
default, with the 1932 rule. Seat-years are read from members_by_year, like
every figure on the seat axis, so a vacancy is a dip below the seats that
exist and a member who served part of a year counts that part.
"""
import charts
import paths
import style

d = paths.read("members_by_year")
d = d[["year", "race_known", "race_default"]].rename(
    columns={"race_known": "known", "race_default": "default"}).reset_index(drop=True)
if d.default.sum() == 0:
    raise ValueError("no sitting member's race rests on the default; nothing to draw")

for profile in style.PROFILES:
    style.apply(profile)
    spans = charts.runs(((d.known + d.default) > 0).to_numpy())
    series = charts.series(d, style.RACE_BASIS)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d.year.to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, int(d.year.min()), 2020, step=20, label="year", through=int(d.year.max()) + 1)
    charts.rule(ax)
    charts.legend(fig, series)
    paths.save(fig, profile)
