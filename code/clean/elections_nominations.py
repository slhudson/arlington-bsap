"""How each County Board candidate was nominated -> data/clean/elections_nominations.csv

One row per candidate per nominating contest. Two kinds of row, told apart
by `basis`:

    derived   a primary the county's candidate history (to 2021) or the
              state's database (from 2022) prints, with its counts
    keyed     a convention, caucus, committee vote or primary a newspaper
              reports, keyed by hand with a quoted sentence
              (data/transcribed/by_claude/elections_nominations.csv)

A primary candidate won the nomination if they are on the same year's
regular general ballot. The state's own winner flag is not used: for a
ranked-choice primary it marks every candidate who was not eliminated in
the first count, and the county prints no flag. docs/elections.md, "How the
Board's candidates were nominated", has what each column holds and the
years no source covers.
"""
import numpy as np
import pandas as pd

import citekeys
import elections
import paths
from elections import COUNTY_HISTORY_THROUGH
from paths import write

METHODS = {"Democratic primary", "Democratic caucus", "Democratic committees' vote",
           "ABC convention", "Republican committee", "Republican mass meeting",
           "regular nomination", "citizens' candidate", ""}
PARTIES = {"Democratic", "Republican", "ABC", "citizens'"}
OUTCOMES = {"nominated", "lost", "unopposed", "withdrew", "ran against the nominee"}
SEATS = {"regular"}

# Ranked-choice counting in a state-run primary: 2023 was Arlington's first
# (arlnow2022dorsey); 2024 and 2025 followed.
RANKED_CHOICE_YEARS = {2023, 2024, 2025}

COLUMNS = ["year", "seat", "date", "party", "method", "counting", "name", "outcome", "votes",
           "votes_kind", "pct", "total_votes", "contested", "source", "basis", "note"]


def iso(election_date: str, year: int) -> str:
    """A date as the two records print it ("June 9, 2015", "June 13", an
    ISO timestamp), as YYYY-MM-DD."""
    s = str(election_date)
    if s[:4].isdigit() and "T" in s:
        return s[:10]
    d = pd.to_datetime(s if s[-4:].isdigit() else f"{s}, {year}", format="mixed")
    return d.strftime("%Y-%m-%d")


def derived() -> pd.DataFrame:
    c = elections.contests()
    c = c[(c.record == "county") | (c.year > COUNTY_HISTORY_THROUGH)]
    regular = c[~c.primary & ~c.special & c.person & ~c.writein]
    on_ballot = {y: set(g.surname) for y, g in regular.groupby("year")}
    rows = []
    for contest, g in c[c.primary].groupby("contest", sort=False):
        first = g.iloc[0]
        year = int(first.year)
        named = g[g.person & ~g.writein]
        if first.record == "county":
            source = first.source
        else:
            source = f"{citekeys.VA_ELECTIONS} contest {contest}"
        counted = named.votes.notna().all()
        total = int(g.votes.sum()) if g.votes.notna().all() else np.nan
        winners = [s in on_ballot.get(year, set()) for s in named.surname]
        if not any(winners):
            raise ValueError(f"{year} primary {contest}: no candidate is on the regular general ballot")
        multi = len(named) > 1
        counting = "ranked-choice" if year in RANKED_CHOICE_YEARS else "plurality"
        kind = ("first-choice" if year in RANKED_CHOICE_YEARS and len(named) > 2 else "count") if counted else ""
        for (_, r), won in zip(named.iterrows(), winners):
            rows.append({
                "year": year, "seat": "regular", "date": iso(r.election_date, year),
                "party": "Democratic", "method": "Democratic primary", "counting": counting,
                "name": r["name"], "outcome": "nominated" if won else "lost",
                "votes": r.votes, "votes_kind": kind, "pct": np.nan, "total_votes": total,
                "contested": True if multi else np.nan,
                "source": source, "basis": "derived",
                "note": "; ".join(filter(None, [
                    "" if counted else "the county prints the primary's candidates and no counts",
                    "" if multi else "the county prints one name; whether anyone ran against them is not stated"]))})
    return pd.DataFrame(rows, columns=COLUMNS)


def keyed() -> pd.DataFrame:
    k = paths.typed(paths.built("elections_nominations"))
    for col, ok in (("method", METHODS), ("party", PARTIES), ("outcome", OUTCOMES)):
        bad = set(k[col].dropna()) - ok
        if bad:
            raise ValueError(f"elections_nominations.csv: {col} {sorted(bad)} is not one the "
                             f"clean step knows; add it to the vocabulary or fix the row")
    k["year"] = k.year.astype(int)
    k["votes_kind"] = np.where(k.votes.notna(), "count", "")
    lost = k.groupby(["year", "seat", "party"]).outcome.transform(lambda o: (o == "lost").any())
    unopposed = k.outcome == "unopposed"
    k["contested"] = np.where(lost, True, np.where(unopposed, False, np.nan))
    k["basis"] = "keyed"
    return k.assign(note=k.note.fillna("")).reindex(columns=COLUMNS)


def build() -> pd.DataFrame:
    d = pd.concat([derived(), keyed()], ignore_index=True)
    d = d.sort_values(["year", "date", "party", "seat", "outcome", "votes"],
                      ascending=[True, True, True, True, True, False]).reset_index(drop=True)
    dup = d[d.duplicated(["year", "seat", "party", "name"], keep=False)]
    assert dup.empty, f"a candidate twice in one nominating contest:\n{dup[['year', 'seat', 'name', 'basis']]}"
    return d


if __name__ == "__main__":
    write(build(), "elections_nominations")
