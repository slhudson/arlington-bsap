"""Residents of voting age by sex and race by magisterial district, 1880-1920, and the county's men 1870-1930 -> data/clean/residents_by_district_adults.csv

One row per census per district, and the county where all three districts
are counted: the men and the women aged 21 and over in the full-count
schedules, in the columns `men_white`, `men_black`, `men_other` and
`men_all` (their sum), the same four for `women_`, and `adults_all`, men and
women together. Women could not vote in Virginia before 1920; the table
counts them anyway, and the figure that reads them decides from which
election they enter the denominator. Twenty-one is the voting age
throughout.

1930 is one county row, from the volume that prints the county's men and
women 21 and over (the turnout table's `voting_age_21`): no race and no
district, so those cells are blank. 1870, 1890 and 1900 are county rows of
the same kind, from the volumes that print the county's men 21 and over
(`county_published`): men only, as one number, no race, no district, the
women's cells blank, since the 1870 and 1890 schedules are not in the
extract and the 1900 ones are short. The turnout figure then divides by a
printed or counted number at every census from 1870 to 1930.

The counts are the schedules the district race table already reads, placed
in a magisterial district by the same reading of each enumeration district
(`residents_by_district.placed`, with its ED_READ_BY_HAND), so the two tables
cannot place a person differently. Each district's head count here is
checked against the one `residents_by_district.csv` writes, to the person.

Three readings are decided here:

- A man or woman of any race code but 1 (white) and 2 (Black) is `men_other`, as in
  residents_by_district: code 3 is American Indian, and any other code
  stops the step.
- Arlington district in 1900 is written, and is short: the 1900 database
  holds 2,701 of the 3,200 people the volume prints for it, so its men are a
  floor on the district's. A rate with this count beneath it is an upper
  bound. The county is not written for 1900, because two districts and a
  short third are not a county (residents_by_district.INCOMPLETE).
- Sex is the schedules' code, 1 male and 2 female; any other code stops the
  step, so a person is never counted in neither column silently.
- A county's published men are net of Alexandria city where the volume's
  county row includes it, 1870 and 1890: the city's own line is keyed beside
  it and subtracted here. The 1900 county row is the county alone (the
  bulletin prints the city as a line of its own), so nothing comes off. Each
  net is checked against residents_by_district: the printed all-ages total
  less the city's must be the three districts' population. The men are all
  males 21 and over, as the schedules count them, and not only citizens, which
  1870 also prints for the county and not for the city.

docs/residents.md, "Men of voting age".
"""
import pandas as pd

import census
import citekeys
import residents
import residents_by_district as rbd
from paths import read, write

ADULT = 21
SEXES = {"1": "men", "2": "women"}
COUNTY = "county"
RACES = ["white", "black", "other"]
MEN = [f"men_{r}" for r in RACES]
WOMEN = [f"women_{r}" for r in RACES]
COLUMNS = MEN + WOMEN
TOTALS = ["men_all", "women_all", "adults_all"]
# The keyed files of the volumes that print the county's men 21 and over where
# the schedules cannot be counted: the county's row and, where that row
# includes Alexandria city, the city's own. 1900's county row is the county.
PUBLISHED = {
    1870: ("1870/population-1870a-57_p637_table24_virginia_alexandria.csv",
           "1870/population-1870a-58_p655_table25_virginia_alexandria.csv"),
    1890: ("1890/1890a_v1-18_p786_table79_virginia_alexandria.csv",
           "1890/1890a_v1-18_p823_table80_virginia_alexandria.csv"),
    1900: ("1900/bulletin-102_p4_table11_virginia_alexandria.csv", None),
}
# The county's printed 1930 lines, and the volume that prints them.
VOLUME_1930 = {"men_all": "Males 21 years old and over", "women_all": "Females 21 years old and over"}


def adults(year) -> pd.DataFrame:
    """The year's residents of voting age per magisterial district per sex
    and race column, with the district's whole head count beside them,
    every district present."""
    d, named = rbd.placed(year)
    d = d.assign(district=named, sex=d.sex.astype(str))
    code = d.race.astype(str)
    if not set(code) <= set(rbd.RACE_CODES):
        raise AssertionError(f"{year}: race code(s) {sorted(set(code) - set(rbd.RACE_CODES))} "
                             f"are not in RACE_CODES, so their adults would be counted in no column")
    if not set(d.sex) <= set(SEXES):
        raise AssertionError(f"{year}: sex code(s) {sorted(set(d.sex) - set(SEXES))} are not "
                             f"1 or 2, so those people would be counted in neither column")
    adult = d[d.age >= ADULT]
    column = adult.sex.map(SEXES) + "_" + code[adult.index].map(rbd.RACE_CODES)
    wide = (adult.assign(column=column)
            .pivot_table(index="district", columns="column", values="people",
                         aggfunc="sum", fill_value=0)
            .reindex(index=list(rbd.DISTRICTS), columns=COLUMNS, fill_value=0))
    wide["head_count"] = d.groupby("district").people.sum()
    return wide


def county_1930() -> pd.DataFrame:
    """The volume's printed count of the county's men and women 21 and over."""
    t = residents.volume_table(1930)
    row = {"year": 1930, "district": COUNTY}
    for column, line in VOLUME_1930.items():
        row[column] = int(t.loc[line, "total"])
    row["source"] = "; ".join(t.loc[list(VOLUME_1930.values()), "cite"].unique())
    return pd.DataFrame([row])


def printed_men(line) -> int:
    """The men 21 and over a keyed row prints: its nativity and colour columns
    added, and checked against the total the page prints beside them where it
    prints one; the printed total alone where it prints nothing finer."""
    parts = line[["native_white", "foreign_white", "colored"]]
    printed = line.printed_total
    if parts.isna().all():
        return int(printed)
    men = int(parts.sum())
    if pd.notna(printed) and men != printed:
        raise AssertionError(f"{line.year} {line.source} p.{line.page}: the columns make "
                             f"{men:,} men and the page prints {printed:,.0f}; a cell is misread")
    return men


def county_published(population) -> pd.DataFrame:
    """The county's men 21 and over at the censuses whose schedules this
    table cannot count, from the volumes: one row per census, `men_all` only,
    net of Alexandria city where the volume's county row includes it.
    `population` is the county's population per census in residents_by_district."""
    rows = []
    for year, (county_file, city_file) in PUBLISHED.items():
        county = census.keyed(county_file).iloc[0]
        men, source = printed_men(county), f"{county.source} p.{county.page:.0f}"
        if city_file:
            city = census.keyed(city_file).iloc[0]
            men -= printed_men(city)
            source += f"; {city.source} p.{city.page:.0f}"
            if county.all_ages - city.all_ages != population[year]:
                raise AssertionError(
                    f"{year}: the county's {county.all_ages:,.0f} less the city's {city.all_ages:,.0f} "
                    f"is not the {population[year]:,} residents_by_district holds; the volume's "
                    f"county row does not include the city, or a cell is misread")
        if not 0.2 < men / population[year] < 0.45:
            raise AssertionError(f"{year}: {men:,} men of voting age among {population[year]:,} "
                                 f"people is not a plausible share")
        rows.append({"year": year, "district": COUNTY, "men_all": men, "source": source})
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    parts = []
    for year in rbd.FROM_THE_SCHEDULES:
        m = adults(year)
        m["men_all"] = m[MEN].sum(axis=1)
        m["women_all"] = m[WOMEN].sum(axis=1)
        m["adults_all"] = m.men_all + m.women_all
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
        for who, n in (("men", r.men_all), ("women", r.women_all)):
            if not 0.2 < n / r.head_count < 0.45:
                raise AssertionError(
                    f"{r.year} {r.district}: {n:,} {who} of voting age among "
                    f"{r.head_count:,} people is not a plausible share; check the age and sex columns")

    # A county is three districts added up, so only where all three are whole.
    whole = d[~d.apply(lambda r: r.district in rbd.INCOMPLETE.get(r.year, ()), axis=1)]
    whole = whole.groupby("year").filter(lambda g: len(g) == len(rbd.DISTRICTS))
    county = (whole.groupby("year")[COLUMNS + TOTALS].sum()
              .assign(district=COUNTY).reset_index())
    d = pd.concat([d, county], ignore_index=True)
    d["source"] = d.year.map(citekeys.race_source)
    population = them.groupby("year").total.sum()
    d = pd.concat([d, county_published(population), county_1930()], ignore_index=True)
    d = d[["year", "district", *MEN, "men_all", *WOMEN, "women_all", "adults_all", "source"]]
    d["district"] = pd.Categorical(d.district, [*rbd.DISTRICTS, COUNTY])
    d = d.sort_values(["year", "district"], ignore_index=True)
    d["district"] = d.district.astype(str)
    schedules = d.source.str.startswith(citekeys.IPUMS_FULL_COUNT)
    for total, parts in (("men_all", MEN), ("women_all", WOMEN)):
        assert (d[total][schedules] == d[parts][schedules].sum(axis=1)).all(), \
            f"{total} is not the sum of its races"
    d["adults_all"] = d.men_all + d.women_all
    return d


if __name__ == "__main__":
    write(build(), "residents_by_district_adults")
