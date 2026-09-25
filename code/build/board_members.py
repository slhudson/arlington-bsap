"""Who served on the Board, when, and who they were -> data/clean/board_members.csv

One row per person per term, from board_roster.py, with race and gender
attached per person and party per term, each with its own source and note.

Race and gender: data/transcribed/by_claude/board_demographics.csv, a
source's own words about a named member with a citation; otherwise
`assumed`, a white man. An attributed name must match a roster name
exactly. docs/board.md has the reasoning.

Party, per term, from the first of three sources that speaks:

  1. data/transcribed/by_claude/board_party.csv - reporting, cited and
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
import pandas as pd

import board_roster
import citekeys
import elections
from board_roster import AT_LARGE_FROM
from elections import PARTIES
from paths import TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"

# The county's labels are elections.LABELS; the state's names are mapped here.
STATE_PARTIES = {"Democratic": "Democratic", "Republican": "Republican",
                 "Independent": "independent", "Green": "independent"}


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
    a = pd.read_csv(BY_CLAUDE / "board_party.csv", dtype={"start_year": int}).fillna("")

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
    if t.seated_by == board_roster.SPECIAL_ELECTION or t.start_month != 1:
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


def attributions() -> pd.DataFrame:
    """One row per person from the sourced file: race and gender, each with
    every source and note joined. Two sources disagreeing stops the build."""
    a = pd.read_csv(BY_CLAUDE / "board_demographics.csv").fillna("")

    def fold(rows):
        out = {}
        for field in ("race", "gender"):
            has = rows[rows[field] != ""]
            vals = sorted(set(has[field]))
            if len(vals) > 1:
                raise ValueError(f"{rows.name}: sources disagree on {field}: {vals}")
            out[field] = vals[0] if vals else ""
            out[field + "_source"] = "; ".join(has.source)
            out[field + "_note"] = quoted(has.basis, has.quote)
        return pd.Series(out)

    return a.groupby("name").apply(fold, include_groups=False)


def build() -> pd.DataFrame:
    d = board_roster.build()
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
        row["party"], row["party_source"], row["party_note"] = (
            party_of(t, labels, state, parties) if t.start_year >= AT_LARGE_FROM else ("", "", ""))
        att = a.loc[t["name"]] if t["name"] in a.index else None
        for field, default in (("race", "White"), ("gender", "man")):
            row[field], row[f"{field}_source"], row[f"{field}_note"] = (
                (att[field], att[f"{field}_source"], att[f"{field}_note"])
                if att is not None and att[field] else (default, citekeys.ASSUMED, ""))
        rows.append(row)

    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "seated_by", "source", "note",
            "race", "race_source", "race_note", "gender", "gender_source", "gender_note",
            "party", "party_source", "party_note"]
    return pd.DataFrame(rows)[cols]


if __name__ == "__main__":
    write(build(), "board_members")
