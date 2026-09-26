"""The Black share of each magisterial district -> figures/residents_by_district_race.pdf, .png

One line per district over the censuses that give race below the county,
with the whole county behind them as the reference. 1870 is printed in the
volume; 1910 and 1920 are counted from the full-count schedules. 1880 to
1900 give no race below the county, so the line breaks there rather than
being drawn through three censuses nothing reports. Each share is of the
people the same count records in that place.
"""
import pandas as pd

import charts
import paths
import style

COUNTY = "county"


def shares() -> pd.DataFrame:
    """One row per census, one column per place, the Black share per cent,
    a census with no race split left empty."""
    d = pd.read_csv(paths.RESIDENTS_BY_DISTRICT)
    d["counted"] = d[["white", "black", "other"]].sum(axis=1)

    # The county is the three districts added up, so it is only a county
    # where all three have a race split: in 1900 the schedules are short of
    # Arlington district and two districts are not the county.
    whole = d.groupby("year").black.count() == d.groupby("year").district.count()
    county = (d[d.year.isin(whole[whole].index)].groupby("year")[["black", "counted"]].sum()
              .assign(district=COUNTY).reset_index())
    both = pd.concat([d, county], ignore_index=True)
    both["share"] = 100 * both.black / both.counted
    wide = both.pivot(index="year", columns="district", values="share")
    # The censuses with no race below the county stay, empty, so the line
    # breaks across them instead of being drawn through them; the axis stops
    # at the last census that has one rather than running on over nothing.
    told = wide.index[wide.notna().any(axis=1)]
    return wide.loc[told.min():told.max(), list(style.DISTRICTS) + [COUNTY]]


for profile in style.PROFILES:
    style.apply(profile)

    s = shares()
    assert s.notna().any().all(), f"a place with nothing to draw:\n{s}"

    fig, ax = charts.figure(profile)
    charts.lines(ax, s.index.to_numpy(),
                 {style.WHOLE_COUNTY[0]: (s[COUNTY].to_numpy(), style.WHOLE_COUNTY[1])})
    charts.lines(ax, s.index.to_numpy(), charts.series(s, style.DISTRICTS))
    charts.shares(ax, label="Black share of residents")
    charts.years(ax, int(s.index.min()), int(s.index.max()), step=10)
    charts.legend(fig, {**{l: c for l, c in style.DISTRICTS.values()},
                        style.WHOLE_COUNTY[0]: style.WHOLE_COUNTY[1]})
    paths.save(fig, "residents_by_district_race", profile)
