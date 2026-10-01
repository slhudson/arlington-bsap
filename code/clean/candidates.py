"""Black candidacies for the Board, each joined to its election -> data/clean/candidates.csv

One row per candidacy a source says was a Black candidate's, with the
election it was in: the seats, the candidate's votes, the fewest votes that
won a seat, whether the candidate won, and the party label the record
prints. A primary won is a nomination won. Then one row per period in
which a source says no Black candidate ran, name blank, `through` its last
year. docs/candidates.md, "Black candidacies", has what each column holds and
what the sources say about the years between.

A candidacy is matched on surname, year and kind of election (regular,
special or primary) to:

    before 1931   the term members.csv holds for that election, from
                  O'Leary, whose record names the winners and no one else
    1931          the county's contest, which prints the top six and "others
                  not mentioned", and the county's list of all 51 candidates
                  (Anderson p.67), which marks three "(Col)"
    after 1931    the county's candidate history to 2021 and the state's
                  database after, as members_roster_results.outcomes() reads them

A candidacy that matches no election, or two, stops the build. So do a
Black member's election with no candidacy row, a candidacy inside a period
a source says none ran, and a "(Col)" entry on the 1931 list with no
candidacy.
"""
import numpy as np
import pandas as pd

import elections
import paths
from elections import COUNTY_HISTORY_THROUGH, LABELS, label_of, surname
from paths import write

LIST_YEAR = 1931
BEFORE = "before 1931"

# The state's file for a ranked-choice primary carries first choices and
# flags more winners than seats, so neither says who won. The outcome is
# the press's, by candidacy.
RANKED_CHOICE = {(2023, "spain", "primary"): (False, "arlnow2023coffeyprimary"),
                 (2024, "spain", "primary"): (True, "arlnow2024spain")}

# Hjerpe (2021) p.2: Jefferson District elected a Black member at 10 of 11
# recorded elections, 1871-1887.
JEFFERSON_WINS = 10

COLUMNS = ["claim", "name", "year", "month", "through", "election", "office", "seats",
           "votes", "winning_votes", "won", "party", "race_words", "source",
           "election_source", "note"]


def kind(r) -> str:
    """regular, special or primary, as an election record flags it."""
    return "primary" if r.primary else "special" if r.special else "regular"


def records() -> pd.DataFrame:
    """The Board's contests from 1931, one row per candidate: the county's to
    2021 and the state's after, as members_roster_results.outcomes() reads them."""
    c = elections.contests()
    c = c[(c.record == "county") & (c.year <= COUNTY_HISTORY_THROUGH)
          | (c.record == "state") & (c.year > COUNTY_HISTORY_THROUGH)]
    return c.assign(election=[kind(r) for r in c.itertuples()])


def party_of(r) -> str:
    """The label a record prints for a candidate: the state's party column,
    or the county's parenthesis."""
    for p in (r.party, r.primary_party):
        if isinstance(p, str):
            return p
    label = label_of(r.candidate, f"{r.year}: ")
    return LABELS[label] if label else ""


def outcome(g, key):
    """(won, winning_votes, seats, note) for the candidate `key` =
    (year, surname, election) in contest `g`. The county marks the 1931
    winners "(won)" and otherwise the top `seats` counts win."""
    people = g[g.person]
    marked = people[people.candidate.str.contains(r"\(won\)")]
    seats = len(marked) if len(marked) else int(g.seats.iloc[0])
    flagged = people[people.is_winner.eq(True)] if g.record.iloc[0] == "state" else people.iloc[:0]
    if len(flagged) > seats:
        if key not in RANKED_CHOICE:
            raise ValueError(f"{key}: a ranked-choice contest, whose first choices do not say "
                             f"who won; add the outcome and its source to RANKED_CHOICE")
        won, cite = RANKED_CHOICE[key]
        return won, np.nan, seats, f"ranked-choice primary; votes are first choices; outcome from {cite}"
    winners = marked if len(marked) else people.nlargest(seats, "votes")
    won = key[1] in set(winners.surname)
    return won, winners.votes.min(), seats, ""


def join(c, members, listed, contests) -> dict:
    """One candidacy (its rows from every source that states it) joined to
    its election, or a ValueError saying why it cannot be."""
    first = c.iloc[0]
    year, name, election = int(first.year), first["name"], first.election
    key = (year, surname(name), election)
    out = {"claim": "candidacy", "name": name, "year": year, "election": election,
           "office": first.office, "race_words": "; ".join(c.race_words),
           "source": "; ".join(f"{s} p.{p}" if p else s for s, p in zip(c.source, c.page))}
    if year < LIST_YEAR:
        t = members[(members.election_year == year) & (members.surname == key[1])
                    & members.district.map(lambda d: f"{d} District" in first.office)]
        if len(t) != 1:
            raise ValueError(f"{name} {year}: {len(t)} terms in members.csv; "
                             f"a candidacy {BEFORE} must match exactly one")
        return {**out, "seats": 1, "votes": np.nan, "winning_votes": np.nan, "won": True,
                "party": "", "election_source": t.source.iloc[0], "month": np.nan,
                "note": "O'Leary records the winner and no count"}
    rows = contests[(contests.year == year) & (contests.election == election)]
    mine = rows[rows.surname == key[1]]
    if mine.contest.nunique() > 1:
        raise ValueError(f"{name} {year} {election}: stood in {mine.contest.nunique()} contests "
                         f"of that kind; the candidacy cannot say which")
    if len(mine):
        g = rows[rows.contest == mine.contest.iloc[0]]
        r = mine.iloc[0]
        won, threshold, seats, note = outcome(g, key)
        return {**out, "seats": seats, "votes": r.votes, "winning_votes": threshold, "won": won,
                "party": party_of(r), "election_source": r.source, "month": r.month, "note": note}
    # Absent from the contest's rows: only the 1931 list names every candidate.
    entry = listed[listed.surname == key[1]] if year == LIST_YEAR else listed.iloc[:0]
    unprinted = rows[rows.prose & rows.candidate.str.contains("others not mentioned")]
    if len(entry) != 1 or rows.contest.nunique() != 1 or unprinted.empty:
        raise ValueError(f"{name} {year} {election}: matches no election record - no row of "
                         f"that contest in the county's or the state's record, and no entry "
                         f"on a list of candidates the record points to")
    printed = rows[rows.person]
    won, threshold, seats, _ = outcome(rows, key)
    return {**out, "seats": seats, "votes": np.nan, "winning_votes": threshold, "won": won,
            "party": "", "month": rows.month.iloc[0],
            "election_source": f"{entry.source.iloc[0]} p.{entry.page.iloc[0]}; {rows.source.iloc[0]}",
            "note": f"on the county's list, not among the {len(printed)} it prints with a count, "
                    f"so fewer than {printed.votes.min():,.0f} votes"}


def none_ran(d) -> pd.DataFrame:
    """The periods a source says no Black candidate ran in, as keyed."""
    return pd.DataFrame({"claim": "none", "name": "", "year": d.year.astype(int),
                         "through": d.through.astype(int), "office": d.office,
                         "race_words": d.race_words,
                         "source": [f"{s} p.{p}" for s, p in zip(d.source, d.page)],
                         "note": d.basis})


def check(out, members, listed):
    """The guards the docstring lists, over the joined table."""
    cand = out[out.claim == "candidacy"]
    # Every election a Black member won has a candidacy that won, and back.
    black = members[(members.race == "Black") & members.seated_by.isin(["election", "special election"])]
    terms = set(zip(black.surname, black.election_year.astype(int)))
    wins = cand[cand.won.astype(bool) & (cand.election != "primary")]
    won = set(zip(wins.name.map(surname), wins.year))
    if terms != won:
        raise ValueError("Black members' elections and winning candidacies differ:\n"
                         f"  a term, no candidacy: {sorted(terms - won)}\n"
                         f"  a candidacy, no term: {sorted(won - terms)}")
    # No candidacy inside a period a source says none ran.
    for n in out[out.claim == "none"].itertuples():
        inside = cand[cand.year.between(n.year, n.through)]
        if len(inside):
            raise ValueError(f"{n.source} says no Black candidate ran {n.year}-{n.through}, "
                             f"but candidacies are recorded: {list(inside.name)}")
    # Every "(Col)" on the 1931 list is a candidacy, and every 1931 candidacy is one.
    marked = set(listed[listed.entry.str.contains(r"\(Col")].surname)
    of_1931 = set(cand[cand.year == LIST_YEAR].name.map(surname))
    if marked != of_1931:
        raise ValueError(f"the 1931 list marks {sorted(marked)} (Col); the candidacies "
                         f"for 1931 are {sorted(of_1931)}")
    jefferson = cand[cand.office.str.contains("Jefferson") & cand.won.astype(bool)]
    assert len(jefferson) == JEFFERSON_WINS, (
        f"{len(jefferson)} Jefferson District wins 1871-1887; Hjerpe counts {JEFFERSON_WINS}")


def build() -> pd.DataFrame:
    d = paths.built("candidates")
    listed = d[d.claim == "listed"].assign(surname=lambda x: x.entry.map(surname))
    claims = d[(d.claim == "candidacy") & (d["name"] != "")]
    members = paths.read("members").assign(surname=lambda m: m["name"].map(surname))
    contests = records()
    joined = [join(c, members, listed, contests)
              for _, c in claims.groupby(["year", "name", "election", "office"], sort=False)]
    out = pd.concat([pd.DataFrame(joined),
                     none_ran(d[(d.claim == "candidacy") & (d["name"] == "")])],
                    ignore_index=True)
    out["year"] = out.year.astype(int)
    order = out.election.map({"primary": 0, "special": 1, "regular": 2})
    out = (out.assign(_m=out.month.fillna(0), _o=order)
              .sort_values(["claim", "year", "_m", "_o", "office", "name"])
              .drop(columns=["_m", "_o"]))
    out["election_source"] = out.election_source.fillna("")
    check(out, members, listed)
    return out.reindex(columns=COLUMNS).reset_index(drop=True)


if __name__ == "__main__":
    write(build(), "candidates")
