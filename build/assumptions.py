"""Assumptions currently in force while two questions are open.

Mechanism only. The reasoning is in docs/questions.md.

Each figure names the assumption it applies, so which figure takes which
position is greppable rather than buried. When a question is settled, its
assumption moves into the relevant build step and the function is deleted.
"""
import pandas as pd

GROUPS = ["black", "hisp", "aapi", "white"]


def not_reported_as_zero(df: pd.DataFrame, cols=GROUPS) -> pd.DataFrame:
    """Read a not-yet-tabulated category as zero rather than missing."""
    out = df.copy()
    for c in cols:
        out[c] = out[c].fillna(0)
    return out


def rescale_to_100(shares: pd.DataFrame, cols=GROUPS) -> pd.DataFrame:
    """Rescale shares so each year sums to 100%, where they exceed it."""
    out = shares.copy()
    total = out[cols].sum(axis=1)
    over = total > 100
    for c in cols:
        out.loc[over, c] *= 100 / total[over]
    return out
