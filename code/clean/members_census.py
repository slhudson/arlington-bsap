"""What each census record says of a Board member, as claims. A module, not a step.

Reads the census rows of data/built/members_claims.csv, one per record, and
gives members.py race, gender and birth year and members_residence.py
the place, each as a claim row in the shape of the claim files beside it.
docs/members.md, "Census records", has what each column holds and why.
"""
import pandas as pd

import paths

# What the index prints -> the category the build records.
GENDER = {"Male": "man", "Female": "woman"}
RACE = {"White": "White", "Black": "Black", "Mulatto": "Black"}

# What may tie a record to a member besides the name (docs/members.md, "Census
# records"). Several are joined with "; ". A row that states `none` stays in
# the table and feeds nothing; a blank has not been read for a tie and stands
# until it is (census-match-quality in docs/questions.csv).
MATCH = ("district", "occupation", "household", "address", "unique", "none", "")
WEAK = "none"

# Records whose age the sheet misreports, or whose age-derived year disagrees
# with another record with nothing to arbitrate between them, so no birth
# year is read from them. Where a third record gives a printed date instead
# (Febrey), the member still gets a birth year; where it does not (Duncan),
# he gets none. docs/members.md, "Census records", says which record and why.
# A key here that no census row uses would drop nothing and say nothing, so
# records() refuses one.
AGE_MISREPORTED = ("census1910febrey", "census1920febrey", "census1910duncan", "census1920duncan")

# How a birth year was had from the record, added to the basis of its claim.
BIRTH_PRINTED = "; the birth year as the census recorded it"
BIRTH_BY_AGE = "; the year is the census year less the age given, so within a year"


def records() -> pd.DataFrame:
    """The census rows that may be used: a row matched on nothing beyond the
    name stays in the table and gives no claim. Refused if a row prints a
    gender or race the build has no category for, or a match it does not
    list."""
    r = paths.built("members_claims")
    r = r[r.claim == "census"].reset_index(drop=True)
    unknown = r[~r.match.str.split("; ").map(lambda ties: all(x in MATCH for x in ties))]
    if len(unknown):
        raise ValueError("census match with no category here: "
                         + ", ".join(f"{s} {v!r}" for s, v in zip(unknown.source, unknown.match)))
    r = r[r.match != WEAK].reset_index(drop=True)
    missing = [s for s in AGE_MISREPORTED if s not in set(r.source)]
    if missing:
        raise ValueError("AGE_MISREPORTED names a record no census row uses: "
                         + ", ".join(missing))
    for field, codes in (("gender", GENDER), ("race", RACE)):
        unknown = r[(r[field] != "") & ~r[field].isin(list(codes))]
        if len(unknown):
            raise ValueError(f"census {field} with no category here: "
                             + ", ".join(f"{s} {v!r}" for s, v in zip(unknown.source, unknown[field])))
    return r


def claims() -> pd.DataFrame:
    """Race and gender per record, then birth year per record, in the
    columns of members_demographics.csv. The birth year is the one the index
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
                         "birth_year_precision": printed.map({True: "exact", False: "within a year"}),
                         "source": r.source, "quote": r.quote})
    born = born[~r.source.isin(AGE_MISREPORTED)]
    return pd.concat([traits, born], ignore_index=True)


def residences() -> pd.DataFrame:
    """The place per record that has one, in the columns of
    members_residence.csv: the match, then what was checked where the match
    does not already say it. The quote is the sheet where it was read.
    The build stage has already refused a place from a record read only
    in the index (docs/members.md, "Reading an image")."""
    r = records()
    r = r[r.place != ""]
    basis = ["; ".join([b] + [c for c in checked.split("; ") if c not in b])
             for b, checked in zip(r.basis, r.checked)]
    return pd.DataFrame({"name": r.name, "year": r.year, "place": r.place, "basis": basis,
                         "source": r.source, "quote": r.sheet.where(r.sheet != "", r.quote)})
