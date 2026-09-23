"""Residents by race/ethnicity, 1870-2020 -> figures/residents_by_race.pdf, .png

Two panels, left and right: (a) how many residents, (b) what share of them.
Side by side rather than stacked because the counts panel needs to be taller
than it is wide for the decades before 1940 to have any height - Arlington had
under 27,000 residents until 1940 and 238,643 by 2020.

**Two bases, one series, and nothing drawn to mark it.** From 1980 the bands
are the five census groups that partition the county exactly: race crossed with
Hispanic origin, so nobody is counted twice. Before 1980 they are the delivered
race categories, because the Census did not ask Hispanic origin of everyone
until 1980 and 1970's sample question is not comparable - see Q1 in
docs/questions.md.

A rule at 1980 was drawn and then removed. The change is real but small enough
that it does not affect what the figure says: Arlington had 1,387 Hispanic
residents in 1970, under one per cent of the county, and none on the Board. A
line across the figure claimed more visual importance for it than it has. It
belongs in the caption, which carries it, and the labels are the same either
side of 1980 so they do not mislead.

One consequence worth knowing: only 1970 overshoots the county total. 1990,
which used to, is exact on the census basis.

Stacking order, axis upward: the three counted groups, then the residual, then
White. The residual is another kind of not-White, so it belongs with them -
above the sand it splits the non-White population in two and understates how
much the county has diversified.
"""
import numpy as np
import pandas as pd

import charts
import paths
import style

paths.build_stage_on_path()
from assumptions import not_reported_as_zero, rescale_to_100   # noqa: E402

CENSUS_FROM = 1980

for profile in style.PROFILES:
    style.apply(profile)

    c = not_reported_as_zero(pd.read_csv(paths.RESIDENTS))     # not-reported read as zero
    old = style.GROUP_ORDER                                    # black, hisp, aapi, white
    new = ["nh_black", "hispanic", "nh_aapi", "nh_white"]

    # One frame with four bands plus a residual, whichever basis a year is on.
    counts = pd.DataFrame(index=c.index, columns=old, dtype=float)
    on_census = c["year"] >= CENSUS_FROM
    for a, b in zip(old, new):
        counts[a] = np.where(on_census, c[b], c[a])
    residual = np.where(on_census, c["nh_other"],
                        (c["total"] - c[old].sum(axis=1)).clip(lower=0))

    shares = counts.div(c["total"], axis=0) * 100
    residual_share = (100 - shares.sum(axis=1)).clip(lower=0)   # before rescaling
    # Rescaling only ever applies to the pre-1980 years; from 1980 the groups
    # already sum to the county and rescale_to_100 leaves them alone.
    shares = rescale_to_100(shares)

    def bands(frame, resid):
        out = {style.GROUP_LABELS[g]: (frame[g].to_numpy(), style.RACE_COLORS[g])
               for g in ("black", "hisp", "aapi")}
        out[style.OTHER_LABEL] = (np.asarray(resid), style.RESIDUAL_COLOR)
        out[style.GROUP_LABELS["white"]] = (frame["white"].to_numpy(),
                                            style.RACE_COLORS["white"])
        return out

    fig, (a, b) = charts.panels(style.PANELS, profile)

    charts.stacked_bars(a, c["year"], bands(counts, residual))
    charts.counts(a, 250000, 50000)
    charts.years(a, 1870, 2020, rotate=True)
    a.set_title("(a) number of residents")

    charts.stacked_bars(b, c["year"], bands(shares, residual_share))
    charts.shares(b)
    charts.years(b, 1870, 2020, rotate=True)
    b.set_title("(b) share of residents")

    entries = {style.GROUP_LABELS[g]: style.RACE_COLORS[g]
               for g in ("black", "hisp", "aapi")}
    entries[style.OTHER_LABEL] = style.RESIDUAL_COLOR
    entries[style.GROUP_LABELS["white"]] = style.RACE_COLORS["white"]
    charts.legend(fig, entries, ncol=3)

    paths.save(fig, "residents_by_race", profile)
