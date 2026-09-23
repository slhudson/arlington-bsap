"""Who served on the Board, when, and who they were -> data/clean/board_members.csv

One row per person per term, 1870 through 2026. The terms come from
board_roster.py (O'Leary, Novack, and election results, in sequence). Race
and gender are attached here, each with its own source and note, from the
first of three places that has something to say:

  1. data/transcribed/by_claude/board_demographics.csv - a source's own
     words about a named member, with a citation. The note carries the
     basis and the quotation.
  2. Alex Keena's member workbook, 1932-2026, cited as citekeys.KEENA.
  3. Nothing, in which case the source reads citekeys.ASSUMED and the member is
     taken to be a white man. Only 1870-1931 falls through to this.

Every attributed name must match a roster name exactly - a near-miss would
fall silently into the workbook or the default - and every roster member
from 1932 must match exactly one person in the workbook. The build refuses
anything else rather than guess.
"""
import pandas as pd

import board_roster
import citekeys
from paths import BOARD_MEMBERS_XLSX, TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"


def workbook() -> pd.DataFrame:
    """Alex's member database, one row per member per year, as delivered."""
    r = pd.read_excel(BOARD_MEMBERS_XLSX)
    r.columns = [c.strip().lower().replace("/", "_") for c in r.columns]

    # A person should appear once per year. Alfred Frisbie has three rows for
    # 1952 - the coding agrees across them, so nothing is miscoded, but any
    # tally built from this file would count him three times. Recorded rather
    # than silently deduplicated: by_human/ is not edited here.
    key = ["year", "last_name", "first_name"]
    dup = r[r.duplicated(key, keep=False)]
    known = {(1952, "Frisbie", "Alfred")}
    found = {tuple(v) for v in dup[key].drop_duplicates().values}
    unexpected = found - known
    assert not unexpected, f"new duplicate person-years: {sorted(unexpected)}"
    for k, grp in dup.groupby(key):
        for c in ["woman", "white", "black", "hispanic_latino"]:
            assert grp[c].nunique() <= 1, f"{k} duplicate rows disagree on {c}"
    return r


def workbook_coding(r: pd.DataFrame) -> pd.DataFrame:
    """One row per person in the workbook: surname, years served, race, gender."""
    flags = ["woman", "white", "black", "hispanic_latino"]
    per = r.groupby(["last_name", "first_name"]).agg(
        first=("year", "min"), last=("year", "max"),
        **{f: (f, "nunique") for f in flags}, **{f + "_v": (f, "first") for f in flags})
    varying = per[[f for f in flags]].gt(1).any(axis=1)
    if varying.any():
        raise ValueError(f"workbook codes a person two ways: {list(per.index[varying])}")
    per["race"] = per.apply(
        lambda p: "Black" if p.black_v else "Hispanic" if p.hispanic_latino_v else "White", axis=1)
    per["gender"] = per.woman_v.map({1: "woman", 0: "man"})
    per = per.reset_index()
    per["surname"] = per.last_name.map(board_roster.surname)   # "de Ferranti" -> "ferranti", as the roster does
    return per[["surname", "first_name", "first", "last", "race", "gender"]]


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
    k = workbook_coding(workbook())

    rows = []
    for _, t in d.iterrows():
        row = dict(t)
        att = a.loc[t["name"]] if t["name"] in a.index else None
        wb = None
        if t.start_year >= 1932:
            sn = board_roster.surname(t["name"])
            end = t.end_year if pd.notna(t.end_year) else t.start_year
            # The workbook and Novack disagree by a year on some term
            # boundaries (1939, 1963 - see docs/sources.md), so a year of
            # slack is allowed on the overlap.
            hits = k[(k.surname == sn) & (k["first"] <= end + 1) & (k["last"] >= t.start_year - 1)]
            # The workbook spells a few people two ways ("Kenneth" and
            # "Kenneth M." Haggerty). Several matches are fine if they are
            # coded the same; none, or a disagreement, stops the build.
            if hits.empty or hits[["race", "gender"]].drop_duplicates().shape[0] > 1:
                raise ValueError(f"{t['name']} ({t.start_year}-{end}): "
                                 f"{len(hits)} workbook matches\n{hits}")
            wb = hits.iloc[0]
        for field, default in (("race", "White"), ("gender", "man")):
            if att is not None and att[field]:
                row[field], row[field + "_source"], row[field + "_note"] = (
                    att[field], att[field + "_source"], att[field + "_note"])
            elif wb is not None:
                row[field], row[field + "_source"], row[field + "_note"] = (
                    wb[field], citekeys.KEENA, "")
            else:
                row[field], row[field + "_source"], row[field + "_note"] = (default, citekeys.ASSUMED, "")
        rows.append(row)

    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "source", "note",
            "race", "race_source", "race_note", "gender", "gender_source", "gender_note"]
    return pd.DataFrame(rows)[cols]


if __name__ == "__main__":
    write(build(), "board_members")
