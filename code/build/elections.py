"""The two election records as one table -> data/built/elections.csv

One row per candidate per contest, every office, both records, with the
contest's own facts on each row. Nothing is chosen: every row of the
county's candidate history is here, prose and write-ins included, and
every candidate in the state's files, their precinct rows summed.
code/clean/elections.py selects from it.

    record      "county" (arlingtonelections2021, to 2021) or "state"
                (vaelections, 2000 on)
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
         RAW / "va_dept_of_elections" / "president_1924-2024.csv")

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


COLUMNS = ["record", "contest", "office", "year", "election_date", "election_kind", "page",
           "month", "november", "primary", "special", "seats", "fills", "candidate", "name",
           "votes", "person", "writein", "prose", "party", "primary_party", "is_winner", "source"]


def build() -> pd.DataFrame:
    d = pd.concat([county()] + [state(p) for p in STATE], ignore_index=True)
    return d[COLUMNS]


if __name__ == "__main__":
    write(build(), "elections")
