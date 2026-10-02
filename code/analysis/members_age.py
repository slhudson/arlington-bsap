"""Ages of the Board, 1932-2026 -> figures/members_age.pdf, .png

A Lexis diagram: age against year. Behind, the youngest-to-oldest span of the
members holding a seat in each month, drawn where every member in it either
has a birth year or is named in UNKNOWN below, so its edges lie on the
strokes and move only when the Board changes. Over it, one diagonal per member with a birth year, from
the age at which they arrived to the age at which they left; terms less than
a year apart are one stroke. Diagonals are clipped at the left edge.
"""
import numpy as np
import pandas as pd

import charts
import members
import paths
import style

FIRST, LAST = 1932, members.LAST

# The members seated since 1932 whose birth year no source gives. The span is
# still drawn in their months, understating the spread by whatever they would
# add at either edge, and naming them is what keeps that a known quantity:
# a member who arrives without a birth year and is not named here stops the
# build rather than quietly widening the tolerance. W. P. Ames was found in no
# census; Susan Cunningham and Tannia Talento are recent enough that a stated
# age should be findable (docs/members.md, "What rests on an assumption").
# Edward Duncan is here because his Jefferson district term runs into January
# 1932, the figure's first month, though he belongs to the era before it.
UNKNOWN = {"Edward Duncan", "W. P. Ames", "Susan R. Cunningham", "Tannia Talento"}
MERGE_WITHIN = 12           # months between terms that still make one stroke


def check_unknown_is_current(d):
    """Nobody in UNKNOWN has since been given a birth year.

    The set is an admission of what the span leaves out, so a name that stays
    in it after the gap is filled would understate what the figure knows.
    """
    found = sorted(n for n in UNKNOWN
                   if n in set(d[d.birth_year.notna()].name))
    if found:
        raise ValueError("UNKNOWN in code/analysis/members_age.py names members who now "
                         "have a birth year: " + ", ".join(found))


def span_by_month():
    """One row per month: youngest and oldest age holding a seat, as the
    strokes measure age (the month less the birth year less a half), NaN
    where too few members have a birth year."""
    d = paths.read("members")
    check_unknown_is_current(d)
    rows = []
    for m in range(FIRST * 12, (LAST + 1) * 12):
        s = d[(d.held_from <= m) & (m < d.held_to)].drop_duplicates("name")
        ages = (m / 12 - s.birth_year.dropna() - 0.5).to_numpy()
        missing = set(s[s.birth_year.isna()].name) - UNKNOWN
        if missing:
            raise ValueError(
                f"{m // 12}-{m % 12 + 1:02d}: no birth year for "
                + ", ".join(sorted(missing))
                + ".\n  Find one, or add the member to UNKNOWN in "
                  "code/analysis/members_age.py, which says who the span leaves out.")
        drawn = bool(len(ages))
        rows.append({"x": m / 12,
                     "youngest": ages.min() if drawn else np.nan,
                     "oldest": ages.max() if drawn else np.nan})
    out = pd.DataFrame(rows)
    if out.oldest.notna().sum() == 0:
        raise ValueError("no month has enough birth years to draw; nothing to draw")
    return out


def tenures():
    """(x0, age0, x1, age1) per member's run of terms, x in years. Age is
    the year less the birth year less a half: a birth year alone puts the
    birthday at mid-year, so the age on 1 July is the same whole number the
    band uses."""
    d = paths.read("members").dropna(subset=["birth_year"]).sort_values(["name", "held_from"])
    out = []
    for _, g in d.groupby("name"):
        start, stop, birth = None, None, g.birth_year.iloc[0]
        for a, b in zip(g.held_from, g.held_to):
            if start is not None and a - stop > MERGE_WITHIN:
                out.append((start, stop, birth))
                start = None
            start, stop = (a if start is None else start), b
        out.append((start, stop, birth))
    segs = []
    for a, b, birth in out:
        x0, x1 = max(a / 12, FIRST), min(b / 12, LAST + 1)
        if x1 > x0:
            segs.append((x0, x0 - birth - 0.5, x1, x1 - birth - 0.5))
    return segs


for profile in style.PROFILES:
    style.apply(profile)
    d = span_by_month()
    spans = charts.runs(d.oldest.notna().to_numpy())

    fig, ax = charts.figure(profile)
    charts.age_band(ax, d.x.to_numpy(), d.youngest.to_numpy(), d.oldest.to_numpy(),
                    spans, style.AGE_SPAN["band"][1], width=1 / 12)
    charts.strokes(ax, tenures(), style.AGE_SPAN["member"][1])
    charts.ages(ax, 0, 100)
    charts.years(ax, 1930, 2020, step=10, label="year", through=LAST + 1)
    ax.set_xlim(FIRST, LAST + 1)
    paths.save(fig, profile)

