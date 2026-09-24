"""Residents by race/ethnicity, 1870-2020 -> figures/residents_by_race.pdf, .png

Two panels, left and right: (a) how many residents, (b) what share of them.
Side by side rather than stacked because the counts panel needs to be taller
than it is wide for the decades before 1940 to have any height - Arlington had
under 27,000 residents until 1940 and 238,643 by 2020.

**Two bases, one series, and nothing drawn to mark it.** From 1980 the bands
are census groups that partition the county exactly: race crossed with Hispanic
origin, so nobody is counted twice. Before 1980 they are the delivered race
categories, because the Census did not ask Hispanic origin of everyone until
1980 and 1970's sample question is not comparable - see
docs/methods.md. The switch happens in code/build/residents.py, so this
script reads four columns and never asks which basis a year is on.

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

TOP = 50000          # White leaves the axis in the late 1930s; see off_scale

for profile in style.PROFILES:
    style.apply(profile)

    c = pd.read_csv(paths.RESIDENTS)
    groups = style.GROUP_ORDER                                 # black, hisp, aapi, white

    # The four columns already carry the basis each year is on - crossed census
    # categories from 1980, POP-TWPS0076 from 1900, the volumes before that -
    # so nothing is selected here. No fillna either: a blank stays blank, so a
    # line begins the year the Census first reported that group rather than
    # running along zero before it.
    counts = c[groups].astype(float)
    # The four never exceed the county in any year: the build refuses to write
    # a row whose race columns do not account for its published total, in
    # every stretch and by its own source's arithmetic. So this is a genuine
    # remainder - American Indian and other race before 1980, the census's own
    # non-Hispanic other and multiracial count from 1980 - and not a residue
    # of two category systems being mixed, which is what it was until the
    # 1970 columns were found transposed.
    residual = (c["total"] - c[groups].sum(axis=1)).clip(lower=0)

    shares = counts.div(c["total"], axis=0) * 100
    residual_share = (100 - shares.fillna(0).sum(axis=1)).clip(lower=0)
    shares = shares.fillna(0)

    def bands(frame, resid):
        out = {style.GROUP_LABELS[g]: (frame[g].to_numpy(), style.RACE_COLORS[g])
               for g in ("black", "hisp", "aapi")}
        out[style.OTHER_LABEL] = (np.asarray(resid), style.RESIDUAL_COLOR)
        out[style.GROUP_LABELS["white"]] = (frame["white"].to_numpy(),
                                            style.RACE_COLORS["white"])
        return out

    fig, (a, b) = charts.panels(profile)

    # (a) Unstacked lines, White excluded. Stacked bars cannot show when a
    # group starts being counted - a band of height zero and a band that has
    # not started are the same picture - and a line simply begins. Nothing is
    # stacked, so the axis reaches the largest single series, not the county.
    lines = {style.GROUP_LABELS[g]: (counts[g], style.RACE_COLORS[g])
             for g in ("black", "hisp", "aapi")}
    lines[style.OTHER_LABEL] = (residual.replace(0, np.nan), style.RESIDUAL_COLOR)
    # White last, so it draws over the others, and in the darker stroke.
    lines[style.GROUP_LABELS["white"]] = (counts["white"], style.SAND_LINE)
    charts.lines(a, c["year"], lines)
    charts.counts(a, TOP, 5000)
    charts.years(a, 1870, 2020, step=20)
    # White is on scale until the late 1930s and then far off it. The axis
    # clips it and an arrow marks where it goes, which keeps the years when
    # the groups were comparable - Black outnumbered White until about 1890 -
    # without giving three quarters of the axis to a series that ends at
    # 161,329.
    charts.off_scale(a, c["year"], counts["white"], style.SAND_LINE, TOP)
    a.set_title("(a) number of residents")

    charts.stacked_bars(b, c["year"], bands(shares, residual_share))
    charts.shares(b)
    charts.years(b, 1870, 2020, step=20)
    b.set_title("(b) share of residents")

    entries = {style.GROUP_LABELS[g]: style.RACE_COLORS[g]
               for g in ("black", "hisp", "aapi")}
    entries[style.OTHER_LABEL] = style.RESIDUAL_COLOR
    entries[style.GROUP_LABELS["white"]] = style.RACE_COLORS["white"]
    charts.legend(fig, entries, ncol=3)

    paths.save(fig, "residents_by_race", profile)
