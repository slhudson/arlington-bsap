"""Arlington's Board beside nineteen southeastern cities of its size
-> data/clean/localities_southeastern.csv

One row per city: its voting seats, and how many of them are elected at
large. Arlington's row is the Board's five, all at large, from
data/clean/localities.csv.

A city's seats are the appendix's council members. Its at-large seats are
the ones the appendix's election column counts as at-large; a council
printed as "Ward" alone has none. The two counts must add to the council
members: they do for every city in the appendix, and a city that stopped
adding up is refused. The appendix counts a Mayor who sits and votes as one
at-large seat, as Appendix D does (docs/localities.md), and leaves out one
who is chief executive without a seat.
"""
import re

import pandas as pd

import paths
from paths import write


def split(printed: str, members: int, city: str) -> tuple:
    """(ward seats, at-large seats) from an election column: "9 Ward",
    "Ward" or "7 Ward/3 at-large". A bare "Ward" is every member."""
    ward = re.search(r"(\d+) Ward", printed)
    large = re.search(r"(\d+) at-large", printed)
    if printed == "Ward":
        w, a = members, 0
    elif ward or large:
        w = int(ward.group(1)) if ward else 0
        a = int(large.group(1)) if large else 0
    else:
        raise ValueError(f"{city}: cannot read the election {printed!r}")
    if w + a != members:
        raise AssertionError(f"{city}: {w} ward and {a} at-large seats are not "
                             f"the {members} members printed")
    return w, a


def build() -> pd.DataFrame:
    b = paths.built("localities_southeastern")
    seats = b["council_members"].astype(int)
    parts = [split(p, int(m), c) for p, m, c in zip(b["at_large_or_ward"], seats, b["city"])]
    out = pd.DataFrame({
        "locality": b["city"].str.rsplit(", ", n=1).str[0],
        "state": b["city"].str.rsplit(", ", n=1).str[1],
        "members": seats,
        "ward_members": [w for w, _ in parts],
        "at_large_members": [a for _, a in parts],
        "members_source": b["source"],
    })
    own = paths.read("localities")
    arl = own[own["locality"] == "Arlington"].iloc[0]
    out = pd.concat([out, pd.DataFrame([{
        "locality": "Arlington", "state": "VA", "members": int(arl["members"]),
        "ward_members": 0, "at_large_members": int(arl["members"]),
        "members_source": arl["members_source"]}])], ignore_index=True)
    return out


if __name__ == "__main__":
    write(build(), "localities_southeastern")
