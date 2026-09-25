"""The sitting Board by age band, 1870-2026 -> figures/board_age_bands.pdf, .png

A stacked step area of the members sitting on 1 July of each year, in three
bands of age (under 40, 40 to 59, 60 and over) with those who have no birth
year in grey on top, with the 1932 rule. Years with no roster are gaps.
"""
import pandas as pd

import charts
import members
import paths
import style

UNDER, OVER = 40, 60

rows = []
for year, s in members.by_year():
    age = year - s.birth_year.dropna()
    rows.append({"year": year,
                 "under40": int((age < UNDER).sum()),
                 "40to59": int(((age >= UNDER) & (age < OVER)).sum()),
                 "60plus": int((age >= OVER).sum()),
                 "unknown": int(s.birth_year.isna().sum())})
d = pd.DataFrame(rows)
if d[["under40", "40to59", "60plus"]].sum().sum() == 0:
    raise ValueError("no sitting member has a birth year; nothing to draw")

for profile in style.PROFILES:
    style.apply(profile)
    sitting = d[["under40", "40to59", "60plus", "unknown"]].sum(axis=1) > 0
    spans = charts.runs(sitting.to_numpy())
    series = charts.series(d, style.AGE_BANDS)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d.year.to_numpy(), series, spans)
    charts.seats(ax, label="members sitting")
    charts.years(ax, members.FIRST, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS)
    charts.legend(fig, series)
    paths.save(fig, "board_age_bands", profile)
