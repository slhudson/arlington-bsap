"""Who served on the Board, when, and who they were -> data/clean/board_members.csv

One row per person per term, 1870 through 2026. The terms come from
board_roster.py (O'Leary, Novack, and election results, in sequence). Race
and gender are attached here, each with its own source and note, from the
first of two places that has something to say:

  1. data/transcribed/by_claude/board_demographics.csv - a source's own
     words about a named member, with a citation. The note carries the
     basis and the quotation.
  2. Nothing, in which case the source reads citekeys.ASSUMED and the member is
     taken to be a white man. docs/board.md says what stands behind that
     default in each period.

Every attributed name must match a roster name exactly - a near-miss would
fall silently into the default - and the build refuses anything else rather
than guess.

**Party** is attached the same way, per term rather than per person, because
a member's label changes between elections (Bozman ran as ABC's candidate
five times and as a Democrat once). What "party" means when it has never
been on the ballot is in docs/board.md. The sources, in order:

  1. data/transcribed/by_claude/board_party.csv - reporting, cited and
     quoted, keyed on the name and the term's start year.
  2. The county's candidate history, which prints a label after a name -
     "(D)", "(ABC)", "(I)" - from 1931, though not on every winner.
  3. The state's elections database, which records party from 2007, and
     from 2022 is the only source; where its general-election row carries
     none, a win in that year's Democratic primary stands in.

Where the county and the state both name a party they must agree, and
reporting may override the county only where the county prints "(I)" or
nothing: a cited claim that a member the county calls a Democrat was a
Republican is a finding, and the build stops on it. A member none of the
three covers is `unsourced`; before 1932 no party is attempted at all.
"""
import pandas as pd

import board_roster
import citekeys
import elections
from board_roster import AT_LARGE_FROM
from elections import PARTIES
from paths import TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"

# The labels the county prints after a name, and what each records, are
# elections.LABELS. The state's party names differ and are mapped here.
STATE_PARTIES = {"Democratic": "Democratic", "Republican": "Republican",
                 "Independent": "independent", "Green": "independent"}


def county_labels() -> dict:
    """(surname, election year) -> the labels the county prints for that
    person's County Board rows that year, with the pages they are on.

    A person's rows in one year may repeat the label (a primary listing and
    the general) or print it on only one of them; a blank is not a label.
    """
    out = {}
    for _, r in elections.county_history().iterrows():
        entry = out.setdefault((r.surname, int(r.year)), {"labels": set(), "pages": set()})
        entry["labels"] |= elections.labels_on(r.candidate)
        entry["pages"].add(int(r.page))
    return out


def state_parties() -> dict:
    """(surname, election year) -> the party the state database records for a
    County Board winner that year, and the contest it comes from.

    The general election is read first. Where its winner carries no party -
    2000-2003, and 2023 on - a win in that year's Democratic primary is the
    record instead, and the entry says so.
    """
    c = elections.state_results()
    won = c[c.person & c.is_winner].groupby(["year", "contest_id", "candidate_name"]).agg(
        party=("candidate_party_name", "first"), kind=("election_type", "first"),
        primary=("primary_party", "first")).reset_index()
    out = {}
    for _, w in won.sort_values("kind").iterrows():     # "General" sorts before "Primary"
        key = (elections.surname(w.candidate_name), int(w.year))
        if w.kind.startswith("Primary"):
            if key not in out and w.primary == "Democratic":
                out[key] = {"party": "Democratic", "contest": int(w.contest_id),
                            "note": "won the Democratic primary; the general election "
                                    "record carries no party"}
        elif w.party in STATE_PARTIES:
            out[key] = {"party": STATE_PARTIES[w.party], "contest": int(w.contest_id), "note": ""}
    return out


def party_attributions() -> pd.DataFrame:
    """One row per (name, term start year) from the sourced file: party, with
    every source and note joined. Two sources disagreeing is a finding, and
    the build stops on it."""
    a = pd.read_csv(BY_CLAUDE / "board_party.csv", dtype={"start_year": int}).fillna("")

    def fold(rows):
        vals = sorted(set(rows.party))
        if len(vals) > 1:
            raise ValueError(f"{rows.name}: sources disagree on party: {vals}")
        return pd.Series({"party": vals[0], "source": "; ".join(rows.source),
                          "note": " | ".join(f"{b}: {q}" if q else b
                                             for b, q in zip(rows.basis, rows.quote))})

    return a.groupby(["name", "start_year"]).apply(fold, include_groups=False)


def election_year(t) -> int:
    """The election that seated a term. A January start follows a November
    election; a special election or an appointment seats its winner at once."""
    if t.seated_by == board_roster.SPECIAL_ELECTION or t.start_month != 1:
        return int(t.start_year)
    return int(t.start_year) - 1


def party_of(t, labels, state, att):
    """(party, source, note) for one term, from the first source that speaks.

    See the module docstring for the order and for which disagreements stop
    the build.
    """
    key = (elections.surname(t["name"]), election_year(t))
    county = labels.get(key, {"labels": set(), "pages": set()})
    printed = sorted(county["labels"])
    if len(printed) > 1:
        raise ValueError(f"{t['name']} {key[1]}: the county prints more than one label: {printed}")
    label = printed[0] if printed else None
    # A label only losers have carried is not a party a winner can be given
    # by default: what "(Ind. Dem.)" records for a member is a decision.
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
    source and note. Two sources for one person are both kept; two sources
    disagreeing is a finding, and the build stops on it."""
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
            out[field + "_note"] = " | ".join(
                f"{b}: {q}" if q else b for b, q in zip(has.basis, has.quote))
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
        if t.start_year >= AT_LARGE_FROM:
            row["party"], row["party_source"], row["party_note"] = party_of(t, labels, state, parties)
        else:
            row["party"], row["party_source"], row["party_note"] = "", "", ""
        att = a.loc[t["name"]] if t["name"] in a.index else None
        for field, default in (("race", "White"), ("gender", "man")):
            if att is not None and att[field]:
                row[field], row[field + "_source"], row[field + "_note"] = (
                    att[field], att[field + "_source"], att[field + "_note"])
            else:
                row[field], row[field + "_source"], row[field + "_note"] = (default, citekeys.ASSUMED, "")
        rows.append(row)

    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "seated_by", "source", "note",
            "race", "race_source", "race_note", "gender", "gender_source", "gender_note",
            "party", "party_source", "party_note"]
    return pd.DataFrame(rows)[cols]


if __name__ == "__main__":
    write(build(), "board_members")
