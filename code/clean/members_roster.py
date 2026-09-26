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
  novack1994       1932-1994  members_roster_novack.py    terms of service, with
                                                        mid-term departures
  election results 1995-      members_roster_results.py   the county's candidate
                                                        history to 2021, the
                                                        state's database from 2022

1912-1931 names almost nobody: O'Leary's last listed election is 1915, and
its winners' four-year terms end in January 1912. The county's candidate
history prints the district races of November 1923 and 1927, keyed in
members_terms.csv and read by members_roster_results.py. What a term is, the
seats that exist, how a term begins, the readers the sources share, is
members_terms.py.
"""
import re

import pandas as pd

import members_roster_novack as novack
import members_roster_oleary as oleary
import members_roster_results as results
from members_terms import PRESENT, SEATED_BY, SPECIAL_ELECTION, UNRECORDED


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


def build() -> pd.DataFrame:
    d = pd.DataFrame(list(oleary.terms()) + list(results.keyed_terms()) + list(novack.terms()))
    d = results.terms(d)
    check_names(d)
    check_seated_by(d)
    check_five_seats(d)
    # A blank end is missing, not a float: the columns stay whole numbers.
    d[["end_year", "end_month"]] = d[["end_year", "end_month"]].astype("Int64")
    d = d.sort_values(["name", "start_year", "start_month"]).reset_index(drop=True)
    # Each person's terms numbered from 1, keyed on the full name.
    d["term_number"] = d.groupby(d.name.str.strip()).cumcount() + 1
    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "seated_by", "source", "note"]
    return d[cols].sort_values(["start_year", "start_month", "district", "name"]).reset_index(drop=True)
