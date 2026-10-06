"""The Black share of each district's men of voting age -> figures/residents_by_district_race_adults.pdf, .png

One line per district, the whole county behind them where all three districts
are counted, a dotted segment across a census with no count. The lines are
the men aged 21 and over at the four censuses whose schedules are held, 1880,
1900, 1910 and 1920. Arlington district in 1900 is a share of the men the
database holds there, which are fewer than the district's.

1870 is a ring on each line's axis position, unjoined to anything: the volume
prints race by township for every resident and not for men 21 and over, and
the 1870 extract places no one in a township, so the ring is the share of all
residents, a different count from the line's (docs/residents.md).
"""
import pandas as pd

import charts
import paths
import style

COUNTY = "county"
FIRST_RING = 1870


def shares() -> pd.DataFrame:
    """One row per census, one column per place, Black men as a per cent of
    men of voting age."""
    d = paths.read("residents_by_district_adults")
    d = d[d.men_all.notna() & d.men_black.notna()]
    d = d.assign(share=100 * d.men_black / d.men_all)
    wide = d.pivot(index="year", columns="district", values="share")
    # Every decade, so 1890 (no schedules) is an empty row the line is dotted across.
    wide = wide.reindex(range(int(wide.index.min()), int(wide.index.max()) + 1, 10))
    return wide[list(style.DISTRICTS) + [COUNTY]]


def residents_1870() -> pd.Series:
    """Black residents as a per cent of all residents in 1870, per district
    and for the county, which is the three districts added up."""
    d = paths.read("residents_by_district")
    d = d[d.year == FIRST_RING]
    d = d.assign(counted=d[["white", "black", "other"]].sum(axis=1))
    share = 100 * d.set_index("district").black / d.set_index("district").counted
    share[COUNTY] = 100 * d.black.sum() / d.counted.sum()
    return share


for profile in style.PROFILES:
    style.apply(profile)

    s = shares()
    assert s.notna().any().all(), f"a place with nothing to draw:\n{s}"
    ring = residents_1870()
    assert ring.notna().all(), f"1870 is missing a place:\n{ring}"

    fig, ax = charts.figure(profile)
    charts.lines(ax, s.index.to_numpy(),
                 {style.WHOLE_COUNTY[0]: (s[COUNTY].to_numpy(), style.WHOLE_COUNTY[1])}, bridge=True)
    charts.lines(ax, s.index.to_numpy(), charts.series(s, style.DISTRICTS), bridge=True)
    charts.marks(ax, [FIRST_RING], [ring[COUNTY]], style.WHOLE_COUNTY[1], filled=False)
    for key, (label, colour) in style.DISTRICTS.items():
        charts.marks(ax, [FIRST_RING], [ring[key]], colour, filled=False)
    charts.shares(ax, label="Black share of men of voting age")
    charts.years(ax, FIRST_RING, int(s.index.max()), step=10)
    charts.legend(fig, {style.WHOLE_COUNTY[0]: style.WHOLE_COUNTY[1],
                        **{l: c for l, c in style.DISTRICTS.values()}})
    paths.save(fig, profile)
