"""Every claim about a Board member, one row each -> data/built/members_claims.csv

Six files under data/transcribed/by_claude/ stacked into one table, each
cell as keyed in, with `claim` saying which file a row came from:
`demographics` (race, gender or a birth year a source states), `party` (a
term's party, keyed on the term's start year), `residence` (a dated
place), `census` (one record, with what the index prints and what the
sheet gives), `novack` (a member's whole service as Novack prints it, the
`term` string and `notes`) and `terms` (a term keyed in from the county's
candidate history, with its dates and `note`). A field a row does not
carry is blank. Nothing is coded, matched or chosen here;
code/clean/members_roster.py reads the terms, code/clean/members_census.py the
census rows, and code/clean/members.py and members_residence.py resolve
the rest. docs/members.md, "Census records", has what each column holds.

Three rows are refused. A census row that does not say what was read
against the image, the sheet or the index; a place on a census row the
sheet was never read against, since a street is the field the index gets
wrong (docs/members.md, "Reading an image"); and a demographics or residence
row citing a census record, which belongs in the census file, one row per
record, where code/transcribe/members_census.py moves it.
"""
import re

import pandas as pd

import citekeys
from paths import BY_CLAUDE, source, write

FILES = {"demographics": BY_CLAUDE / "members_demographics.csv",
         "party": BY_CLAUDE / "members_party.csv",
         "residence": BY_CLAUDE / "members_residence.csv",
         "census": BY_CLAUDE / "members_census.csv",
         "novack": BY_CLAUDE / "arlington_historical_magazine" / "novack_terms_1930-1994.csv",
         "terms": BY_CLAUDE / "members_terms.csv"}

# A census record's citekey, census<year><surname>, unlike a volume's (census1880).
CENSUS_RECORD = re.compile(r"census\d{4}[a-z]+")

COLUMNS = ["name", "claim", "year", "start_year", "start_month", "election_date", "end_year", "end_month",
           "district", "seated_by", "term", "race", "gender", "race_words", "gender_words", "party_words", "birth_year", "age", "age_date", "birthplace",
           "occupation", "place", "basis", "match", "checked", "source", "page", "quote",
           "sheet", "notes", "note"]


def census_records(r: pd.DataFrame) -> pd.DataFrame:
    """The census file, refused if a row does not name what was read
    against the image, or carries a place without the sheet read."""
    unchecked = r[~r.checked.str.contains("sheet|index")]
    if len(unchecked):
        raise ValueError("census rows that do not name what was checked (the sheet or the index):\n"
                         + "\n".join(f"  {n} {s}: {c!r}" for n, s, c
                                     in zip(unchecked.name, unchecked.source, unchecked.checked)))
    unread = r[(r.place != "") & ~r.checked.str.contains("sheet")]
    if len(unread):
        raise ValueError("census places taken from the index without the sheet read:\n"
                         + "\n".join(f"  {n} {s}: {p!r}" for n, s, p
                                     in zip(unread.name, unread.source, unread.place)))
    return r


def not_census(r: pd.DataFrame, claim) -> pd.DataFrame:
    """A demographics or residence file, refused if a row cites a census
    record: the record is one row of members_census.csv, and each claim is
    derived from it there."""
    stray = r[[bool(CENSUS_RECORD.fullmatch(citekeys.key_of(s))) for s in r.source]]
    if len(stray):
        raise ValueError(f"{claim} rows citing a census record, which belongs in members_census.csv "
                         f"(code/transcribe/members_census.py moves it):\n"
                         + "\n".join(f"  {n} {s}" for n, s in zip(stray.name, stray.source)))
    return r


def build() -> pd.DataFrame:
    parts = []
    for claim, path in FILES.items():
        d = source(path, dtype=str).fillna("")
        if claim == "census":
            d = census_records(d)
        elif claim in ("demographics", "residence"):
            d = not_census(d, claim)
        parts.append(d.assign(claim=claim))
    return pd.concat(parts, ignore_index=True).reindex(columns=COLUMNS).fillna("")


if __name__ == "__main__":
    write(build(), "members_claims")
