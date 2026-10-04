"""The full counts, by enumeration district, sex, race and age -> data/built/ipums.csv

One row per enumeration district per sex code per race code per age, with how many people the
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
    sex          the IPUMS sex code, as delivered (1 male, 2 female)
    race         the IPUMS race code, as delivered
    age          the IPUMS age in years, as delivered
    people       how many people the extract holds in that district at that sex, race and age

Counting people is not a decision, and neither is putting a description
beside the district it describes. What blank means - Fort Myer's district
names none - and which magisterial district each enumeration district
belongs to are decided in code/clean/residents_by_district.py; which ages
count as adults, in code/clean/residents_by_district_adults.py.

The join is on `ed`, so an enumeration district in one table and not the
other loses a value, and write() refuses the step: the extract and the
descriptions have to be about the same six districts.
"""
import pandas as pd

from paths import BY_CLAUDE, RAW, source, write

EXTRACTS = sorted((RAW / "ipums").glob("*/*.csv.gz"))
DESCRIPTIONS = sorted((BY_CLAUDE / "nara").glob("*/*_enumeration_districts.csv"))

# IPUMS builds ENUMDIST as the county's code followed by the district's own
# number in five digits, so the number the census printed is what is left of
# it below 100,000: 13000010 is district 10.
ED_IN = 100_000


def people(path) -> pd.DataFrame:
    """One extract as counts by enumeration district, sex, race code and age."""
    d = source(path, dtype=str, keep_default_na=False)
    d = d.assign(ed=(d.ENUMDIST.astype(int) % ED_IN).astype(str))
    return (d.groupby(["YEAR", "ed", "SEX", "RACE", "AGE"]).size().rename("people").reset_index()
            .rename(columns={"YEAR": "year", "SEX": "sex", "RACE": "race", "AGE": "age"}))


def descriptions(path) -> pd.DataFrame:
    """One year's enumeration district descriptions, the year from its folder."""
    d = source(path, dtype=str, keep_default_na=False)
    return d.assign(year=path.parent.name)


def build() -> pd.DataFrame:
    counts = pd.concat([people(p) for p in EXTRACTS], ignore_index=True)
    described = pd.concat([descriptions(p) for p in DESCRIPTIONS], ignore_index=True)
    d = counts.merge(described, on=["year", "ed"], how="outer", validate="many_to_one")
    return d[["year", "ed", "district", "description", "sex", "race", "age", "people"]].sort_values(
        ["year", "ed", "sex", "race", "age"], ignore_index=True)


if __name__ == "__main__":
    write(build(), "ipums")
