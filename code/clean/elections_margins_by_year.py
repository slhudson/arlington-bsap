"""Each general election beside how its winners were nominated -> data/clean/elections_margins_by_year.csv

One row per general-election contest (a regular election, a special
election, or before 1931 a district's single seat): the seats, the winners
and how each was nominated, whether anyone stood against them whom the record
labels neither Democratic nor ABC, and the two margins, general and
nominating. A winner whose nomination no source covers reads "no record";
that is a gap, and the row says nothing about whether the nomination was
contested. docs/elections.md, "How close the contests were".
"""
import numpy as np
import pandas as pd

import paths
from elections import surname
from paths import write

COLUMNS = ["year", "tier", "contest", "seats", "winners", "nominated_by", "contested_other",
           "general_margin_votes", "general_margin_share", "nomination_contested",
           "nomination_margin_votes", "nomination_margin_share", "general_status", "note"]


def how(name: str, noms: pd.DataFrame, year: int, seat: str) -> pd.DataFrame:
    """The nomination rows for one winner in one seat."""
    s = surname(name)
    return noms[(noms.year == year) & (noms.seat == seat)
                & (noms.name.map(surname) == s) & noms.outcome.isin(["nominated", "unopposed"])]


def build() -> pd.DataFrame:
    m = paths.read("elections_margins")
    noms = paths.read("elections_nominations")
    gen = m[m.stage == "general"]
    nom = m[m.stage == "nomination"]
    rows = []
    for _, g in gen.iterrows():
        winners = [w for w in str(g.winners).split("; ") if w and w != "nan"]
        parts, contests = [], []
        used = []
        for w in winners:
            h = how(w, noms, int(g.year), g.contest)
            if h.empty:
                parts.append(f"{w}: no record")
                continue
            r = h.iloc[0]
            kind = ("unopposed" if r.outcome == "unopposed"
                    else "contested" if r.contested is True
                    else "contest not reported")
            parts.append(f"{w}: {r.method or 'method not stated'}, {kind}")
            key = (r.year, r.seat, r.party)
            if key not in used:
                used.append(key)
        for y, seat, party in used:
            n = nom[(nom.year == y) & (nom.contest == seat) & (nom.party == party)]
            if len(n):
                contests.append(n.iloc[0])
        def pick(col, fmt):
            vals = [fmt(c[col]) for c in contests if pd.notna(c[col])]
            return "; ".join(vals) if vals else np.nan
        flag = "; ".join(f"{c.party} nomination: {c.note}" for c in contests
                         if c.status != "computed" and pd.notna(c.note))
        contested = []
        for y, seat, party in used:
            mask = (noms.year == y) & (noms.seat == seat) & (noms.party == party)
            contested.append("yes" if (noms[mask].outcome == "lost").any()
                             else "no" if (noms[mask].outcome == "unopposed").any() else "not reported")
        rows.append({
            "year": g.year, "tier": g.tier, "contest": g.contest, "seats": g.seats,
            "winners": g.winners, "nominated_by": "; ".join(parts),
            "contested_other": g.contested_other,
            "general_margin_votes": g.margin_votes, "general_margin_share": g.margin_share,
            "nomination_contested": "; ".join(contested) if contested else np.nan,
            "nomination_margin_votes": pick("margin_votes", lambda v: f"{int(v)}"),
            "nomination_margin_share": pick("margin_share", lambda v: f"{v:.3f}"),
            "general_status": g.status,
            "note": "; ".join(filter(None, [g.note if pd.notna(g.note) else "", flag]))})
    return pd.DataFrame(rows, columns=COLUMNS)


if __name__ == "__main__":
    write(build(), "elections_margins_by_year")
