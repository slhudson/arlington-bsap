"""Who served on the Board, when, and who they were -> data/clean/members.csv

One row per person per term, from members_roster.py, with race, gender and
birth year attached per person and party per term, each with its own
source and note, the year of the election that seated each elected term,
and the months the term held: `held_from` and `held_to`, months counted
from year 0, the end exclusive, with the handover month given to the
incoming member and an unrecorded end held to the end of its first year.
Every count of who held a seat when reads those two columns, so the rule
is applied here and nowhere else. docs/members.md, Seat-years.

Race, gender and birth year: data/transcribed/by_claude/members_demographics.csv,
a source's own words about a named member with a citation, and the census
records in members_census.csv through members_census.py; otherwise race and
gender are `assumed`, a white man, and the birth year is blank and
`unsourced`. An attributed name must match a roster name exactly.
docs/members.md has the reasoning.

Party, per term, from the first of three sources that speaks:

  1. data/transcribed/by_claude/members_party.csv - reporting, cited and
     quoted, keyed on the name and the term's start year.
  2. The county's candidate history, which prints a label after a name -
     "(D)", "(ABC)", "(I)" - from 1931, though not on every winner.
  3. The state's elections database, which records party from 2007 and is
     the only source from 2022; where its general-election row carries
     none, a win in that year's Democratic primary stands in.

The county and the state must agree where both name a party, and reporting
may override the county only where it prints "(I)" or nothing. A member
none of the three covers is `unsourced`; before 1932 no party is attempted.
"""
import numpy as np
import pandas as pd

import members_census
import members_roster
import members_terms
import citekeys
import elections
import paths
from members_terms import AT_LARGE_FROM
from elections import PARTIES
from paths import write

# The county's labels are elections.LABELS; the state's names are mapped here.
STATE_PARTIES = {"Democratic": "Democratic", "Republican": "Republican",
                 "Independent": "independent", "Green": "independent"}

# What members_demographics.csv attributes per person, and what a person is
# when no source speaks: race and gender have a standing assumption, a birth
# year has none.
ATTRIBUTED = {"race": "White", "gender": "man", "birth_year": ""}

# How a gender is known, in members.gender_evidence: "record" (a census
# listing), "press" (a pronoun or honorific a paper uses), both joined with
# "; ", or this when no source speaks and the default stands.
NO_EVIDENCE = "none"

# A birth year that puts a member outside this range of ages when first
# seated is a misreading, not a finding.
AGE_WHEN_SEATED = (18, 100)


def claims(kind, columns) -> pd.DataFrame:
    """The rows of one claim file, from data/built/members_claims.csv, in the
    file's own columns."""
    c = paths.built("members_claims")
    return c.loc[c.claim == kind, columns].reset_index(drop=True)


def quoted(basis, quotes) -> str:
    """"basis: quote" per source, joined - the note on an attribution."""
    return " | ".join(f"{b}: {q}" if q else b for b, q in zip(basis, quotes))


def county_labels() -> dict:
    """(surname, election year) -> the labels the county prints for that
    person's County Board rows that year, with their pages."""
    out = {}
    c = elections.contests()
    for _, r in c[c.record == "county"].iterrows():
        entry = out.setdefault((r.surname, int(r.year)), {"labels": set(), "pages": set()})
        entry["labels"] |= elections.labels_on(r.candidate)
        entry["pages"].add(int(r.page))
    return out


def state_parties() -> dict:
    """(surname, election year) -> the party the state records for a County
    Board winner that year, and the contest. The general election is read
    first; where its winner carries no party (2000-2003, 2023 on), a win in
    that year's Democratic primary stands in, and the entry says so."""
    c = elections.contests()
    won = c[(c.record == "state") & c.person & (c.is_winner == True)]  # noqa: E712
    out = {}
    for _, w in won.sort_values("kind", kind="stable").iterrows():     # "General" sorts before "Primary"
        key = (w.surname, int(w.year))
        if w.primary:
            if key not in out and w.primary_party == "Democratic":
                out[key] = {"party": "Democratic", "contest": int(w.contest),
                            "note": "won the Democratic primary; the general election "
                                    "record carries no party"}
        elif w.party in STATE_PARTIES:
            out[key] = {"party": STATE_PARTIES[w.party], "contest": int(w.contest), "note": ""}
    return out


def party_attributions() -> pd.DataFrame:
    """One row per (name, term start year) from the sourced file. Two sources
    disagreeing stops the build."""
    a = claims("party", ["name", "start_year", "party_words", "basis", "source", "quote"])
    a["party"] = decode(a.party_words, PARTY_WORDS, "party")
    a["start_year"] = a.start_year.astype(int)

    def fold(rows):
        vals = sorted(set(rows.party))
        if len(vals) > 1:
            raise ValueError(f"{rows.name}: sources disagree on party: {vals}")
        return pd.Series({"party": vals[0], "source": "; ".join(rows.source),
                          "note": quoted(rows.basis, rows.quote)})

    return a.groupby(["name", "start_year"]).apply(fold, include_groups=False)


def election_year(t) -> int:
    """The election that seated a term: a January start follows a November
    election; a special election or an appointment seats at once."""
    if t.seated_by == members_terms.SPECIAL_ELECTION or t.start_month != 1:
        return int(t.start_year)
    return int(t.start_year) - 1


def party_of(t, labels, state, att):
    """(party, source, note) for one term, from the first source that speaks."""
    key = (elections.surname(t["name"]), election_year(t))
    county = labels.get(key, {"labels": set(), "pages": set()})
    printed = sorted(county["labels"])
    if len(printed) > 1:
        raise ValueError(f"{t['name']} {key[1]}: the county prints more than one label: {printed}")
    label = printed[0] if printed else None
    # A label no winner has carried.
    if label is not None and elections.LABELS.get(label, "other") == "other":
        raise ValueError(f"{t['name']} {key[1]}: party label ({label}) is not one this build "
                         f"knows for a winner. Add it to elections.LABELS with what it "
                         f"records, or fix the reading.")
    county_party = elections.LABELS[label] if label else ""
    county_cite = f"{citekeys.ARLINGTON_ELECTIONS} p.{min(county['pages'])}" if county["pages"] else ""
    listed = f"county lists ({label})" if label else ""
    s = state.get(key)

    if s and county_party in PARTIES and s["party"] != county_party:
        raise ValueError(f"{t['name']} {key[1]}: county lists ({label}) but the state "
                         f"records {s['party']} in contest {s['contest']}")

    a = att.loc[(t["name"], t.start_year)] if (t["name"], t.start_year) in att.index else None
    if a is not None:
        if county_party in PARTIES - {"independent"} and county_party != a.party:
            raise ValueError(f"{t['name']} {t.start_year}: county lists ({label}) but "
                             f"{a.source} says {a.party}")
        return a.party, a.source, " | ".join(filter(None, [listed, a.note]))
    if county_party:
        return county_party, county_cite, listed if label not in ("D", "R", "I", "ABC") else ""
    if s:
        return s["party"], f"{citekeys.VA_ELECTIONS} contest {s['contest']}", s["note"]
    if label:                                  # "Convention"
        return "", county_cite, f"{listed}: nominated by a convention the source does not name"
    return "", citekeys.UNSOURCED, ""


def held(terms: pd.DataFrame) -> pd.DataFrame:
    """held_from and held_to for every term: months from year 0, the end
    exclusive. An unrecorded end holds to the end of its first year, and a
    term ending in the month another term in the same district begins
    yields that month to the incoming member - or, where the seat stood
    empty instead, to nobody (members_roster.VACANT_FROM)."""
    end_year = pd.to_numeric(terms.end_year).fillna(terms.start_year)
    end_month = pd.to_numeric(terms.end_month).fillna(12)
    start = terms.start_year * 12 + terms.start_month - 1
    stop = end_year * 12 + end_month
    starts = terms.assign(start=start).groupby("district").start.apply(set).to_dict()
    for district, month in members_roster.VACANT_FROM:
        starts.setdefault(district, set()).add(month - 1)
    stop = [s - 1 if (s - 1) in starts.get(d, set()) else s for d, s in zip(terms.district, stop)]
    return pd.DataFrame({"held_from": start.astype(int), "held_to": pd.Series(stop, index=terms.index).astype(int)})


# What the words a source uses mean. members_demographics.csv and
# members_party.csv keep the words as printed (`race_words`, `gender_words`,
# `party_words`); the category is decided here, in the open. A word this does
# not list stops the build.
GENDER_WORDS = {"he": "man", "his": "man", "him": "man", "mr.": "man",
                "captain": "man",
                "she": "woman", "her": "woman", "mrs.": "woman", "ms.": "woman"}
RACE_WORDS = {
    "black": "Black", "african american": "Black", "african americans": "Black",
    # The word the 1875 Alexandria Gazette prints beside a member's name.
    "colored": "Black",
    "black community": "Black", "black people i know, i among them": "Black",
    # As the census's Mulatto is coded (members_census.py).
    "mixed race": "Black",
    "latin american heritage": "Hispanic",
    # A description that implies a race the source does not state: a
    # Confederate soldier of the period was White; breaking the all-white
    # pattern was the first Black member.
    "former confederate soldier": "White",
    "all-white pattern": "Black",
    # A count of the members of color, not a claim about the named member;
    # the person's own rows carry the race.
    "3 black men, one hispanic man": "",
}
# A party is what the source calls the member, except that an independent
# with the formal backing of a party's committee is coded to that party
# (the coding rule: Dugan 1947, Vihstadt 2014-15), and where a source calls
# a member independent but another calls him a Democrat, Democratic (Fisher
# 1968, from the 1971 source).
PARTY_WORDS = {
    "independents": "independent",
    "democrat": "Democratic", "democrats": "Democratic",
    "democratic party nominee": "Democratic",
    "republicans": "Republican",
    "candidate of abc": "ABC", "endorsee of abc": "ABC",
    "democratic-leaning independent": "independent",
    "democrat (though nominally an independent)": "Democratic",
    "democrat-cum-independent": "Democratic",
    "independent; endorsed by the republican committee": "Republican",
    "independent; formal backing of the republican committee": "Republican",
    "independent; supported by abc and democrats": "Democratic",
    "independent; backed by abc and the democratic party": "Democratic",
    "democratic incumbent": "Democratic",
    "no opposition in the forthcoming democratic primary": "Democratic",
    "won the democratic nomination": "Democratic",
    "a member of the democratic party": "Democratic",
    "member of the arlington democratic executive committee": "Democratic",
    "a democrat, previously elected to the board on the party ticket": "Democratic",
    "a democrat": "Democratic",
    "independent candidates": "independent",
    "represent the abc political coalition": "ABC",
    # AIM, the Arlington Independent Movement, is coded independent: docs/members.md.
    "candidate of the arlington independent movement (aim)": "independent",
    "nominee of arlington independent movement": "independent",
}


def decode(words: pd.Series, table: dict, what: str) -> pd.Series:
    """A column of words as the category each means, blank for blank. Gender
    words may be several, joined with ", " (`Mr., his`); they must agree."""
    def one(w):
        if w == "":
            return ""
        parts = [p.strip().lower() for p in w.split(", ")] if what == "gender" else [w.lower()]
        missing = [p for p in parts if p not in table]
        found = {table[p] for p in parts if p in table}
        if missing or len(found) != 1:
            raise ValueError(f"{what} words with no single category here: {w!r}; "
                             f"add them to the table in members.py or fix the reading")
        return found.pop()
    return words.map(one)


BORN_BY_AGE = "; the year is the year of the date less the age given, so within a year"

# How exact a birth year is, in members.birth_year_precision: a printed
# birth date or year, or a date less a printed age. docs/members.md.
EXACT = "exact"
WITHIN_A_YEAR = "within a year"


def birth_years_from_ages(a: pd.DataFrame) -> pd.DataFrame:
    """A source that states an age gives the age and the date it was stated
    (`age`, `age_date`, as printed); the birth year is decided here, the
    same way members_census.py does it for a census record. A row gives a
    birth year or an age, and an age needs its date."""
    aged = a.age != ""
    if (aged & (a.birth_year != "")).any():
        raise ValueError("a claim row gives both a birth year and an age:\n"
                         + "\n".join(f"  {n}" for n in a.name[aged & (a.birth_year != "")]))
    years = a.age_date.str.findall(r"\d{4}").str[-1]
    undated = aged & years.isna()
    if undated.any():
        raise ValueError("an age with no year in its date:\n"
                         + "\n".join(f"  {n}: {d!r}" for n, d in zip(a.name[undated], a.age_date[undated])))
    if ((~aged) & (a.age_date != "")).any():
        raise ValueError("a date with no age beside it")
    a = a.copy()
    a.loc[aged, "birth_year"] = (years[aged].astype(int) - a.age[aged].astype(int)).astype(str)
    a.loc[aged, "basis"] = a.basis[aged] + BORN_BY_AGE
    a["birth_year_precision"] = np.where(aged, WITHIN_A_YEAR, np.where(a.birth_year != "", EXACT, ""))
    return a.drop(columns=["age", "age_date"])


def attributions() -> pd.DataFrame:
    """One row per person from the claim file and the census records: race,
    gender and birth year, each with every source and note joined. Two
    sources disagreeing stops the build."""
    a = claims("demographics", ["name", "race_words", "gender_words", "birth_year", "age",
                                "age_date", "basis", "source", "quote"])
    a["race"] = decode(a.race_words, RACE_WORDS, "race")
    a["gender"] = decode(a.gender_words, GENDER_WORDS, "gender")
    a = birth_years_from_ages(a.drop(columns=["race_words", "gender_words"]))
    # Where a gender came from: a row of the claim file is a press reading
    # (the pronoun or honorific a paper uses), a census claim is a record.
    census = members_census.claims()
    a = pd.concat([a.assign(evidence="press"), census.assign(evidence="record")],
                  ignore_index=True).fillna("")

    def fold(rows):
        out = {}
        for field in ATTRIBUTED:
            has = rows[rows[field] != ""]
            vals = sorted(set(has[field]))
            if len(vals) > 1:
                raise ValueError(f"{rows.name}: sources disagree on {field}: {vals}")
            out[field] = vals[0] if vals else ""
            out[field + "_source"] = "; ".join(has.source)
            out[field + "_note"] = quoted(has.basis, has.quote)
            if field == "birth_year":
                out["birth_year_precision"] = (EXACT if (has.birth_year_precision == EXACT).any()
                                               else WITHIN_A_YEAR if len(has) else "")
            if field == "gender":
                out["gender_evidence"] = "; ".join(sorted(set(has.evidence)))
        return pd.Series(out)

    return a.groupby("name").apply(fold, include_groups=False)


def build() -> pd.DataFrame:
    d = members_roster.build()
    a = attributions()
    unknown = sorted(set(a.index) - set(d.name))
    if unknown:
        raise ValueError("attributed names not in the roster (spelling must match exactly):\n"
                         + "\n".join(f"  {n!r}" for n in unknown))
    labels, state, parties = county_labels(), state_parties(), party_attributions()
    stray = sorted(set(parties.index) - set(zip(d.name, d.start_year)))
    if stray:
        raise ValueError("party attributions that match no term (name and start year "
                         "must match exactly):\n" + "\n".join(f"  {n!r} {y}" for n, y in stray))

    rows = []
    for _, t in d.iterrows():
        row = dict(t)
        row["election_year"] = (election_year(t) if t.seated_by in
                                (members_terms.ELECTION, members_terms.SPECIAL_ELECTION) else "")
        row["party"], row["party_source"], row["party_note"] = (
            party_of(t, labels, state, parties) if t.start_year >= AT_LARGE_FROM else ("", "", ""))
        att = a.loc[t["name"]] if t["name"] in a.index else None
        for field, default in ATTRIBUTED.items():
            row[field], row[f"{field}_source"], row[f"{field}_note"] = (
                (att[field], att[f"{field}_source"], att[f"{field}_note"])
                if att is not None and att[field]
                else (default, citekeys.ASSUMED if default else citekeys.UNSOURCED, ""))
        row["gender_evidence"] = att["gender_evidence"] if att is not None and att["gender"] else NO_EVIDENCE
        row["birth_year_precision"] = att["birth_year_precision"] if att is not None and att["birth_year"] else ""
        rows.append(row)

    out = pd.DataFrame(rows)
    assert ((out.gender_source == citekeys.ASSUMED) == (out.gender_evidence == NO_EVIDENCE)).all(), \
        "a gender is assumed exactly when no record or press reading backs it"
    out[["held_from", "held_to"]] = held(out)
    check_birth_years(out)
    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "held_from", "held_to", "seated_by", "election_year",
            "source", "note",
            "race", "race_source", "race_note", "gender", "gender_source", "gender_note",
            "gender_evidence",
            "birth_year", "birth_year_source", "birth_year_note", "birth_year_precision",
            "party", "party_source", "party_note"]
    return out[cols]


def check_birth_years(members):
    """A birth year is a four-digit year, and the member's age when first
    seated falls in AGE_WHEN_SEATED."""
    has = members[members.birth_year != ""]
    bad = has[~has.birth_year.str.fullmatch(r"\d{4}")]
    if len(bad):
        raise ValueError("birth_year must be a four-digit year:\n"
                         + "\n".join(f"  {r['name']!r}: {r.birth_year!r}" for _, r in bad.iterrows()))
    first = has.sort_values(["start_year", "start_month"]).groupby("name").first()
    age = first.start_year - first.birth_year.astype(int)
    lo, hi = AGE_WHEN_SEATED
    off = first[(age < lo) | (age > hi)]
    if len(off):
        raise ValueError(f"age when first seated is outside {lo}-{hi}; check the birth year:\n"
                         + "\n".join(f"  {n!r}: born {r.birth_year}, seated {r.start_year}"
                                     for n, r in off.iterrows()))


if __name__ == "__main__":
    write(build(), "members")
