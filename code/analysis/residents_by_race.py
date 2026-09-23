"""Residents by race/ethnicity, 1870-2020 -> figures/residents_by_race.pdf, .png

Two panels, left and right: (a) how many residents, (b) what share of them.
Side by side rather than stacked because the counts panel needs to be taller
than it is wide for the decades before 1940 to have any height - Arlington had
under 27,000 residents until 1940 and 238,643 by 2020.

**Still the delivered categories, not the census basis.** data/clean/ now also
carries five groups that partition the county exactly, from 1980 - see Q1 in
docs/questions.md. They cover forty years of a hundred and fifty, so showing
both bases in one figure is a presentation decision nobody has taken yet, and
taking it here would bury it. The census basis is drawn in the gallery.

The 1970 and 1990 columns are treated differently in the two panels: (a) plots
them as reported, so those bars sit slightly above the total, while (b)
rescales them to 100%. That is the open question, not a choice made here.
"""
import numpy as np
import pandas as pd

import charts
import paths
import style

paths.build_stage_on_path()
from assumptions import not_reported_as_zero, rescale_to_100   # noqa: E402

for profile in style.PROFILES:
    style.apply(profile)

    c = not_reported_as_zero(pd.read_csv(paths.RESIDENTS))     # not-reported read as zero
    order = style.GROUP_ORDER
    other = (c["total"] - c[order].sum(axis=1)).clip(lower=0)

    shares = c[order].div(c["total"], axis=0) * 100
    other_share = (100 - shares.sum(axis=1)).clip(lower=0)     # before rescaling
    shares = rescale_to_100(shares)                            # the 1970/1990 overlap

    # Stacking order, axis upward: the three counted groups, then the residual,
    # then White on top. The residual is another kind of not-White, so it
    # belongs with them - stacked above the sand it splits the non-White
    # population in two and understates how much the county has diversified.
    # Hatched because it is a mixed category rather than a counted one.
    HATCH = "////"

    def bands(frame, residual_values):
        out = {style.GROUP_LABELS[g]: (frame[g].to_numpy(), style.RACE_COLORS[g])
               for g in ("black", "hisp", "aapi")}
        out[style.OTHER_LABEL] = (np.asarray(residual_values),
                                  style.RESIDUAL_COLOR, HATCH)
        out[style.GROUP_LABELS["white"]] = (frame["white"].to_numpy(),
                                            style.RACE_COLORS["white"])
        return out

    fig, (a, b) = charts.panels(0.80, profile)

    charts.stacked_bars(a, c["year"], bands(c, other))
    charts.counts(a, 250000, 50000)
    charts.years(a, 1870, 2020, rotate=True)
    a.set_title("(a) number of residents")

    charts.stacked_bars(b, c["year"], bands(shares, other_share))
    charts.shares(b)
    charts.years(b, 1870, 2020, rotate=True)
    b.set_title("(b) share of residents")

    entries = {style.GROUP_LABELS[g]: style.RACE_COLORS[g]
               for g in ("black", "hisp", "aapi")}
    entries[style.OTHER_LABEL] = (style.RESIDUAL_COLOR, HATCH)
    entries[style.GROUP_LABELS["white"]] = style.RACE_COLORS["white"]
    charts.legend(fig, entries)

    paths.save(fig, "residents_by_race", profile)
