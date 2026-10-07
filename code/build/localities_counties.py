"""Every U.S. county's 2020 population -> data/built/localities_counties.csv

The Census API's redistricting file for counties, as fetched by
code/fetch/census_counties.py, one row per county or county equivalent: its
full name as the Bureau prints it ("Cherokee County, Georgia"), its state's
FIPS code, and its 2020 residents. Nothing is dropped or chosen here:
code/clean/localities_southeastern.py decides which are counties of a body
the peer set must hold.
"""
import pandas as pd

from paths import CENSUS_BUREAU, source, write

COUNTIES = CENSUS_BUREAU / "2020" / "censusapi_dec_pl_P1_race_us_counties.csv.gz"


def build() -> pd.DataFrame:
    c = source(COUNTIES, dtype={"state": str, "county": str})
    return pd.DataFrame({"county_name": c["NAME"], "state_fips": c["state"],
                         "residents": c["P1_001N"]})


if __name__ == "__main__":
    write(build(), "localities_counties")
