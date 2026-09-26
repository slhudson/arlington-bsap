"""Every claim about a Board member, one row each -> data/built/board_claims.csv

Six files under data/transcribed/by_claude/ stacked into one table, each
cell as keyed in, with `claim` saying which file a row came from:
`demographics` (race, gender or a birth year a source states), `party` (a
term's party, keyed on the term's start year), `residence` (a dated
place), `census` (one record, with what the index prints and what the
sheet gives), `novack` (a member's whole service as Novack prints it, the
`term` string and `notes`) and `terms` (a term keyed in from the county's
candidate history, with its dates and `note`). A field a row does not
carry is blank. Nothing is coded, matched or chosen here;
code/clean/board_roster.py reads the terms, code/clean/board_census.py the
census rows, and code/clean/board_members.py and board_residence.py resolve
the rest. docs/board.md, "Census records", has what each column holds.

Two rows are refused. A census row that does not say what was read against
the image, the sheet or the index; and a place on a census row the sheet
was never read against, since a street is the field the index gets wrong
(docs/board.md, "Reading an image").
"""
import pandas as pd

from paths import BY_CLAUDE, source, write

FILES = {"demographics": BY_CLAUDE / "board_demographics.csv",
         "party": BY_CLAUDE / "board_party.csv",
         "residence": BY_CLAUDE / "board_residence.csv",
         "census": BY_CLAUDE / "board_census.csv",
         "novack": BY_CLAUDE / "arlington_historical_magazine" / "novack_terms_1930-1994.csv",
         "terms": BY_CLAUDE / "board_terms.csv"}

COLUMNS = ["name", "claim", "year", "start_year", "start_month", "end_year", "end_month",
           "district", "seated_by", "term", "race", "gender", "birth_year", "age", "birthplace",
           "occupation", "place", "party", "basis", "checked", "source", "page", "quote",
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


def build() -> pd.DataFrame:
    parts = []
    for claim, path in FILES.items():
        d = source(path, dtype=str).fillna("")
        if claim == "census":
            d = census_records(d)
        parts.append(d.assign(claim=claim))
    return pd.concat(parts, ignore_index=True).reindex(columns=COLUMNS).fillna("")


if __name__ == "__main__":
    write(build(), "board_claims")
