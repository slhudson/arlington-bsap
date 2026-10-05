"""Every U.S. place's 2020 population -> data/built/localities_places.csv

The Census API's redistricting file for places, as fetched by
code/fetch/census_places.py, one row per place: its full name as the Bureau
prints it ("Mobile city, Alabama"), its state's FIPS code, and its 2020
residents. Nothing is dropped or chosen here: code/clean/localities_southeastern.py
decides which places are cities and which of them the peer set must hold.
"""
import pandas as pd

from paths import RAW, source, write

PLACES = RAW / "us_census_bureau" / "2020" / "censusapi_dec_pl_P1_race_us_places.csv.gz"


def build() -> pd.DataFrame:
    p = source(PLACES, dtype={"state": str, "place": str})
    return pd.DataFrame({"place_name": p["NAME"], "state_fips": p["state"],
                         "residents": p["P1_001N"]})


if __name__ == "__main__":
    write(build(), "localities_places")
