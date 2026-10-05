"""Who held each seat and when, 1870 through 2026, one row per person per term.

A module, not a step: members.py takes these terms and attaches race,
gender and party.

    name  district  start_year  start_month  end_year  end_month  seated_by  source  note

`district` is a magisterial district through 1931 and "at large" from 1932.
`seated_by` is how the term began: a regular election, a special election,
an appointment, or unrecorded. Months are given where a source gives them;
a November winner is seated the following January. A vacant seat is not a
row. The reasoning is in docs/members.md.

Sources, in sequence, one module each:

  oleary2010       1870-1915  members_roster_oleary.py    who held each magisterial
                                                        district, by election
  arlhist1967off.  1912-1931  members_roster_arlhist.py   the Board block by
                                                        block, from its minute
                                                        books
  novack1994       1932-1994  members_roster_novack.py    terms of service, with
                                                        mid-term departures
  election results 1995-      members_roster_results.py   the county's candidate
                                                        history to 2021, the
                                                        state's database from 2022

O'Leary's last listed election is 1915 and Novack begins in 1930, so
1912-1931 rests on the Historical Society's article, which names all three
magisterial seats for all twenty years save one Washington vacancy it
states. The county's candidate history prints the district races of
November 1923 and 1927, keyed in members_terms.csv and read by
members_roster_results.py; the article closes those terms. What a term is,
the seats that exist, how a term begins, the readers the sources share, is
members_terms.py.
"""
import re

import pandas as pd

import members_roster_arlhist as arlhist
import members_roster_novack as novack
import members_roster_oleary as oleary
import members_roster_results as results
import members_roster_roll as roll
from members_terms import (APPOINTMENT, AT_LARGE_FROM, ELECTION, PRESENT, SEATED_BY,
                           SPECIAL_ELECTION, UNRECORDED)


def check_seats(d: pd.DataFrame, first=AT_LARGE_FROM, last=PRESENT):
    """Five at-large seats, each held by one member in every month from 1932,
    save the eight months members_roster_roll.vacancies() names.

    The vacancies are the point, as they are for the districts below. Five
    seats exist from 1932; whether all five are filled in a given month is a
    fact about the world, and eight times since it has not been - Arlington
    ran with four members while a special election was called. A seat nobody
    held counts towards nobody, so an undeclared gap stops the build and so
    does filling a declared one.

    A mid-term arrival takes the seat in the month it was vacated, because a
    month belongs to whoever held it for any part of it, so that month holds
    two rows for one seat and the count is six. Katie Cristol's July 2023 and
    Tannia Talento's are the same month that way.
    """
    at_large = d[d.district == "at large"]
    start = (at_large.start_year * 12 + at_large.start_month).astype(int)
    end = (pd.to_numeric(at_large.end_year) * 12
           + pd.to_numeric(at_large.end_month)).astype(int)
    midterm = start[at_large.seated_by.isin([SPECIAL_ELECTION, APPOINTMENT])]
    empty = roll.vacancies()
    for m in range(first * 12 + 1, last * 12 + 13):
        year, month = (m - 1) // 12, (m - 1) % 12 + 1
        held = [n for n, lo, hi in zip(at_large.name, start, end) if lo <= m <= hi]
        handover = min((end == m).sum(), (midterm == m).sum())
        expected = 5 - (1 if (year, month) in empty else 0) + handover
        if len(held) != expected:
            raise ValueError(
                f"{year}-{month:02d}: {len(held)} members at large, expected {expected}"
                + (" (a declared vacancy)" if (year, month) in empty else "")
                + f": {sorted(held)}\n  a gap no source accounts for is an error; one a "
                  f"source records belongs in EMPTY in code/clean/members_roster_roll.py.")


NOT_A_NAME = re.compile(r"\b(?:elected|contested|replaced|appointed|vacant|resigned|died)\b|\d", re.I)


def check_names(d: pd.DataFrame):
    """A name is a name. Prose that reached this column was not parsed."""
    bad = d[d.name.str.contains(NOT_A_NAME, regex=True)]
    if len(bad):
        raise ValueError("these names read as prose, not people:\n"
                         + "\n".join(f"  {n!r}" for n in bad.name))


def check_seated_by(d: pd.DataFrame):
    """Every term says how it began, in one of the four words, and none is
    unrecorded from 1932."""
    bad = d[~d.seated_by.isin(SEATED_BY)]
    if len(bad):
        raise ValueError("seated_by must be one of "
                         f"{', '.join(SEATED_BY)}; these are not:\n"
                         + "\n".join(f"  {r['name']} {r.start_year}: {r.seated_by!r}"
                                     for _, r in bad.iterrows()))
    unrecorded = d[(d.start_year >= 1932) & (d.seated_by == UNRECORDED)]
    if len(unrecorded):
        raise ValueError("seated_by is unrecorded for terms after 1931, where every "
                         "source says how a term began:\n"
                         + "\n".join(f"  {r['name']} {r.start_year}"
                                     for _, r in unrecorded.iterrows()))


# The Jefferson seat's four roster rows for 1908-28 are one man, Edward
# Duncan, not up to three: the Alexandria Gazette shows him in office, as
# chairman, from 1913 through 1915 and again 1919 through 1921, covering
# both stretches the roster otherwise leaves blank between the four
# recorded elections. He did not seek re-election in 1931, running instead
# for sheriff and losing, in a piece giving the same "24 years" of board
# service as his 1938 obituary (not yet filed): 1908 to 1932. Sally decided
# to record this as one term rather than six or four (duncan-one-member-or-
# three, 2026-09-27); the 1912 and 1928 renewals are known only by that
# continuity, not by a recorded election win, unlike 1908, 1916, 1920 and
# 1924. docs/members.md.
DUNCAN_SOURCES = ("oleary2010 p.25", "arlhist1967officials p.42-43",
                   "alexandriagazette1913duncan",
                   "alexandriagazette1914duncan", "oleary2010 p.27",
                   "alexandriagazette1915duncan", "alexandriagazette1919duncan",
                   "arlingtonelections2021 p.2", "alexandriagazette1921duncan",
                   "arlingtonelections2021 p.4", "washingtontimes1930duncan",
                   "washingtontimes1931duncan")
DUNCAN_NOTE = (
    "One continuous term, not four: the roster's E. Duncan (1908-12), Duncan "
    "(1916-20) and Edward Duncan (1924-28, two terms) are one man. Elections "
    "are recorded for 1908, 1916, 1920 and 1924; the Alexandria Gazette also "
    "shows him in office, as chairman, from 1913 through 1915 and again from "
    "1919 through 1921, covering both stretches the roster otherwise leaves "
    "blank. He did not seek re-election in 1931, running instead for sheriff "
    "and losing, in a piece giving the same 24 years' service as his 1938 "
    "obituary (not yet filed): 1908 to 1932. The 1912 and 1928 renewals are "
    "known only by that continuity, not by a recorded election win "
    "(docs/members.md)."
)


def apply_duncan_join(d: pd.DataFrame) -> pd.DataFrame:
    """Collapse the Jefferson seat's four 1908-28 roster rows into Edward
    Duncan's one continuous term. See the comment above and docs/members.md."""
    duncan = ((d.district == "Jefferson") & d.name.isin(["E. Duncan", "Duncan", "Edward Duncan"])
              & (d.start_year >= 1908) & (d.start_year <= 1928))
    # Four sources name stretches of the same seat and they overlap, so what
    # matters is not how many rows there are but that together they reach
    # from 1908 to 1932 without a gap. A gap would mean a stretch nobody
    # records, which is a term of someone else's, not part of this one.
    rows = d[duncan].sort_values(["start_year", "start_month"])
    covered = 1908 * 12            # the month before the first, as a month from year 0
    for _, t in rows.iterrows():
        if t.start_year * 12 + t.start_month > covered + 1:
            raise ValueError("the Jefferson rows joined into Edward Duncan's term leave a gap "
                             f"before {t.start_year}-{t.start_month:02d}:\n{rows.to_string()}")
        covered = max(covered, int(t.end_year) * 12 + int(t.end_month))
    if covered != 1932 * 12 + 1:
        raise ValueError(f"Edward Duncan's joined term reaches {(covered - 1) // 12}-"
                         f"{(covered - 1) % 12 + 1:02d}, not 1932-01:\n{rows.to_string()}")
    joined = pd.DataFrame([{
        "name": "Edward Duncan", "district": "Jefferson",
        "start_year": 1908, "start_month": 1, "end_year": 1932, "end_month": 1,
        "seated_by": ELECTION, "source": "; ".join(DUNCAN_SOURCES), "note": DUNCAN_NOTE,
    }])
    return pd.concat([d[~duncan], joined], ignore_index=True)


# The one seat-month in 1912-1931 that nobody held: the Washington seat
# from 1 January 1920, after Clarence R. Ahalt, elected to it, moved from the
# district before the term began, until Frank Upman was appointed on 20
# February. Months are the grain, so the seven weeks count as January alone.
VACANT_1920 = (1920, 1)

# The Board's first month: elected in May 1870, it sat from 1 July
# (arlhist1967officials p.39), so the three seats are empty for six months no
# vacancy accounts for.
BOARD_FROM = (1870, 7)

# Washington's other recorded vacancy, July to November 1873: the May
# election seated nobody, Henry W. Febrey's term ran out with the Board's
# year on 30 June, and Samuel Titus took the seat that December. The
# article's blocks give the same five months (arlhist1967officials p.40).
VACANT_1873 = [("Washington", 1873, month) for month in range(7, 12)]

# Jefferson from April to June 1879: William A. Rowe resigned the seat on 2
# April, having moved into the Arlington District, and it stood empty until
# Travis B. Pinn's term began on 1 July. The months are the article's own
# block, read in members_roster_arlhist.vacated(), which cuts Rowe's term to
# meet them, so the two cannot drift apart.
VACANT_1879 = arlhist.vacancies()

# Jefferson from July to August 1870: the supervisor elected for the township,
# Storm V. Boyd, failed to qualify and never sat, so the seat the roster once
# gave him on O'Leary's election return stands empty until James C. Roach's
# appointment that September. The months are the article's own block, read in
# members_roster_arlhist.unseated().
VACANT_1870 = arlhist.unseated()

# Each recorded vacancy as the district and the first month with no holder,
# counted from year 0. A term ending in one of these ends into the vacancy:
# the seat leaves its holder that month though nobody takes it, so the month
# belongs to no one - the same rule as a term ending in the month its
# successor begins. check_district_seats below and members.held() both apply
# it, and they are the only two places the rule is written.
VACANT_FROM = {(district, year * 12 + month)
               for district, year, month in
               [min(VACANT_1870), min(VACANT_1873), min(VACANT_1879),
                ("Washington",) + VACANT_1920]}


def check_district_seats(d: pd.DataFrame, first=1870, last=arlhist.LAST_YEAR):
    """Each of the three magisterial districts has exactly one member in
    every month from 1870 to 1931, save the months named above: the six
    before the Board sat and the four recorded vacancies.

    The exceptions are the point. A gap that appears anywhere else stops the
    build, and so does filling one of these - a missing supervisor reads like
    a data error, and these five are claims with sources behind them.

    What the earlier coverage rests on differs from 1912-1931's. Before 1912
    the seats run continuously partly because a term with no recorded end is
    held to its statutory four years, not because a source names a man in
    every month, so this checks that the table is internally consistent, not
    that the record is complete. A term's end month belongs to the member
    unless another term in the district begins in it, or the seat stands
    empty instead, and an unrecorded end holds to the end of its first year -
    the three rules members.py applies in held().
    """
    d = d[d.district != "at large"]
    start = d.start_year * 12 + d.start_month
    end = (pd.to_numeric(d.end_year).fillna(d.start_year) * 12
           + pd.to_numeric(d.end_month).fillna(12)).astype(int)
    begins = set(zip(d.district, start)) | VACANT_FROM
    spans = [(dd, lo, hi - 1 if (dd, hi) in begins else hi, n)
             for dd, lo, hi, n in zip(d.district, start, end, d.name)]
    for year in range(first, last + 1):
        for month in range(1, 13):
            m = year * 12 + month
            for district in sorted(set(d.district)):
                held = [n for dd, lo, hi, n in spans if dd == district and lo <= m <= hi]
                empty = ((year, month) < BOARD_FROM
                         or (district, year, month) == ("Washington",) + VACANT_1920
                         or (district, year, month) in VACANT_1873
                         or (district, year, month) in VACANT_1879
                         or (district, year, month) in VACANT_1870)
                expected = 0 if empty else 1
                if len(held) != expected:
                    raise ValueError(
                        f"{year}-{month:02d} {district}: {len(held)} members hold the "
                        f"seat, expected {expected}: {held}")


# Ten mid-term handovers O'Leary and the article both record without saying
# how; the press this settles for, keyed on the roster's name, district and
# the term's start year and month: how the term began, the citekey the
# finding adds (or "" where the article's own prose already carries it), and
# why. docs/members.md.
SEATED_BY_FOUND = {
    ("James C. Roach", "Jefferson", 1870, 9): (APPOINTMENT, "",
        "The article's own block for this term reads \"James C. Roach, "
        "Jefferson Township (Appointed)\" -- its own word for how the seat "
        "was filled, which O'Leary's bare \"replaced by\" does not carry "
        "(Sally, 5 October 2026)."),
    ("H. Dwight Smith", "Arlington", 1872, 12): (APPOINTMENT, "gazette1872smithappointed",
        "The Alexandria Gazette's County Court report of 5 December 1872: "
        "\"The resignation of John Syphax, colored, as Supervisor of "
        "Arlington Township, was accepted, and H. D. Smith appointed to fill "
        "the vacancy\" (Sally, 5 October 2026)."),
    ("Lott W. Crocker", "Arlington", 1873, 3): (APPOINTMENT, "gazette1873crockerappointed",
        "The Alexandria Gazette's County Court report of 3 March 1873: "
        "\"W. J. Douglas was appointed Clerk of Arlington township, and "
        "L. W. Crocker Supervisor of same township, vice H. D. Smith, "
        "resigned\" (Sally, 5 October 2026)."),
    ("Francis G. Schutt", "Arlington", 1873, 4): (APPOINTMENT, "gazette1873schuttqualified",
        "The Alexandria Gazette's County Court report of 8 April 1873: "
        "\"F. G. Schutt qualified as Supervisor of Arlington Township, vice "
        "G. W. Wibert, who failed to qualify\" -- a different man, elected "
        "to succeed Crocker, who never took the seat, the same pattern as "
        "Storm V. Boyd's in 1870 (Sally, 5 October 2026)."),
    ("William N. Febrey", "Washington", 1892, 7): (APPOINTMENT, "gazette1892febreyappointed",
        "The Alexandria Gazette of 18 July 1892: \"Judge Chichester, of the "
        "County Court, has appointed Mr. W. N. Febrey County Supervisor of "
        "Washington district to fill the vacancy caused by the death of "
        "Walter G. Wilson, colored, deceased\", following the court's notice "
        "of 5 July that an appointment would be made during vacation "
        "(gazette1892wilsondeath) (Sally, 5 October 2026)."),
    ("W. C. Wibirt", "Arlington", 1912, 1): (ELECTION, "gazette1911districtcandidates",
        "The Alexandria Gazette's preview of the 7 November 1911 election "
        "names W. C. Wilbert and R. Gordon Finney the Arlington district's "
        "two candidates for supervisor; the Gazette's own returns table "
        "prints no district-only supervisor tally (alexandriagazette19111108p2), "
        "so the winner rests on this article naming the field and the "
        "article's own record of who then held the seat (Sally, 5 October "
        "2026)."),
    ("Robert L. Walker", "Washington", 1912, 1): (ELECTION, "gazette1911districtcandidates",
        "The same preview names R. L. Walker, W. N. Febrey and Charles V. "
        "Grunwell the Washington district's three candidates for supervisor; "
        "the Gazette's returns table prints no district-only supervisor "
        "tally (alexandriagazette19111108p2) (Sally, 5 October 2026)."),
    ("Thomas J. DeLashmutt", "Arlington", 1920, 1): (ELECTION, "alexandriagazette19191105p1",
        "The Alexandria Gazette's election returns of 5 November 1919: \"For "
        "supervisor in Arlington district Thomas J. De Lashmutt was elected. "
        "The vote was De Lashmutt, 411; F. C. Hall, 191; J. R. Robinson, 110; "
        "Richard E. Babcock, 34\" (Sally, 5 October 2026)."),
}


def apply_seated_by_found(d: pd.DataFrame) -> pd.DataFrame:
    """`d` with SEATED_BY_FOUND's readings written onto the matching term: how
    it began, the citekey the finding adds, and why. Every key must match
    exactly one roster row, or the reading is keyed to a term that has moved
    and the build stops."""
    d = d.copy()
    for (who, district, year, month), (how, cite, note) in SEATED_BY_FOUND.items():
        hit = ((d.name == who) & (d.district == district)
               & (d.start_year == year) & (d.start_month == month))
        if hit.sum() != 1:
            raise ValueError(f"SEATED_BY_FOUND matches {hit.sum()} roster rows, "
                             f"expected one: {who!r} {district} {year}-{month:02d}")
        d.loc[hit, "seated_by"] = how
        if cite:
            d.loc[hit, "source"] = d.loc[hit, "source"] + f"; {cite}"
        d.loc[hit, "note"] = [" ".join(filter(None, [n, note])) for n in d.loc[hit, "note"]]
    return d


def build() -> pd.DataFrame:
    d = pd.DataFrame(list(oleary.terms()) + list(results.keyed_terms()) + list(novack.terms()))
    # The article settles what a member is called before anything matches on
    # a name, then corrects 1870-1911, then supplies 1912-1931 outright.
    d = arlhist.names(d)
    d = arlhist.notes(d)
    d = arlhist.early(d)
    d = arlhist.terms(d)
    d = apply_duncan_join(d)
    d = results.terms(d)
    # The county's roll last: it moves ends the election records could only
    # guess at, and adds the terms no contest holds.
    roll.check_against_novack(d)
    d, cut = roll.corrections(d)
    d = pd.concat([d, pd.DataFrame(list(roll.terms(d, cut)))], ignore_index=True)
    d = roll.witnessed(d)
    d = roll.overruled(d)
    d = apply_seated_by_found(d)
    check_names(d)
    check_seated_by(d)
    roll.check_empty_is_the_roll(d)
    check_seats(d)
    check_district_seats(d)
    # A blank end is missing, not a float: the columns stay whole numbers.
    d[["end_year", "end_month"]] = d[["end_year", "end_month"]].astype("Int64")
    d = d.sort_values(["name", "start_year", "start_month"]).reset_index(drop=True)
    # Each person's terms numbered from 1, keyed on the full name.
    d["term_number"] = d.groupby(d.name.str.strip()).cumcount() + 1
    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "seated_by", "source", "note"]
    return d[cols].sort_values(["start_year", "start_month", "district", "name"]).reset_index(drop=True)
