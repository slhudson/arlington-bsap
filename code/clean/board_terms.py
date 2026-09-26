"""What a term on the Board is, for every source the roster is read from.
A module, not a step.

The seats that exist, how a term begins, how long one runs by statute and
the year the roster is checked to; and the readers the sources share, a
month or a year in a source's prose and a term listing in
data/built/board_claims.csv. docs/board.md has the reasoning.
"""
import re

import pandas as pd

import paths
from elections import MONTHS

PRESENT = 2026            # checked month by month up to here; board_seats stops here

# The seats that exist: three district supervisors from 1870, five members
# at large from January 1932 (anderson1958).
SEATS_DISTRICT = 3.0
SEATS_AT_LARGE = 5.0
AT_LARGE_FROM = 1932

# The values seated_by takes: how a term began.
ELECTION = "election"
SPECIAL_ELECTION = "special election"
APPOINTMENT = "appointment"
UNRECORDED = "unrecorded"
SEATED_BY = (ELECTION, SPECIAL_ELECTION, APPOINTMENT, UNRECORDED)

# Va. Const. 1902 sec. 112, applied from the November 1903 election.
TERM_YEARS = 4

MONTH = rf"({'|'.join(MONTHS)})[a-z]*\.?"          # "Dec", "December", "Dec."
MONTH_RE = re.compile(r"\b" + MONTH, re.I)
YEAR_RE = re.compile(r"\b((?:18|19|20)\d\d)\b")


def seats(year):
    """The seats that existed in a year."""
    return SEATS_DISTRICT if year < AT_LARGE_FROM else SEATS_AT_LARGE


def month_of(text):
    """The first month a text names, as a number, or "" for none."""
    m = MONTH_RE.search(text or "")
    return MONTHS[m.group(1).title()] if m else ""


def listing(kind) -> pd.DataFrame:
    """The rows of one term listing, from data/built/board_claims.csv, every
    cell as keyed in and a blank a blank."""
    c = paths.built("board_claims")
    return c[c.claim == kind].reset_index(drop=True)
