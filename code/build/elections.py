"""The election records as one table -> data/built/elections.csv

One row per candidate per contest, every office, both records, with the
contest's own facts on each row; and, for 1870-1920, one row per entry
O'Leary prints, the Board of Supervisors by district and the presidential
returns. Nothing is chosen: every row of the county's candidate history is
here, prose and write-ins included, every candidate in the state's files,
their precinct rows summed, every line of O'Leary's as transcribed, and
every ticket of the Commonwealth's return for President as keyed.
code/clean/elections.py selects from it.

    record      "county" (arlingtonelections2021, to 2021), "state"
                (vaelections, 2000 on), "oleary" (oleary2010, 1870-1920),
                "state_return" (the Almanack's and the Secretary's printed
                county returns for President, 1876-1916, 1924, 1928) or
                "gazette_return" (the Alexandria Gazette's printed district
                returns for President, 1872, 1876, 1892, 1896, 1900, 1920) or
                "press_return" (a newspaper's printed County Board counts for
                candidates the county's history leaves blank)
    entry       O'Leary's printed line, unparsed; `district` the magisterial
                district it is listed under
    contest     an id shared by the contest's rows: for the county, the
                year, date and heading without its qualifier
    office      the heading as printed, qualifier included
    year        as printed for the county, from the date for the state
    election_date, election_kind, month, november, primary
    special     a special election, by a qualifier on any of the contest's
                headings or an off-November date
    seats       how many seats the contest filled, from its heading
    fills       whose unexpired term a special fills, as the heading
                names them, or ""
    candidate   as printed; `name` is it without the county's label
    votes       the count as a number; blank where the page prints none
    prose       the row is a remark about the contest, not a candidate
    writein     the write-in line
    person      the row names a candidate: neither of the above
    party, primary_party, is_winner    the state's columns; is_winner is
                true if any precinct row says so
    source      the citation for the row
    read_from, quote
                a "state_return" row's reading: what was read and the
                printed line it was read from; `page` is where it prints

The county's text columns and page stay on its rows. County rows come
first, in page order; state rows follow, in contest order.
"""
import re

import numpy as np
import pandas as pd

import citekeys
from paths import BY_CLAUDE, RAW, source, write

COUNTY = BY_CLAUDE / "arlington_county" / "candidate_history_1920-present.csv"
STATE = (RAW / "va_dept_of_elections" / "county_board_2000-2026.csv.gz",
         RAW / "va_dept_of_elections" / "president_1924-2024.csv.gz")
# O'Leary's listings, and the office each is of.
OLEARY = {BY_CLAUDE / "arlington_county" / "members_1870-1920.csv": "Board of Supervisors",
          BY_CLAUDE / "arlington_county" / "president_1872-1920.csv": "President"}

# The Commonwealth's county returns for President, one row per ticket as keyed.
STATE_RETURN = BY_CLAUDE / "elections_results_state.csv"
# The Alexandria Gazette's own district returns for President, one row per
# ticket per district as keyed.
GAZETTE_RETURN = BY_CLAUDE / "elections_results_gazette.csv"
# County Board counts a newspaper printed for a candidate the county's
# history leaves blank, one row per candidate as keyed.
PRESS_RETURN = BY_CLAUDE / "elections_results_press.csv"

NAMED = re.compile(r"^[*A-Z]")                          # a row naming a candidate
# The qualifiers a contest heading carries.
TWO_SEATS = re.compile(r"two seats|2 seats|vote for 2|two elected", re.I)
SPECIAL = re.compile(r"special|unexpired", re.I)
# "(to fill Eisenberg's unexpired term)", "(... following death of Charles Monroe)"
FILLS = re.compile(r"to fill ([A-Za-z]+)['’]s unexpired term|death of ([A-Za-z. ]+?)\)", re.I)
PARTY_LABEL = re.compile(r"\s*\((?:[^)]+)\)\s*$")

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}


def county() -> pd.DataFrame:
    """Every row of the county's candidate history, text as transcribed
    with blanks as "", plus the columns above."""
    c = source(COUNTY, dtype=str).fillna("")
    c["votes"] = pd.to_numeric(c.votes.str.replace(",", ""), errors="coerce")
    c["prose"] = ~c.candidate.str.match(NAMED) | c.candidate.str.contains(":")
    c["writein"] = c.candidate.str.contains("write", case=False)
    c["person"] = ~c.prose & ~c.writein
    c["november"] = c.election_date.str.startswith("November")
    c["primary"] = c.election_kind.str.contains("Primary")
    c["base"] = c.office.str.replace(r"\s*\(.*", "", regex=True).str.strip()
    key = ["year", "election_date", "base"]
    c = c.merge(c.groupby(key).office.agg(" ".join).rename("qualifiers"),
                left_on=key, right_index=True)
    c["record"] = "county"
    c["contest"] = c.year + " " + c.election_date + " " + c.base
    c["month"] = c.election_date.str[:3].map(MONTHS)
    c["special"] = c.qualifiers.str.contains(SPECIAL) | ~c.november
    c["seats"] = np.where(c.qualifiers.str.contains(TWO_SEATS), 2, 1)
    fills = c.qualifiers.str.extract(FILLS)
    c["fills"] = [a if isinstance(a, str) else b if isinstance(b, str) else ""
                  for a, b in zip(fills[0], fills[1])]
    c["name"] = c.candidate.str.replace(PARTY_LABEL, "", regex=True).str.strip()
    c["source"] = citekeys.ARLINGTON_ELECTIONS + " p." + c.page
    return c


def state(path) -> pd.DataFrame:
    """Every candidate of every contest in one of the state's files, their
    precinct rows summed; the total, undervote and write-in lines marked."""
    s = source(path, low_memory=False)
    s["date"] = pd.to_datetime(s.election_date)
    s["writein"] = s.candidate_name.str.startswith("Write", na=False)
    s["person"] = ~s.candidate_name.str.match(r"^(Total|Write|Under|Over)", na=False)
    s = s[s.person | s.writein]
    g = s.groupby(["contest_id", "candidate_name"], sort=False).agg(
        votes=("votes", "sum"), date=("date", "first"), election_date=("election_date", "first"),
        election_kind=("election_type", "first"), office=("office_name", "first"),
        seats=("number_seats", "first"), party=("candidate_party_name", "first"),
        primary_party=("primary_party", "first"),
        is_winner=("is_winner", lambda v: bool(v.fillna(False).astype(bool).any())),
        person=("person", "first"), writein=("writein", "first")).reset_index()
    return pd.DataFrame({
        "record": "state", "contest": g.contest_id.astype(str),
        "office": g.office, "election_date": g.election_date, "election_kind": g.election_kind,
        "year": g.date.dt.year, "month": g.date.dt.month, "november": g.date.dt.month == 11,
        "primary": g.election_kind.str.startswith("Primary"),
        "special": g.date.dt.month != 11, "seats": g.seats.astype(int), "fills": "",
        "candidate": g.candidate_name, "name": g.candidate_name, "votes": g.votes,
        "person": g.person, "writein": g.writein, "prose": False,
        "party": g.party, "primary_party": g.primary_party, "is_winner": g.is_winner,
        "source": citekeys.VA_ELECTIONS + " contest " + g.contest_id.astype(str)})


def oleary(path, office) -> pd.DataFrame:
    """Every entry of one of O'Leary's listings, one row each, as printed."""
    o = source(path, dtype=str).fillna("")
    o["record"] = "oleary"
    o["office"] = office
    o["contest"] = o.year + " " + o.election_date + " " + office
    o["month"] = o.election_date.str[:3].map(MONTHS)
    o["november"] = o.election_date.str.startswith("November")
    o["source"] = citekeys.OLEARY + " p." + o.page
    return o


def state_return() -> pd.DataFrame:
    """Every ticket of the Commonwealth's return for President as keyed, one
    row each, with the page it prints on and the line it was read from. The
    office stays as keyed; the clean stage decides what each ticket is."""
    r = source(STATE_RETURN, dtype=str).fillna("")
    return pd.DataFrame({
        "record": "state_return", "office": r.office, "contest": r.year + " " + r.office,
        "year": r.year, "page": r.page, "candidate": r.candidate, "name": r.candidate,
        "votes": r.votes, "party": r.party, "person": True, "writein": False, "prose": False,
        "source": r.source, "read_from": r.read_from, "quote": r.quote, "note": r.note})


def gazette_return() -> pd.DataFrame:
    """Every ticket of the Alexandria Gazette's own district returns for
    President as keyed, one row each, with the district, the page it prints
    on and the line it was read from. The office stays as keyed; the clean
    stage decides what each ticket is."""
    r = source(GAZETTE_RETURN, dtype=str).fillna("")
    return pd.DataFrame({
        "record": "gazette_return", "office": r.office, "district": r.district,
        "contest": r.year + " " + r.office + " " + r.district, "year": r.year, "page": r.page,
        "candidate": r.candidate, "name": r.candidate, "votes": r.votes, "party": r.party,
        "person": True, "writein": False, "prose": False,
        "source": r.source, "read_from": r.read_from, "quote": r.quote, "note": r.note})


def press_return() -> pd.DataFrame:
    """Every County Board count a newspaper printed that the county's history
    leaves blank, one row each, with the page it prints on and the line it
    was read from. The clean stage decides which blank each one fills."""
    r = source(PRESS_RETURN, dtype=str).fillna("")
    return pd.DataFrame({
        "record": "press_return", "office": r.office, "election_date": r.election_date,
        "contest": r.year + " " + r.election_date + " " + r.office, "year": r.year,
        "page": r.page, "candidate": r.candidate, "name": r.candidate, "votes": r.votes,
        "person": True, "writein": False, "prose": False,
        "source": r.source, "read_from": r.read_from, "quote": r.quote, "note": r.note})


COLUMNS = ["record", "contest", "office", "district", "year", "election_date", "election_kind",
           "page", "month", "november", "primary", "special", "seats", "fills", "candidate",
           "name", "entry", "votes", "person", "writein", "prose", "party", "primary_party",
           "is_winner", "source", "read_from", "quote", "note"]


def build() -> pd.DataFrame:
    d = pd.concat([county()] + [state(p) for p in STATE]
                  + [oleary(p, office) for p, office in OLEARY.items()]
                  + [state_return(), gazette_return(), press_return()],
                  ignore_index=True)
    return d[COLUMNS]


if __name__ == "__main__":
    write(build(), "elections")
