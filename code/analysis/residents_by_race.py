"""Residents by race/ethnicity, 1870-2020 -> figures/residents_by_race.pdf, .png

Two panels, left and right: (a) how many residents, (b) what share of them.
Side by side rather than stacked because the counts panel needs to be taller
than it is wide for the decades before 1940 to have any height - Arlington had
under 27,000 residents until 1940 and 238,643 by 2020.

**Two bases, one series, and the join is marked.** From 1980 the bands are the
five census groups that partition the county exactly: race crossed with
Hispanic origin, so nobody is counted twice. Before 1980 they are the delivered
race categories, because the Census did not ask Hispanic origin of everyone
until 1980 and 1970's sample question is not comparable - see Q1 in
docs/questions.md.

The alternative was two figures, one per basis. This is one series a reader can
follow, with a rule at 1980 and a caption saying what changes there. The
categories carry the same names and colours on both sides of it; what changes
is whether they overlap.

One consequence worth knowing: only 1970 now overshoots the county total. 1990,
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
HATCH = "////"

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
        out[style.OTHER_LABEL] = (np.asarray(resid), style.RESIDUAL_COLOR, HATCH)
        out[style.GROUP_LABELS["white"]] = (frame["white"].to_numpy(),
                                            style.RACE_COLORS["white"])
        return out

    fig, (a, b) = charts.panels(0.80, profile)

    charts.stacked_bars(a, c["year"], bands(counts, residual))
    charts.counts(a, 250000, 50000)
    charts.years(a, 1870, 2020, rotate=True)
    a.set_title("(a) number of residents")

    charts.stacked_bars(b, c["year"], bands(shares, residual_share))
    charts.shares(b)
    charts.years(b, 1870, 2020, rotate=True)
    b.set_title("(b) share of residents")

    # The basis changes in both panels, so the rule is drawn in both. The note
    # is written once, inside the left panel: the band above the frame is taken
    # by the panel titles, and 0.90 lands in white space above the 1980-2010
    # bars, which top out well below it.
    charts.rule(a, year=CENSUS_FROM - 5, note="census categories from 1980",
                inside_y=0.90)
    charts.rule(b, year=CENSUS_FROM - 5, note=None)

    entries = {style.GROUP_LABELS[g]: style.RACE_COLORS[g]
               for g in ("black", "hisp", "aapi")}
    entries[style.OTHER_LABEL] = (style.RESIDUAL_COLOR, HATCH)
    entries[style.GROUP_LABELS["white"]] = style.RACE_COLORS["white"]
    charts.legend(fig, entries, ncol=3)

    paths.save(fig, "residents_by_race", profile)
