"""Terms from election results: the county's candidate history to 2021 and
the state's database from 2022. A module, not a step: board_roster.py
assembles it with the rest.

    keyed_terms()   the district races of November 1923 and 1927, which the
                    county's history prints and board_terms.csv keys by hand
    terms()         1995 on, computed from who won each contest
    outcomes()      every County Board general election from 1931: who won,
                    who stood, how many seats

board_elections(), special_candidates() and general_winners() are the
lookups board_roster_novack.py cuts Novack's spans with.
"""
import pandas as pd

import elections
from board_terms import ELECTION, SPECIAL_ELECTION, listing
from elections import COUNTY_HISTORY_THROUGH, MONTHS, surname

MONTH_NAMES = {v: k for k, v in MONTHS.items()}


def keyed_terms():
    """Terms keyed by hand from the county's candidate history, for the
    two 1912-1931 elections it prints under the district headings
    (board_terms.csv). They add names to the roster; board_seats does not
    read them, and states the 1912-1931 seats itself. docs/board.md."""
    d = listing("terms")
    for _, r in d.iterrows():
        yield {"name": r["name"], "district": r.district,
               "start_year": int(r.start_year), "start_month": int(r.start_month),
               "end_year": int(r.end_year) if r.end_year else float("nan"),
               "end_month": int(r.end_month) if r.end_month else float("nan"),
               "seated_by": r.seated_by, "source": r.source, "note": r.note}


def board_elections():
    """Regular November County Board elections from 1931: year -> surnames who stood."""
    c = elections.county_history()
    c = c[c.november & ~c.primary]
    return {int(y): set(g.surname) for y, g in c.groupby("year")}


def special_candidates():
    """November County Board elections from 1931: year -> surnames in a
    same-day special contest, marked in the office column or after the
    candidate's name. Who won is not read here."""
    c = elections.county_history()
    c = c[c.november & (c.office.str.contains("special|unexp", case=False)
                        | c.candidate.str.contains("unexp", case=False))]
    return {int(y): set(g.surname) for y, g in c.groupby("year")}


def general_winners():
    """Regular County Board elections: year -> surnames who won."""
    out = {}
    for c in outcomes():
        if not c["special"]:
            out.setdefault(c["year"], set()).update(surname(w) for w in c["winners"])
    return out


def outcomes():
    """Every County Board general election from 1931, from both records: who
    won, who stood, how many seats. Both records hold 2021 and must name the
    same winner there."""
    c = elections.contests()
    c = c[c.person & ~c.primary]
    out = []
    for _, g in c.groupby("contest", sort=False):
        first = g.iloc[0]
        won = g.nlargest(int(first.seats), "votes")
        out.append({"record": first.record, "year": int(first.year), "month": int(first.month),
                    "special": bool(first.special), "fills": first.fills,
                    "source": first.source,
                    "winners": list(won.name), "stood": list(g.name)})
    overlap = [(c["record"], sorted(map(surname, c["winners"]))) for c in out
               if c["year"] == COUNTY_HISTORY_THROUGH and not c["special"]]
    if len(overlap) != 2 or overlap[0][1] != overlap[1][1]:
        raise ValueError(f"county and state sources disagree on {COUNTY_HISTORY_THROUGH}: {overlap}")
    return [c for c in out if c["record"] == "county" or c["year"] > COUNTY_HISTORY_THROUGH]


def terms(earlier: pd.DataFrame):
    """Terms from 1995 on, appended to `earlier`.

    A regular November win in year Y is a four-year term from January Y+1. A
    special election's winner serves until the next regular election they
    stand in, and the member whose term covered that date and ended then is
    closed at the special; that member must be unique. A person is named as
    Novack spells them where the surname matches, otherwise as the county
    spells them the first time they win.
    """
    rows = list(outcomes())
    known = {surname(n): n for n in earlier.name}

    def canonical(n):
        return known.setdefault(surname(n), n)

    new = [{"name": canonical(w), "district": "at large",
            "start_year": c["year"] + 1, "start_month": 1,
            "end_year": c["year"] + 4, "end_month": 12,
            "seated_by": ELECTION, "source": c["source"], "note": ""}
           for c in rows if not c["special"] and c["year"] >= 1994
           for w in c["winners"]]
    d = pd.concat([earlier, pd.DataFrame(new)], ignore_index=True)

    for c in sorted((c for c in rows if c["special"] and c["year"] >= 1995),
                    key=lambda c: (c["year"], c["month"])):
        for w in c["winners"]:
            w = canonical(w)
            nxt = [r["year"] for r in rows if not r["special"] and r["year"] >= c["year"]
                   and any(canonical(s) == w for s in r["stood"])]
            if not nxt:
                raise ValueError(f"{w} won a special election in {c['year']} and never "
                                 "stood again; the seat's cycle cannot be inferred")
            end = min(nxt)
            when = f"{MONTH_NAMES[c['month']]} {c['year']}"
            covers = ((d.start_year * 12 + d.start_month <= c["year"] * 12 + c["month"])
                      & (d.end_year == end) & (d.end_month == 12) & (d.name != w))
            if c["fills"]:
                covers &= d.name.map(surname) == surname(c["fills"])
            if covers.sum() != 1:
                raise ValueError(f"special election {when}: {covers.sum()} members "
                                 f"hold a term ending {end}, expected 1:\n"
                                 f"{d[covers][['name', 'start_year', 'end_year']]}")
            i = d.index[covers][0]
            d.loc[i, ["end_year", "end_month"]] = [c["year"], c["month"]]
            d.loc[i, "note"] = (d.loc[i, "note"] + " " if d.loc[i, "note"] else "") + \
                f"Left the seat before the end of the term; filled by special election in {when}."
            d.loc[len(d)] = {"name": w, "district": "at large",
                             "start_year": c["year"], "start_month": c["month"],
                             "end_year": end, "end_month": 12,
                             "seated_by": SPECIAL_ELECTION, "source": c["source"],
                             "note": f"Elected in a special election in {when} to fill an unexpired term."}
    return d
