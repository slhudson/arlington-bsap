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

A County Board candidacy the county's history prints on a second page, in
another format, is collapsed to one row before anything else reads it:
_dedup_board_pages() (docs/candidates.md, "Duplicate pages").
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


def _dedup_board_pages(e: pd.DataFrame) -> pd.DataFrame:
    """One row per County Board candidacy per contest.

    The county's candidate history sometimes prints a contest twice: a
    results table, with vote counts, and a narrative of the board's
    turnover (holdovers, incumbents, an appointment), without. The two can
    even disagree on the contest's exact date. Within a year, office and
    kind of election (regular, special or primary - not the printed date,
    which the two pages need not share), a candidate named on more than one
    page keeps the row with a vote count, or the first row if neither page
    has one; a second table transcribed twice collapses to whichever copy
    is read first. The narrative's own words for the candidate survive in
    `status`; if the kept row carries no party label and a dropped one
    carries exactly one, it moves onto the kept row so label_of() still
    finds it. Two pages
    naming the same candidate with two different counts is not this
    pattern, and stops the build.

    Rows for every other office pass through unchanged, `status` blank.
    """
    board = (e.record == "county") & e.office.str.match(BOARD)
    rest = e[~board].assign(status="")
    if not board.any():
        return rest
    b = e[board].copy()
    b["_votes"] = pd.to_numeric(b.votes.str.replace(",", ""), errors="coerce")
    b["_surname"] = b.candidate.map(surname)
    b["_base"] = b.office.str.replace(r"\s*\(.*", "", regex=True).str.strip()
    b["status"] = ""
    kept = []
    for key, g in b.groupby(["year", "_base", "primary", "special"], sort=False):
        named = g[g.person == "True"]
        for _, rows in named.groupby("_surname", sort=False):
            if len(rows) == 1:
                kept.append(rows)
                continue
            with_votes = rows[rows._votes.notna()]
            if with_votes._votes.nunique() > 1:
                raise ValueError(
                    f"{key[0]} {key[1]}: {rows.candidate.iloc[0]!r} and "
                    f"{rows.candidate.iloc[-1]!r} carry different vote counts across pages "
                    f"{sorted(rows.page.unique())} - not the same candidacy twice, or a real "
                    f"disagreement to resolve by hand")
            keep = (with_votes if len(with_votes) else rows).iloc[[0]].copy()
            others = [t for t in rows.candidate if t != keep.candidate.iloc[0]]
            keep["status"] = "; ".join(others)
            if not labels_on(keep.candidate.iloc[0]):
                found = {l for t in others for l in labels_on(t)}
                if len(found) == 1:
                    keep["candidate"] = keep.candidate + f" ({found.pop()})"
            kept.append(keep)
        kept.append(g[g.person != "True"])
    b = pd.concat(kept).drop(columns=["_votes", "_surname", "_base"])
    return pd.concat([rest, b]).sort_index()


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
    a contest. The Commonwealth's return for President has state_return()."""
    return (e.record.isin(["county", "state"]) & e.office.str.match(office)
            & ~e.office.str.startswith("County Board Candidates"))


def contests(office=BOARD) -> pd.DataFrame:
    """Both records' rows for `office`, typed, county rows first."""
    e = _dedup_board_pages(paths.built("elections"))
    return _typed(e[_selected(e, office)])


def county_history(office=BOARD) -> pd.DataFrame:
    """The county's candidate history for `office`, typed."""
    e = _dedup_board_pages(paths.built("elections"))
    return _typed(e[(e.record == "county") & _selected(e, office)])


def oleary(office) -> pd.DataFrame:
    """O'Leary's entries for `office`, as printed: year and page as numbers,
    the entry and the district as text."""
    e = paths.built("elections")
    o = e[(e.record == "oleary") & e.office.str.match(office)]
    o = o[["page", "year", "election_date", "district", "entry"]].reset_index(drop=True)
    return o.astype({"page": int, "year": int})


def state_return() -> pd.DataFrame:
    """The Commonwealth's county return for President, one row per ticket as
    keyed: year and votes as numbers, the rest as printed."""
    e = paths.built("elections")
    r = e[e.record == "state_return"].copy()
    r["year"] = r.year.astype(int)
    r["votes"] = pd.to_numeric(r.votes).astype(int)
    return r.reset_index(drop=True)
