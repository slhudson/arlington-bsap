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
from members_terms import ELECTION, PRESENT, SEATED_BY, SPECIAL_ELECTION, UNRECORDED


def check_five_seats(d: pd.DataFrame, first=1995, last=PRESENT):
    """Five members at large in every month; six in a handover month."""
    at_large = d[d.district == "at large"]
    start = at_large.start_year * 12 + at_large.start_month
    end = pd.to_numeric(at_large.end_year) * 12 + pd.to_numeric(at_large.end_month)
    handover = set(start[at_large.seated_by == SPECIAL_ELECTION])
    for m in range(first * 12 + 1, last * 12 + 13):
        n = ((start <= m) & (end >= m)).sum()
        expected = 6 if m in handover else 5
        if n != expected:
            raise ValueError(f"{(m - 1) // 12}-{(m - 1) % 12 + 1:02d}: {n} members "
                             f"at large, expected {expected}")


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
    "(duncan-one-member-or-three)."
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

# The Board's first month: it did not exist before May 1870, so the three
# seats are empty for four months no vacancy accounts for.
BOARD_FROM = (1870, 5)

# Washington's other recorded vacancy, June to November 1873: Samuel Titus
# takes the seat that December.
VACANT_1873 = [("Washington", 1873, month) for month in range(6, 12)]


def check_district_seats(d: pd.DataFrame, first=1870, last=arlhist.LAST_YEAR):
    """Each of the three magisterial districts has exactly one member in
    every month from 1870 to 1931, save the months named above: the four
    before the Board existed and the two recorded vacancies.

    The exceptions are the point. A gap that appears anywhere else stops the
    build, and so does filling one of these - a missing supervisor reads like
    a data error, and these three are claims with sources behind them.

    What the earlier coverage rests on differs from 1912-1931's. Before 1912
    the seats run continuously partly because a term with no recorded end is
    held to its statutory four years, not because a source names a man in
    every month, so this checks that the table is internally consistent, not
    that the record is complete. A term's end month belongs to the member
    unless another term in the district begins in it, and an unrecorded end
    holds to the end of its first year - the two rules members.py applies in
    held().
    """
    d = d[d.district != "at large"]
    start = d.start_year * 12 + d.start_month
    end = (pd.to_numeric(d.end_year).fillna(d.start_year) * 12
           + pd.to_numeric(d.end_month).fillna(12)).astype(int)
    begins = set(zip(d.district, start))
    spans = [(dd, lo, hi - 1 if (dd, hi) in begins else hi, n)
             for dd, lo, hi, n in zip(d.district, start, end, d.name)]
    for year in range(first, last + 1):
        for month in range(1, 13):
            m = year * 12 + month
            for district in sorted(set(d.district)):
                held = [n for dd, lo, hi, n in spans if dd == district and lo <= m <= hi]
                empty = ((year, month) < BOARD_FROM
                         or (district, year, month) == ("Washington",) + VACANT_1920
                         or (district, year, month) in VACANT_1873)
                expected = 0 if empty else 1
                if len(held) != expected:
                    raise ValueError(
                        f"{year}-{month:02d} {district}: {len(held)} members hold the "
                        f"seat, expected {expected}: {held}")


def build() -> pd.DataFrame:
    d = pd.DataFrame(list(oleary.terms()) + list(results.keyed_terms()) + list(novack.terms()))
    d = arlhist.terms(d)
    d = apply_duncan_join(d)
    d = results.terms(d)
    check_names(d)
    check_seated_by(d)
    check_five_seats(d)
    check_district_seats(d)
    # A blank end is missing, not a float: the columns stay whole numbers.
    d[["end_year", "end_month"]] = d[["end_year", "end_month"]].astype("Int64")
    d = d.sort_values(["name", "start_year", "start_month"]).reset_index(drop=True)
    # Each person's terms numbered from 1, keyed on the full name.
    d["term_number"] = d.groupby(d.name.str.strip()).cumcount() + 1
    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "seated_by", "source", "note"]
    return d[cols].sort_values(["start_year", "start_month", "district", "name"]).reset_index(drop=True)
