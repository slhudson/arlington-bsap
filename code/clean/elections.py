"""Selecting from the election table code/build/elections.py wrote.

A module, not a step: it writes nothing. data/built/elections.csv holds
both records, every office; this module picks an office, gives the columns
their types, and reads the county's labels.

    contests()         both records for one office, one row per candidate
                       per contest, typed, with the surname each record is
                       matched on
    county_history()   the county's rows alone for one office
    contest_rows()     one year's county rows reduced to the contest's own
                       lines, and whether they are the county's whole vote
    labels_on()        the party labels the county prints after a name
    label_of()         the one label a row carries, or ""
    surname()          the surname, as both records are matched on

The county's candidate history (arlingtonelections2021) runs to the 2021
election; the state's database (vaelections) is read from 2000.
"""
import re

import numpy as np
import pandas as pd

import paths

# The last election in the county's candidate history.
COUNTY_HISTORY_THROUGH = 2021

BOARD = re.compile(r"^(Member, )?County Board\b")      # a contest heading, any qualifier after
PRESIDENT = re.compile(r"^President")
SUPERVISORS = re.compile(r"^Board of Supervisors$")     # O'Leary's district listings, 1870-1920

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
    # Labels no winner has carried; members.py stops on one.
    "AIM": "other", "Ind. Dem.": "other", "Ind. Rep.": "other",
    "G": "other", "IG": "other", "Va. Reform": "other",
}
PARTIES = {"Democratic", "Republican", "ABC", "independent"}
NOT_A_LABEL = {"won", "inc.", "holdover", "not on ballot"}
LABEL = re.compile(r"\(([^()]*)\)")

FLAGS = ["november", "primary", "special", "person", "writein", "prose"]


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


def _typed(e: pd.DataFrame) -> pd.DataFrame:
    """The built rows with their types: years and counts as numbers, flags
    as booleans, and the state's blank party as missing rather than ""."""
    e = e.copy()
    if not e.year.str.match(r"^\d{4}$").all():
        raise AssertionError("a selected election row has no four-digit year")
    e["year"] = e.year.astype(int)
    e["kind"] = e.election_kind
    e["month"] = pd.to_numeric(e.month)
    e["seats"] = pd.to_numeric(e.seats).astype(int)
    e["votes"] = pd.to_numeric(e.votes)
    for c in FLAGS:
        e[c] = e[c] == "True"
    e["is_winner"] = e.is_winner.map({"True": True, "False": False})
    for c in ("party", "primary_party"):
        e[c] = e[c].where(e[c] != "", np.nan)
    e["surname"] = e.candidate.map(surname)
    return e.reset_index(drop=True)


def _selected(e: pd.DataFrame, office) -> pd.Series:
    """The county's and the state's rows for `office`; O'Leary's entries have
    oleary(). "County Board Candidates" heads a pointer to an article, not
    a contest."""
    return ((e.record != "oleary") & e.office.str.match(office)
            & ~e.office.str.startswith("County Board Candidates"))


def contests(office=BOARD) -> pd.DataFrame:
    """Both records' rows for `office`, typed, county rows first."""
    e = paths.built("elections")
    return _typed(e[_selected(e, office)])


def county_history(office=BOARD) -> pd.DataFrame:
    """The county's candidate history for `office`, typed."""
    e = paths.built("elections")
    return _typed(e[(e.record == "county") & _selected(e, office)])


def oleary(office) -> pd.DataFrame:
    """O'Leary's entries for `office`, as printed: year and page as numbers,
    the entry and the district as text."""
    e = paths.built("elections")
    o = e[(e.record == "oleary") & e.office.str.match(office)]
    o = o[["page", "year", "election_date", "district", "entry"]].reset_index(drop=True)
    return o.astype({"page": int, "year": int})
