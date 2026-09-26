"""The Black share of each magisterial district, 1870 and 1920 -> figures/residents_by_district_race.pdf, .png

One position per place - the three districts, then the whole county - and at each
a stroke from the district's Black share in 1870 to its share in 1920, an
open ring at the earlier census and a filled dot at the later. The county is
the three districts added together, so it is the same arithmetic as the
three beside it. Each share is of the people the same count records in that
place, so 1870 divides by the volume's district total and 1920 by the
schedules'.
"""
import pandas as pd

import charts
import paths
import style

YEARS = tuple(style.DISTRICT_RACE)
COUNTY = "whole county"


def shares() -> pd.DataFrame:
    """One row per place, one column per census, the Black share per cent."""
    d = pd.read_csv(paths.RESIDENTS_BY_DISTRICT)
    d = d[d.year.isin(YEARS)].copy()
    d["counted"] = d[["white", "black", "other"]].sum(axis=1)

    county = d.groupby("year")[["black", "counted"]].sum().assign(district=COUNTY)
    both = pd.concat([d, county.reset_index()], ignore_index=True)
    both["share"] = 100 * both.black / both.counted
    wide = both.pivot(index="district", columns="year", values="share")
    return wide.reindex(sorted(wide.index.drop(COUNTY)) + [COUNTY])


for profile in style.PROFILES:
    style.apply(profile)

    s = shares()
    assert s.notna().all().all(), f"a place with no share to draw:\n{s}"

    fig, ax = charts.figure(profile, of_width=style.NARROW)
    charts.dumbbell(ax, {label: (s[year].to_numpy(), colour, filled)
                         for year, (label, colour, filled) in style.DISTRICT_RACE.items()},
                    profile)
    charts.shares(ax, label="Black share of residents")
    charts.places(ax, list(s.index))
    charts.dot_legend(fig, {label: (colour, filled)
                           for label, colour, filled in style.DISTRICT_RACE.values()}, profile)
    paths.save(fig, "residents_by_district_race", profile)
