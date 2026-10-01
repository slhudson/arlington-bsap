"""Virginia's governing bodies beside Arlington's -> data/clean/localities.csv

One row per locality: its kind (city or county), its voting members, its
2020 residents and its land area, each with a source.

A city's members are its council members, and a Mayor elected at large
counts as one more unless the appendix says the Mayor sits outside council,
which it says only of Richmond. docs/localities.md has the reasoning.

Every count must lie within the three to eleven members the Code of
Virginia allows a governing body.
"""
import pandas as pd

import paths
from paths import write

AT_LARGE = "elected at large"
FROM_MEMBERS = "one of the members"


def members(row) -> int:
    """A locality's voting members."""
    if row["kind"] == "county":
        return int(row["members"])
    if row["mayor"] not in (AT_LARGE, FROM_MEMBERS):
        raise ValueError(f"{row['locality']}: unknown mayor {row['mayor']!r}")
    extra = row["mayor"] == AT_LARGE and row["mayor_on_council"] != "no"
    return int(row["council_members"]) + int(extra)


def build() -> pd.DataFrame:
    b = paths.built("localities")
    out = pd.DataFrame({
        "locality": b["locality"],
        "kind": b["kind"],
        "members": b.apply(members, axis=1),
        "members_source": b["members_source"],
        "members_note": b["members_note"],
        "residents": b["residents"].astype(int),
        "residents_source": b["residents_source"],
        "land_sq_mi": b["land_sq_mi"].astype(float),
        "land_source": b["land_source"],
    })
    bad = out[~out["members"].between(3, 11)]
    if len(bad):
        raise AssertionError("outside the Code's three to eleven members: "
                             + ", ".join(bad["locality"] + f" ({bad['members'].tolist()})"))
    if (out["locality"] == "Arlington").sum() != 1:
        raise AssertionError("expected exactly one Arlington row")
    return out


if __name__ == "__main__":
    write(build(), "localities")
