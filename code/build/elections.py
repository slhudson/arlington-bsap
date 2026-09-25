"""The two election records the Board builds read, each loaded once.

A module, not a step: it writes nothing. Each file is read one way, and
the callers select from it.

    county_history()   the county's candidate history, County Board rows,
                       1931 to COUNTY_HISTORY_THROUGH
    contest_rows()     one year's rows reduced to the contest's own lines,
                       and whether they are the county's whole vote
    state_results()    the state's database, County Board contests, 2000 on
    label_of()         the party label the county prints after a name
    surname()          the surname, as both records are matched on

The county's candidate history (arlingtonelections2021) runs to the 2021
election. Every County Board row is kept, primaries and write-ins
included, and the frame says what each row is. The state's database
(vaelections) is one row per candidate per precinct per vote channel; its
non-candidate rows are marked rather than dropped.
"""
import re

import pandas as pd

from paths import RAW, TRANSCRIBED

COUNTY = TRANSCRIBED / "by_claude" / "arlington_county" / "candidate_history_1920-present.csv"
STATE = RAW / "va_dept_of_elections" / "county_board_2000-2026.csv"

# The last election in the county's candidate history.
COUNTY_HISTORY_THROUGH = 2021

BOARD = re.compile(r"^(Member, )?County Board\b")      # a contest heading, any qualifier after
NAMED = re.compile(r"^[*A-Z]")                          # a row naming a candidate

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


def state_results() -> pd.DataFrame:
    """Every row of the state's County Board file, plus:

        date       election_date as a date
        year       int
        person     the row names a candidate: not a total, an undervote
                   count or the write-in line
        writein    the write-in line
        surname    surname() of the candidate
    """
    s = pd.read_csv(STATE, low_memory=False)
    s["date"] = pd.to_datetime(s.election_date)
    s["year"] = s.date.dt.year
    s["writein"] = s.candidate_name.str.startswith("Write", na=False)
    s["person"] = ~s.candidate_name.str.match(r"^(Total|Write|Under|Over)", na=False)
    s["surname"] = s.candidate_name.map(surname)
    return s
