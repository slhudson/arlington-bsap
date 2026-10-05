"""What each census record says of a Board member, as claims. A module, not a step.

Reads the census rows of data/built/members_claims.csv, one per record, and
gives members.py race, gender and birth year and members_residence.py
the place, each as a claim row in the shape of the claim files beside it.

A census listing names a person, not a Board member, and gives several
traits at once, so each record matched to a member is one row of
data/transcribed/by_claude/members_census.csv and every trait is derived
from that row rather than keyed separately. Its columns:

    name, source  the roster name and the record's citekey, census<year><surname>
    year          the census year
    basis         what ties the record to the member, stated once: the name,
                  the place, and an occupation, a spouse or a house number
                  where one agrees; where the index misreads a name, what it
                  reads
    match         what ties it besides the name, from MATCH below, several
                  joined with "; ": district (the district he sat for),
                  occupation, household (a spouse or child another source
                  names), address (a house or street a newspaper also
                  prints), unique (the only person of the name in the
                  county's index that year), or none. Blank where no one has
                  yet read the record for a tie
    checked       what was read against the image: "read against the sheet,
                  which agrees", or what the sheet gives where it differs
                  from the index (the sources skill, "Reading an image")
    gender, race, age, birthplace, occupation
                  as the index prints them: Male, Mulatto, 39
    birth_year    a birth year the index prints as a date, not its "abt"
                  estimate from the age (the 1900 schedule records a month
                  and year); blank otherwise
    place         the street and house number as read for residence, from
                  the sheet where the sheet was read; blank where no one has
                  read it for that purpose
    quote         the index listing verbatim
    sheet         the sheet's lines verbatim, where they were read

A name alone with nothing else in agreement is no match. A row whose match
is `none` stays in the table, so the search and the reading are on record,
and gives the member nothing, so his traits fall to the default or to his
other sources (Sally). Male is a man, Female a woman, White White, and both
Black and Mulatto Black, as Hjerpe codes Pinn's 1880 record; a printed value
with no code here stops the build, since a dropped claim would fall silently
into the default. The birth year is the one the index prints as a date, or
else the census year less the age, and the claim's basis says which. The
place joins the claims of members_residence.csv in
data/clean/members_residence.csv, none chosen over another.
"""
import pandas as pd

import paths

# What the index prints -> the category the build records.
GENDER = {"Male": "man", "Female": "woman"}
RACE = {"White": "White", "Black": "Black", "Mulatto": "Black"}

# What may tie a record to a member besides the name (the docstring above).
# Several are joined with "; ". A row that states `none` stays in
# the table and feeds nothing; a blank has not been read for a tie and stands
# until it is (census-match-quality in docs/questions.csv).
MATCH = ("district", "occupation", "household", "address", "unique", "none", "")
WEAK = "none"

# Records whose age the sheet misreports, or whose age-derived year disagrees
# with another record with nothing to arbitrate between them, so no birth
# year is read from them. Where a third record gives a printed date instead
# (Febrey), the member still gets a birth year; where it does not (Duncan),
# he gets none. Each record's own row says why in its `checked` and `basis`.
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
    in the index (the sources skill, "Reading an image")."""
    r = records()
    r = r[r.place != ""]
    basis = ["; ".join([b] + [c for c in checked.split("; ") if c not in b])
             for b, checked in zip(r.basis, r.checked)]
    return pd.DataFrame({"name": r.name, "year": r.year, "place": r.place, "basis": basis,
                         "source": r.source, "quote": r.sheet.where(r.sheet != "", r.quote)})
