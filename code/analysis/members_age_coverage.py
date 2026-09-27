"""How many sitting members have a birth year, 1870-2026
-> figures/members_age_coverage.pdf, .png

A stacked step area of the members sitting on 1 July of each year, those
with a birth year and those without, with the 1932 rule. A year the roster
names nobody in is a gap.
"""
import pandas as pd

import charts
import members
import paths
import style

rows = []
for year, s in members.by_year():
    known = int(s.birth_year.notna().sum())
    rows.append({"year": year, "known": known, "unknown": len(s) - known})
d = pd.DataFrame(rows)
if d.known.sum() == 0:
    raise ValueError("no sitting member has a birth year; nothing to draw")

for profile in style.PROFILES:
    style.apply(profile)
    spans = charts.runs(((d.known + d.unknown) > 0).to_numpy())
    series = charts.series(d, style.AGE_COVERAGE)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d.year.to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, members.FIRST, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    charts.legend(fig, series)
    paths.save(fig, "members_age_coverage", profile)
