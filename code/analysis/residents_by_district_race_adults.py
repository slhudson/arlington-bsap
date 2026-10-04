"""The Black share of each district's men of voting age -> figures/residents_by_district_race_adults.pdf, .png

The same picture as residents_by_district_race with the men aged 21 and over
in place of every resident: one line per district, the whole county behind
them where all three districts are counted, a dotted segment across a census
with no count. The censuses are the four whose schedules are held, 1880,
1900, 1910 and 1920. Arlington district in 1900 is a share of the men the
database holds there, which are fewer than the district's.
"""
import pandas as pd

import charts
import paths
import style

COUNTY = "county"


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


for profile in style.PROFILES:
    style.apply(profile)

    s = shares()
    assert s.notna().any().all(), f"a place with nothing to draw:\n{s}"

    fig, ax = charts.figure(profile)
    charts.lines(ax, s.index.to_numpy(),
                 {style.WHOLE_COUNTY[0]: (s[COUNTY].to_numpy(), style.WHOLE_COUNTY[1])}, bridge=True)
    charts.lines(ax, s.index.to_numpy(), charts.series(s, style.DISTRICTS), bridge=True)
    charts.shares(ax, label="Black share of men of voting age")
    charts.years(ax, int(s.index.min()), int(s.index.max()), step=10)
    charts.legend(fig, {style.WHOLE_COUNTY[0]: style.WHOLE_COUNTY[1],
                        **{l: c for l, c in style.DISTRICTS.values()}})
    paths.save(fig, profile)
