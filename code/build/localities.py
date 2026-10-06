"""Virginia's other governing bodies beside Arlington's -> data/built/localities.csv

One row per locality whose governing body is keyed in: the 38 independent
cities from the Richmond Charter Review Commission's Appendix D, and the
counties in transcribed/by_claude/county_boards.csv. Each carries its 2020
census population and its land area, joined on the locality's name.

    locality          the name, without "city" or "County"
    kind              city or county
    council_members   cities: the council members the appendix counts
    mayor             cities: elected at large, or one of the members
    mayor_on_council  cities: "no" where the appendix says so, else blank
    members           counties: the board's members
    members_source    the citekey behind the count, and members_note
    residents         the 2020 census total, and residents_source
    land_sq_mi        land area in square miles, and land_source

Nothing is added up or chosen here: code/clean/localities.py decides what
a city's council counts as.
"""
import zipfile

import pandas as pd

import citekeys
from paths import BY_CLAUDE, RAW, source, write

CITIES = BY_CLAUDE / "city_of_richmond" / "city_councils.csv"
COUNTIES = BY_CLAUDE / "county_boards.csv"
POPULATION = RAW / "us_census_bureau" / "2020" / "censusapi_dec_pl_P1_race_virginia_counties.csv.gz"
GAZETTEER = RAW / "us_census_bureau" / "2020" / "gazetteer_counties_national.zip"


def gazetteer() -> pd.DataFrame:
    """Virginia's rows of the national counties file, which is one
    tab-separated text file inside the zip as published."""
    with zipfile.ZipFile(GAZETTEER) as z:
        (inner,) = z.namelist()
        with z.open(inner) as f:
            g = pd.read_csv(f, sep="\t", dtype=str)
    g.columns = g.columns.str.strip()
    return g[g["USPS"] == "VA"]


def build() -> pd.DataFrame:
    cities = source(CITIES, dtype=str, keep_default_na=False)
    counties = source(COUNTIES, dtype=str, keep_default_na=False)
    census = source(POPULATION, dtype=str)
    land = gazetteer()

    rows = pd.concat([
        pd.DataFrame({"locality": cities["city"], "kind": "city",
                      "council_members": cities["council_members"], "mayor": cities["mayor"],
                      "mayor_on_council": cities["mayor_on_council"], "members": "",
                      "members_source": cities["source"], "members_note": ""}),
        pd.DataFrame({"locality": counties["county"], "kind": "county",
                      "council_members": "", "mayor": "", "mayor_on_council": "",
                      "members": counties["members"], "members_source": counties["source"],
                      "members_note": counties["note"]}),
    ], ignore_index=True)

    suffix = rows["kind"].map({"city": " city", "county": " County"})
    population = dict(zip(census["NAME"], census["P1_001N"]))
    area = dict(zip(land["NAME"].str.strip(), land["ALAND_SQMI"].str.strip()))
    rows["residents"] = (rows["locality"] + suffix + ", Virginia").map(population)
    rows["residents_source"] = citekeys.CENSUS_DATA_FILE
    rows["land_sq_mi"] = (rows["locality"] + suffix).map(area)
    rows["land_source"] = citekeys.CENSUS_GAZETTEER_2020

    missing = rows[rows["residents"].isna() | rows["land_sq_mi"].isna()]
    if len(missing):
        raise AssertionError("no census population or land area under these names: "
                             + ", ".join(missing["locality"] + " (" + missing["kind"] + ")"))
    return rows


if __name__ == "__main__":
    write(build(), "localities")
