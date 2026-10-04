"""Men of voting age by race by magisterial district, 1880-1920 -> data/clean/residents_by_district_adults.csv

One row per census per district, and the county where all three districts
are counted: the men aged 21 and over in the full-count schedules, in the
columns `men_white`, `men_black` and `men_other`, and `men_all`, their sum.
Women are not counted: they could not vote in Virginia before 1920, and the
figures that read this table stop at 1919. Twenty-one is the voting age
throughout.

The counts are the schedules the district race table already reads, placed
in a magisterial district by the same reading of each enumeration district
(`residents_by_district.placed`, with its ED_READ_BY_HAND), so the two tables
cannot place a person differently. Each district's head count here is
checked against the one `residents_by_district.csv` writes, to the person.

Two readings are decided here:

- A man of any race code but 1 (white) and 2 (Black) is `men_other`, as in
  residents_by_district: code 3 is American Indian, and any other code
  stops the step.
- Arlington district in 1900 is written, and is short: the 1900 database
  holds 2,701 of the 3,200 people the volume prints for it, so its men are a
  floor on the district's. A rate with this count beneath it is an upper
  bound. The county is not written for 1900, because two districts and a
  short third are not a county (residents_by_district.INCOMPLETE).

docs/residents.md, "Men of voting age".
"""
import pandas as pd

import citekeys
import residents_by_district as rbd
from paths import read, write

ADULT = 21
MALE = "1"
COUNTY = "county"
COLUMNS = ["men_white", "men_black", "men_other"]


def men(year) -> pd.DataFrame:
    """The year's men of voting age per magisterial district per race
    column, with the district's whole head count beside them, every
    district present."""
    d, named = rbd.placed(year)
    d = d.assign(district=named, sex=d.sex.astype(str))
    code = d.race.astype(str)
    if not set(code) <= set(rbd.RACE_CODES):
        raise AssertionError(f"{year}: race code(s) {sorted(set(code) - set(rbd.RACE_CODES))} "
                             f"are not in RACE_CODES, so their men would be counted in no column")
    adult = d[(d.sex == MALE) & (d.age >= ADULT)]
    wide = (adult.assign(column=code[adult.index].map(rbd.RACE_CODES))
            .pivot_table(index="district", columns="column", values="people",
                         aggfunc="sum", fill_value=0)
            .reindex(index=list(rbd.DISTRICTS), columns=["white", "black", "other"], fill_value=0))
    wide.columns = COLUMNS
    wide["head_count"] = d.groupby("district").people.sum()
    return wide


def build() -> pd.DataFrame:
    parts = []
    for year in rbd.FROM_THE_SCHEDULES:
        m = men(year)
        m["men_all"] = m[COLUMNS].sum(axis=1)
        m["year"] = year
        parts.append(m.rename_axis("district").reset_index())
    d = pd.concat(parts, ignore_index=True)

    # The same people, placed the same way: a district's schedules head count
    # is residents_by_district's, wherever that table writes one.
    them = read("residents_by_district").set_index(["year", "district"])
    counted = them[["white", "black", "other"]].sum(axis=1, min_count=1)
    for r in d.itertuples():
        theirs = counted.get((r.year, r.district))
        if pd.notna(theirs) and theirs != r.head_count:
            raise AssertionError(
                f"{r.year} {r.district}: {r.head_count:,} people here, {theirs:,.0f} in "
                f"residents_by_district.csv; the two tables place enumeration districts differently")
        if not 0.2 < r.men_all / r.head_count < 0.45:
            raise AssertionError(
                f"{r.year} {r.district}: {r.men_all:,} men of voting age among "
                f"{r.head_count:,} people is not a plausible share; check the age and sex columns")

    # A county is three districts added up, so only where all three are whole.
    whole = d[~d.apply(lambda r: r.district in rbd.INCOMPLETE.get(r.year, ()), axis=1)]
    whole = whole.groupby("year").filter(lambda g: len(g) == len(rbd.DISTRICTS))
    county = (whole.groupby("year")[COLUMNS + ["men_all"]].sum()
              .assign(district=COUNTY).reset_index())
    d = pd.concat([d, county], ignore_index=True)

    d["source"] = d.year.map(citekeys.race_source)
    d = d[["year", "district", *COLUMNS, "men_all", "source"]]
    d["district"] = pd.Categorical(d.district, [*rbd.DISTRICTS, COUNTY])
    d = d.sort_values(["year", "district"], ignore_index=True)
    d["district"] = d.district.astype(str)
    assert (d.men_all == d[COLUMNS].sum(axis=1)).all(), "men_all is not the sum of its races"
    return d


if __name__ == "__main__":
    write(build(), "residents_by_district_adults")
