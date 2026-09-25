"""What each census record says of a Board member, as claims. A module, not a step.

Reads data/transcribed/by_claude/board_census.csv, one row per record, and
gives board_members.py race, gender and birth year and board_residence.py
the place, each as a claim row in the shape of the claim files beside it.
docs/board.md, "Census records", has what each column holds and why.
"""
import pandas as pd

from paths import BY_CLAUDE

CENSUS = BY_CLAUDE / "board_census.csv"

# What the index prints -> the category the build records.
GENDER = {"Male": "man", "Female": "woman"}
RACE = {"White": "White", "Black": "Black", "Mulatto": "Black"}

# How a birth year was had from the record, added to the basis of its claim.
BIRTH_PRINTED = "; the birth year as the census recorded it"
BIRTH_BY_AGE = "; the year is the census year less the age given, so within a year"


def records() -> pd.DataFrame:
    """The table, refused if a row does not say what was read against the
    image, or prints a gender or race the build has no category for."""
    r = pd.read_csv(CENSUS, dtype=str).fillna("")
    unchecked = r[~r.checked.str.contains("sheet|index")]
    if len(unchecked):
        raise ValueError("census rows that do not name what was checked (the sheet or the index):\n"
                         + "\n".join(f"  {n} {s}: {c!r}" for n, s, c
                                     in zip(unchecked.name, unchecked.source, unchecked.checked)))
    for field, codes in (("gender", GENDER), ("race", RACE)):
        unknown = r[(r[field] != "") & ~r[field].isin(list(codes))]
        if len(unknown):
            raise ValueError(f"census {field} with no category here: "
                             + ", ".join(f"{s} {v!r}" for s, v in zip(unknown.source, unknown[field])))
    return r


def claims() -> pd.DataFrame:
    """Race and gender per record, then birth year per record, in the
    columns of board_demographics.csv. The birth year is the one the index
    prints as a date, or else the census year less the age, and its basis
    says which."""
    r = records()
    blank = pd.Series("", index=r.index)
    traits = pd.DataFrame({"name": r.name, "race": r.race.map(RACE).fillna(""),
                           "gender": r.gender.map(GENDER).fillna(""), "birth_year": blank,
                           "basis": r.basis, "source": r.source, "quote": r.quote})
    printed = r.birth_year != ""
    by_age = (r.year.astype(int) - pd.to_numeric(r.age)).astype("Int64").astype(str)
    born = pd.DataFrame({"name": r.name, "race": blank, "gender": blank,
                         "birth_year": r.birth_year.where(printed, by_age).replace("<NA>", ""),
                         "basis": r.basis + printed.map({True: BIRTH_PRINTED, False: BIRTH_BY_AGE}),
                         "source": r.source, "quote": r.quote})
    return pd.concat([traits, born], ignore_index=True)


def residences() -> pd.DataFrame:
    """The place per record that has one, in the columns of
    board_residence.csv: the match, then what was checked where the match
    does not already say it. The quote is the sheet where it was read.

    A place is taken only from a record read against its sheet; docs/board.md,
    "Reading an image", says why the index alone does not carry a street."""
    r = records()
    r = r[r.place != ""]
    unread = r[~r.checked.str.contains("sheet")]
    if len(unread):
        raise ValueError("census places taken from the index without the sheet read:\n"
                         + "\n".join(f"  {n} {s}: {p!r}" for n, s, p
                                     in zip(unread.name, unread.source, unread.place)))
    basis = ["; ".join([b] + [c for c in checked.split("; ") if c not in b])
             for b, checked in zip(r.basis, r.checked)]
    return pd.DataFrame({"name": r.name, "year": r.year, "place": r.place, "basis": basis,
                         "source": r.source, "quote": r.sheet.where(r.sheet != "", r.quote)})
