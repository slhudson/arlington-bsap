"""The two election records the Board builds read, each loaded once.

A module, not a step: it writes nothing. board_roster, board_members,
voters and turnout all read the county's candidate history and the state's
elections database, and each used to open the file itself with its own
idea of which rows were County Board rows and which candidates were
people. Six filters for one file is how they drift apart - one matching
"County Board" anywhere in the office, another only at its start, a third
also dropping the prose block the 1931 page carries. Here the file is read
one way and the callers select from it.

    county_history()   the county's candidate history, County Board rows,
                       1931 to COUNTY_HISTORY_THROUGH
    state_results()    the state's database, County Board contests, 2000 on
    label_of()         the party label the county prints after a name
    surname()          the surname, as both records are matched on

**The county's candidate history** (arlingtonelections2021) runs to the 2021
election and the county no longer publishes it. Every County Board row is
kept, primaries and write-ins included; the frame says what each row is and
a caller chooses. Votes are numbers, blank where the page prints none.

**The state's database** (vaelections) is the Department of Elections' own
CSV, one row per candidate per precinct per vote channel, so a candidate's
votes are summed by whoever needs them. It is the only source from 2022.
Four rows per contest are not candidates - the ballot and vote totals, the
undervotes, and write-ins - and the frame marks them rather than dropping
them, because turnout counts write-ins as votes cast and the roster does not.
"""
import re

import pandas as pd

from paths import RAW, TRANSCRIBED

COUNTY = TRANSCRIBED / "by_claude" / "arlington_county" / "candidate_history_1920-present.csv"
STATE = RAW / "va_dept_of_elections" / "county_board_2000-2026.csv"

# The last election in the county's candidate history. The state database is
# the source after it, and the build checks the two agree on this year.
COUNTY_HISTORY_THROUGH = 2021

# A County Board contest's heading, whatever qualifier follows it - "(two
# seats)", "(to fill Favola's unexpired term)", "Special Election".
BOARD = re.compile(r"^(Member, )?County Board\b")
# A row that names a candidate begins with a capital (or the asterisk some
# years put on the winner). The page also carries prose - "(others not
# mentioned)", "Running Before Primary:", "[Listing attached]" - and write-ins.
NAMED = re.compile(r"^[*A-Z]")

# --- the county's party labels ----------------------------------------------
# The label the county prints in parentheses after a candidate's name, and
# what it records. Every label a County Board candidate has carried is here;
# one that is not stops the build, because a new label is a decision and not
# a default. board_members.py accepts a winner only under the four parties
# and the convention case; voters.py counts every vote, so the minor labels
# fall into "other" there.
LABELS = {
    "D": "Democratic",
    "R": "Republican", "Rep.": "Republican",
    "ABC": "ABC",                      # Arlingtonians for a Better County
    "I": "independent", "Non-Part.": "independent", "Non-Partisan": "independent",
    "NP": "independent",
    "IM": "independent",               # 1954, presumably Arlington Independent Movement
    # Kaul and Krupsaw, 1955: nominated by a convention the source does not
    # name. Not a party, so nothing is recorded; the note keeps the label.
    "Convention": "",
    # Labels only losing candidates have carried. A winner under one of these
    # would be a decision for a person, and board_members.py stops on it.
    "AIM": "other", "Ind. Dem.": "other", "Ind. Rep.": "other",
    "G": "other", "IG": "other", "Va. Reform": "other",
}
PARTIES = {"Democratic", "Republican", "ABC", "independent"}
# Parentheticals that are not labels: "(won)", "(inc.)", "(holdover)".
NOT_A_LABEL = {"won", "inc.", "holdover", "not on ballot"}
LABEL = re.compile(r"\(([^()]*)\)")


def labels_on(candidate) -> set:
    """The party labels printed after a name, as a set; usually one or none."""
    return {l.strip() for l in LABEL.findall(str(candidate))} - NOT_A_LABEL


def label_of(candidate, where="") -> str:
    """The one party label a candidate row carries, or "" for none.

    Raises where the row prints more than one, or one this module does not
    know: either is a reading for a person to settle, not a value to guess.
    """
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
    """The surname, ignoring the qualifiers the sources hang off a name.

    Candidate entries carry party, status and outcome - "*Elizabeth B. Magruder
    (holdover)", "Elizabeth B. Magruder (won)" - so anything in parentheses,
    anything after a comma or dash, and honorifics are dropped before the last
    word is taken. Without this, Magruder's surname reads as "won". Both
    records are matched on it, because the state spells names its own way
    ("Matthew David De Ferranti" for the county's "Matthew D. \"Matt\" de
    Ferranti").
    """
    s = re.sub(r"\(.*?\)", " ", str(name))          # (won), (D), (holdover)
    s = re.split(r"[,–-]", s)[0]                 # ", conservative", " - removed for..."
    s = re.sub(r"\b(Jr|Sr|II|III|IV|Dr|Mrs|Mr)\b\.?", "", s)
    s = re.sub(r"[^A-Za-z ]", " ", s).split()
    return s[-1].lower() if s else ""


def county_history(office=BOARD) -> pd.DataFrame:
    """Every County Board row of the county's candidate history.

    Text columns as transcribed, blanks as "", plus:

        year       int
        votes      the count as a number; NaN where the page prints none
        prose      the row is a remark about the contest, not a candidate
        writein    the write-in line
        person     the row names a candidate: neither of the above
        november   a November election, as against a primary or an
                   off-month special
        primary    the row is from a primary
        surname    surname() of the candidate

    `office` narrows the rows to another office's - voters.py checks the
    presidential returns the same pages print.
    """
    c = pd.read_csv(COUNTY, dtype=str).fillna("")
    # The 1931 page carries a block headed "County Board Candidates" that is
    # a pointer to an article, not a contest. Its office is not the Board's.
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
        writein    the write-in line, which turnout counts as votes cast
        surname    surname() of the candidate
    """
    s = pd.read_csv(STATE, low_memory=False)
    s["date"] = pd.to_datetime(s.election_date)
    s["year"] = s.date.dt.year
    s["writein"] = s.candidate_name.str.startswith("Write", na=False)
    s["person"] = ~s.candidate_name.str.match(r"^(Total|Write|Under|Over)", na=False)
    s["surname"] = s.candidate_name.map(surname)
    return s
