"""Contested treatments, in one place, applied explicitly by each figure.

These are the two open questions in docs/questions.md. Neither is settled, and
the existing figures disagree about both. Rather than hide that disagreement
inside five separate scripts, each treatment is implemented once here and each
figure names the one it uses. The inconsistency stays visible and greppable.

When Q1 and Q2 are settled, the chosen treatment moves into build/clean.py,
data/ carries the resolved values, and these functions and their call sites go
away.
"""
import pandas as pd

GROUPS = ["black", "hisp", "aapi", "white"]

# Census years in which the four race categories sum above the reported total.
# Most likely because the Census tabulates Hispanic origin across races, so
# Hispanic residents are counted twice. See Q1.
OVERLAPPING_YEARS = [1970, 1990]


def not_reported_as_zero(df: pd.DataFrame, cols=GROUPS) -> pd.DataFrame:
    """Read a not-yet-tabulated category as zero. See Q2.

    Hispanic is blank before 1970 and AAPI before 1950 because the Census did
    not separately tabulate them. This treats that absence as a zero, which is
    a stronger claim than the record supports: it renders as a flat zero line
    for a century.

    The alternative, used by the log-scale figure, is to leave the value
    missing so the series simply begins when first reported.
    """
    out = df.copy()
    for c in cols:
        out[c] = out[c].fillna(0)
    return out


def rescale_overlapping_years(shares: pd.DataFrame, cols=GROUPS) -> pd.DataFrame:
    """Rescale 1970 and 1990 shares so each year sums to 100%. See Q1.

    Applied only where the categories sum above 100. Leaves every other year
    untouched. The alternative, used by the count figure, is to plot as
    reported and let those bars exceed the total.
    """
    out = shares.copy()
    total = out[cols].sum(axis=1)
    over = total > 100
    for c in cols:
        out.loc[over, c] *= 100 / total[over]
    return out
