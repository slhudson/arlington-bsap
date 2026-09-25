"""The two election records the Board builds read, each loaded once.

A module, not a step: it writes nothing. Each file is read one way, and
the callers select from it.

    contests()         both records as one table, one row per candidate per
                       contest, with the contest's own facts on each row
    contest_rows()     one year's county rows reduced to the contest's own
                       lines, and whether they are the county's whole vote
    county_history()   the county's candidate history for one office
    state_results()    one of the state's files, with its non-candidate
                       rows marked
    labels_on()        the party labels the county prints after a name
    label_of()         the one label a row carries, or ""
    surname()          the surname, as both records are matched on

The county's candidate history (arlingtonelections2021) runs to the 2021
election. Every County Board row is kept, primaries and write-ins
included, and the frame says what each row is. The state's database
(vaelections) is one row per candidate per precinct per vote channel; its
non-candidate rows are marked rather than dropped.
"""
import re

import numpy as np
import pandas as pd

import citekeys
from paths import BY_CLAUDE, RAW

COUNTY = BY_CLAUDE / "arlington_county" / "candidate_history_1920-present.csv"
STATE = RAW / "va_dept_of_elections" / "county_board_2000-2026.csv"

# The last election in the county's candidate history.
COUNTY_HISTORY_THROUGH = 2021

BOARD = re.compile(r"^(Member, )?County Board\b")      # a contest heading, any qualifier after
NAMED = re.compile(r"^[*A-Z]")                          # a row naming a candidate
# The qualifiers a contest heading carries.
TWO_SEATS = re.compile(r"two seats|2 seats|vote for 2|two elected", re.I)
SPECIAL = re.compile(r"special|unexpired", re.I)
# "(to fill Eisenberg's unexpired term)", "(... following death of Charles Monroe)"
FILLS = re.compile(r"to fill ([A-Za-z]+)['\u2019]s unexpired term|death of ([A-Za-z. ]+?)\)", re.I)
PARTY_LABEL = re.compile(r"\s*\((?:[^)]+)\)\s*$")

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}

# The label the county prints in parentheses after a name, and what it
# records. A label not listed here stops the build.
LABELS = {
    "D": "Democratic",
    "R": "Republican", "Rep.": "Republican",
    "ABC": "ABC",                      # Arlingtonians for a Better County
    "I": "independent", "Non-Part.": "independent", "Non-Partisan": "independent",
    "NP": "independent",
    "IM": "independent",               # 1954, presumably Arlington Independent Movement
    "Convention": "",                  # 1955: a convention the source does not name
    # Labels no winner has carried; board_members.py stops on one.
    "AIM": "other", "Ind. Dem.": "other", "Ind. Rep.": "other",
    "G": "other", "IG": "other", "Va. Reform": "other",
}
PARTIES = {"Democratic", "Republican", "ABC", "independent"}
NOT_A_LABEL = {"won", "inc.", "holdover", "not on ballot"}
LABEL = re.compile(r"\(([^()]*)\)")


def labels_on(candidate) -> set:
    """The party labels printed after a name, as a set; usually one or none."""
    return {l.strip() for l in LABEL.findall(str(candidate))} - NOT_A_LABEL


def label_of(candidate, where="") -> str:
    """The one party label a candidate row carries, or "" for none."""
    labels = sorted(labels_on(candidate))
    if len(labels) > 1:
        raise ValueError(f"{where}{candidate!r} carries more than one label: {labels}")
    label = labels[0] if labels else ""
    if label and label not in LABELS:
        raise ValueError(f"{where}label ({label}) on {candidate!r} is not one this build "
                         f"knows. Add it to elections.LABELS with what it records, or fix "
                         f"the reading.")
    return label


def surname(name) -> str:
    """The surname, lowercased, ignoring the qualifiers the sources hang off
    a name: "*Elizabeth B. Magruder (holdover)", "Magruder, conservative"."""
    s = re.sub(r"\(.*?\)", " ", str(name))          # (won), (D), (holdover)
    s = re.split(r"[,–-]", s)[0]                 # ", conservative", " - removed for..."
    s = re.sub(r"\b(Jr|Sr|II|III|IV|Dr|Mrs|Mr)\b\.?", "", s)
    s = re.sub(r"[^A-Za-z ]", " ", s).split()
    return s[-1].lower() if s else ""


# What the county prints when a year's total is not the county's vote.
PARTIAL = re.compile(r"not mentioned|not final|\d+ of \d+ precincts", re.I)


def contest_rows(g):
    """One year's County Board rows, reduced to the contest's own lines.

    `g` is the year's rows with primaries left out and prose and write-ins
    kept. Returns (rows, complete, note): the candidate and write-in rows,
    deduplicated; whether they are the county's whole vote; and if not, why.

    A block (one page, one date) with no count on any row is a list of the
    Board, not a contest, unless the year has no counts anywhere. A
    candidate with the same count twice in one year is one candidate. A
    year is not the county's vote where a named candidate has no count,
    the page says its totals are from some precincts, or it says others ran
    who are not listed.
    """
    blocks = g.groupby(["page", "election_date"]).votes.apply(lambda v: v.notna().any())
    if blocks.any():
        g = g[[blocks[k] for k in zip(g.page, g.election_date)]]
    named = g[~g.prose].copy()
    named["key"] = [surname(n.lstrip("*W. ")) for n in named.candidate]
    named = named.drop_duplicates(["key", "votes"])
    missing = sorted(named[named.votes.isna()].key.unique())
    partial = [t for t in pd.concat([g.candidate, g.office]) if PARTIAL.search(t)]
    note = "; ".join(filter(None, [
        f"no vote count for {', '.join(missing)}" if missing else "",
        partial[0] if partial else ""]))
    return named, not (missing or partial), note


def county_history(office=BOARD) -> pd.DataFrame:
    """Every row of the county's candidate history for `office`, text
    columns as transcribed with blanks as "", plus:

        year       int
        votes      the count as a number; NaN where the page prints none
        prose      the row is a remark about the contest, not a candidate
        writein    the write-in line
        person     the row names a candidate: neither of the above
        november   a November election, as against a primary or an
                   off-month special
        primary    the row is from a primary
        surname    surname() of the candidate
    """
    c = pd.read_csv(COUNTY, dtype=str).fillna("")
    # "County Board Candidates" heads a pointer to an article, not a contest.
    c = c[c.office.str.match(office) & ~c.office.str.startswith("County Board Candidates")].copy()
    if not c.year.str.match(r"^\d{4}$").all():
        raise AssertionError("a County Board row has no four-digit year")
    c["year"] = c.year.astype(int)
    c["votes"] = pd.to_numeric(c.votes.str.replace(",", ""), errors="coerce")
    c["prose"] = ~c.candidate.str.match(NAMED) | c.candidate.str.contains(":")
    c["writein"] = c.candidate.str.contains("write", case=False)
    c["person"] = ~c.prose & ~c.writein
    c["november"] = c.election_date.str.startswith("November")
    c["primary"] = c.election_kind.str.contains("Primary")
    c["surname"] = c.candidate.map(surname)
    return c.reset_index(drop=True)


def contests() -> pd.DataFrame:
    """Both records as one table: every County Board row of the county's
    candidate history, and every candidate of every contest in the state's
    file with their precinct rows summed. Each row carries its contest's
    own facts:

        record      "county" or "state"
        contest     an id shared by the contest's rows
        year, month, november, primary, kind
        special     a special election, by the contest's label or an
                    off-November date
        seats       how many seats the contest filled
        fills       whose unexpired term a special fills, by surname, or ""
        candidate   as printed; `name` is it without the county's label
        surname, votes, person, writein, prose
        party, primary_party, is_winner    the state's columns; is_winner is
                    true if any precinct row says so
        source      the citation for the row

    The county's text columns and page stay on its rows for contest_rows().
    County rows come first, in page order; state rows follow, in contest order.
    """
    c = county_history()
    c["base"] = c.office.str.replace(r"\s*\(.*", "", regex=True).str.strip()
    key = ["year", "election_date", "base"]
    c = c.merge(c.groupby(key).office.agg(" ".join).rename("qualifiers"),
                left_on=key, right_index=True)
    c["record"] = "county"
    c["contest"] = c.year.astype(str) + " " + c.election_date + " " + c.base
    c["month"] = c.election_date.str[:3].map(MONTHS)
    c["kind"] = c.election_kind
    c["special"] = c.qualifiers.str.contains(SPECIAL) | ~c.november
    c["seats"] = np.where(c.qualifiers.str.contains(TWO_SEATS), 2, 1)
    fills = c.qualifiers.str.extract(FILLS)
    c["fills"] = [surname(a if isinstance(a, str) else b) if isinstance(a, str) or isinstance(b, str)
                  else "" for a, b in zip(fills[0], fills[1])]
    c["name"] = c.candidate.str.replace(PARTY_LABEL, "", regex=True).str.strip()
    c["source"] = citekeys.ARLINGTON_ELECTIONS + " p." + c.page

    s = state_results()
    s = s[s.person | s.writein]
    g = s.groupby(["contest_id", "candidate_name"], sort=False).agg(
        votes=("votes", "sum"), date=("date", "first"), kind=("election_type", "first"),
        seats=("number_seats", "first"), party=("candidate_party_name", "first"),
        primary_party=("primary_party", "first"),
        is_winner=("is_winner", lambda v: bool(v.fillna(False).astype(bool).any())),
        person=("person", "first"), writein=("writein", "first")).reset_index()
    t = pd.DataFrame({
        "record": "state", "contest": g.contest_id.astype(str),
        "year": g.date.dt.year, "month": g.date.dt.month, "november": g.date.dt.month == 11,
        "primary": g.kind.str.startswith("Primary"), "kind": g.kind,
        "special": g.date.dt.month != 11, "seats": g.seats.astype(int), "fills": "",
        "candidate": g.candidate_name, "name": g.candidate_name,
        "surname": g.candidate_name.map(surname), "votes": g.votes,
        "person": g.person, "writein": g.writein, "prose": False,
        "party": g.party, "primary_party": g.primary_party, "is_winner": g.is_winner,
        "source": citekeys.VA_ELECTIONS + " contest " + g.contest_id.astype(str)})
    return pd.concat([c, t], ignore_index=True)


def state_results(path=STATE) -> pd.DataFrame:
    """Every row of one of the state's files, the County Board's unless
    another is given, plus:

        date       election_date as a date
        year       int
        person     the row names a candidate: not a total, an undervote
                   count or the write-in line
        writein    the write-in line
        surname    surname() of the candidate
    """
    s = pd.read_csv(path, low_memory=False)
    s["date"] = pd.to_datetime(s.election_date)
    s["year"] = s.date.dt.year
    s["writein"] = s.candidate_name.str.startswith("Write", na=False)
    s["person"] = ~s.candidate_name.str.match(r"^(Total|Write|Under|Over)", na=False)
    s["surname"] = s.candidate_name.map(surname)
    return s
