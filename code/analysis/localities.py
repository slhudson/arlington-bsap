"""Virginia's localities of at least SMALLEST residents, ready to plot. A
module, not a step: both peer figures read it so they agree on which
localities are shown and how Arlington is marked.

Arlington sorts last, so no other dot is drawn over it, and takes its own
colour and the larger dot; every other locality takes its kind's colour.
"""
import pandas as pd

import charts
import paths
import style

SMALLEST = 100_000
LEGEND = {**{label: c for label, c in style.LOCALITIES.values()}, "Arlington": style.ARLINGTON}


def load(profile) -> pd.DataFrame:
    d = paths.read("localities")
    d = d[d["residents"] >= SMALLEST].copy()
    d["arlington"] = d["locality"] == "Arlington"
    d = d.sort_values("arlington")
    kinds = {k: c for k, (_, c) in style.LOCALITIES.items()}
    d["color"] = d["kind"].map(kinds).where(~d["arlington"], style.ARLINGTON)
    d["area"] = [charts.dot_area(a, profile) for a in d["arlington"]]
    return d


def name(ax, r, x, y, **kw):
    """Name one locality's dot at (r[x], r[y]); Arlington bold, in its colour."""
    charts.dot_label(ax, r[x], r[y], r["locality"], r["area"],
                     r["color"] if r["arlington"] else "black", bold=r["arlington"], **kw)
