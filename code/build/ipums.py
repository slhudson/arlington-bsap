"""The 1920 full count, by enumeration district and race -> data/built/ipums.csv

One row per enumeration district per race code, with how many people the
extract holds there, and beside it the district's transcribed description
and the magisterial district that description names. From
data/raw/ipums/<year>/*.csv.gz, the extract code/fetch/ipums.py asked for,
and data/transcribed/by_claude/nara/<year>/, the enumeration district
descriptions keyed in from NARA T1224.

    year         the census
    ed           the enumeration district, as the 1920 volumes number it
    district     the magisterial district the description names, blank where
                 it names none
    description  the description as transcribed
    race         the IPUMS race code, as delivered
    people       how many people the extract holds in that district at that code

Counting people is not a decision, and neither is putting a description
beside the district it describes. What blank means - Fort Myer's district
names none - and which magisterial district each enumeration district
belongs to are decided in code/clean/residents_by_district.py.

The join is on `ed`, so an enumeration district in one table and not the
other loses a value, and write() refuses the step: the extract and the
descriptions have to be about the same six districts.
"""
import pandas as pd

from paths import BY_CLAUDE, RAW, source, write

EXTRACTS = sorted((RAW / "ipums").glob("*/*.csv.gz"))
DESCRIPTIONS = sorted((BY_CLAUDE / "nara").glob("*/*_enumeration_districts.csv"))

# IPUMS builds ENUMDIST as the county code and the district's own number; the
# last two digits are the number the census printed, 10 to 15 in 1920.
ED_DIGITS = 2


def people(path) -> pd.DataFrame:
    """One extract as counts by enumeration district and race code."""
    d = source(path, dtype=str, keep_default_na=False)
    d = d.assign(ed=d.ENUMDIST.str[-ED_DIGITS:])
    return (d.groupby(["YEAR", "ed", "RACE"]).size().rename("people").reset_index()
            .rename(columns={"YEAR": "year", "RACE": "race"}))


def descriptions(path) -> pd.DataFrame:
    """One year's enumeration district descriptions, the year from its folder."""
    d = source(path, dtype=str, keep_default_na=False)
    return d.assign(year=path.parent.name)


def build() -> pd.DataFrame:
    counts = pd.concat([people(p) for p in EXTRACTS], ignore_index=True)
    described = pd.concat([descriptions(p) for p in DESCRIPTIONS], ignore_index=True)
    d = counts.merge(described, on=["year", "ed"], how="outer", validate="many_to_one")
    return d[["year", "ed", "district", "description", "race", "people"]].sort_values(
        ["year", "ed", "race"], ignore_index=True)


if __name__ == "__main__":
    write(build(), "ipums")
