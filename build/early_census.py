"""Transcribed census figures -> data/clean/early_census.csv, 1870-1890.

Before 1900, Alexandria city was part of the county, so no published table
gives the territory the Board actually governed. That figure has to be derived,
and this is where the derivation lives.

Two routes, and they must agree:

    county outside the city = county including the city  -  the city
                            = arlington + jefferson + washington districts

Doing this in code rather than by hand is the point. Both errors found in the
delivered workbook are ones this file makes impossible: a fourth district
cannot be invented, because the districts are named here, and a race split that
does not sum to its total raises instead of silently leaving a residual.

Freedman village is transcribed but deliberately never summed. The census
prints it inside Arlington district, so adding it counts those residents twice.

See docs/sources.md for what "Arlington County" means and why.
"""
import pandas as pd

from files import EXTRACTED, write

DISTRICTS = ["arlington_district", "jefferson_district", "washington_district"]


def load():
    t = pd.read_csv(EXTRACTED / "by_eye" / "census_1870_1890.csv")
    return t.set_index(["year", "geography", "measure"])["value"]


def build() -> pd.DataFrame:
    v = load()
    rows = []
    for year in (1870, 1880, 1890):
        county = v.get((year, "alexandria_county_incl_city", "total"))
        city = v.get((year, "alexandria_city", "total"))
        by_subtraction = county - city

        # Second route, where the districts were transcribed.
        parts = [v.get((year, d, "total")) for d in DISTRICTS]
        by_districts = sum(parts) if all(pd.notna(parts)) else None

        if by_districts is not None and by_districts != by_subtraction:
            raise AssertionError(
                f"{year}: county minus city is {by_subtraction:,} but the three "
                f"districts sum to {by_districts:,}. One transcription is wrong.")

        row = {"year": year, "total": by_subtraction}

        # Race, where both the county and city splits were transcribed.
        for ours, theirs in (("white", "white"), ("black", "colored")):
            c = v.get((year, "alexandria_county_incl_city", theirs))
            y = v.get((year, "alexandria_city", theirs))
            row[ours] = c - y if pd.notna(c) and pd.notna(y) else pd.NA

        # The check the delivered workbook would have failed for 1870: a race
        # split must account for its own total, give or take categories the
        # census footnotes separately.
        if pd.notna(row["white"]) and pd.notna(row["black"]):
            gap = row["total"] - row["white"] - row["black"]
            if abs(gap) > 5:
                raise AssertionError(
                    f"{year}: white {row['white']:,} + black {row['black']:,} "
                    f"leaves {gap:,} of a total of {row['total']:,} unaccounted.")
            row["unaccounted"] = gap
        rows.append(row)

    d = pd.DataFrame(rows)

    # Freedman village is transcribed but must never be added as a district.
    assert "freedman_village" not in DISTRICTS, "Freedman village is inside Arlington district"
    return d


if __name__ == "__main__":
    d = build()
    print(d.to_string(index=False))
    write(d, "early_census")
