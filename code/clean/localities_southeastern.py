"""Arlington's Board beside nineteen southeastern cities of its size
-> data/clean/localities_southeastern.csv

One row per city: its voting seats and its residents. A city's seats are
the appendix's council members, a Mayor who sits and votes included as the
appendix counts one (docs/localities.md). Its residents are the appendix's
thousands, so a peer's figure is good to the nearest thousand; Arlington's
row is the Board's five and its 2020 census total, from
data/clean/localities.csv.

The peer set is a rule, not a choice: every incorporated place of 180,000
to 300,000 residents in 2020 in the nine states the appendix names. The
Census places file is read for that, and the step stops if the appendix
lists a city the rule does not, or the rule finds one the appendix omits.
"""
import re

import pandas as pd

import paths
from paths import write

LOW, HIGH = 180_000, 300_000
# The nine states of the appendix's note, by FIPS code.
STATES = {"01": "AL", "05": "AR", "13": "GA", "22": "LA", "28": "MS",
          "37": "NC", "45": "SC", "47": "TN", "51": "VA"}


def city_key(place_name: str, state: str):
    """"Mobile city, Alabama" -> "Mobile", for an incorporated place;
    None for a census-designated place, which has no council. Augusta is
    printed as a consolidated government, "Augusta-Richmond County
    consolidated government (balance)", and the appendix calls it Augusta."""
    base = place_name.rsplit(", ", 1)[0]
    if base.endswith(" CDP"):
        return None
    if " consolidated government" in base:
        return base.split("-")[0]
    return re.sub(r" (city|town|village|borough)$", "", base)


def places_in_range() -> set:
    """"Mobile, AL" for every incorporated place in the nine states whose
    2020 population is within LOW and HIGH."""
    p = paths.built("localities_places")
    p = p[p["state_fips"].isin(STATES) & p["residents"].astype(int).between(LOW, HIGH)]
    keys = {(city_key(n, s), STATES[s]) for n, s in zip(p["place_name"], p["state_fips"])}
    return {f"{c}, {st}" for c, st in keys if c}


def build() -> pd.DataFrame:
    b = paths.built("localities_southeastern")
    listed = set(b["city"])
    found = places_in_range()
    if listed != found:
        raise AssertionError(
            "Appendix E does not list the cities of 180,000 to 300,000 in its nine states.\n"
            f"  listed, not found: {sorted(listed - found)}\n"
            f"  found, not listed: {sorted(found - listed)}")
    out = pd.DataFrame({
        "locality": b["city"].str.rsplit(", ", n=1).str[0],
        "state": b["city"].str.rsplit(", ", n=1).str[1],
        "members": b["council_members"].astype(int),
        "members_source": b["source"],
        "residents": b["residents_thousands"].astype(int) * 1000,
    })
    own = paths.read("localities")
    arl = own[own["locality"] == "Arlington"].iloc[0]
    return pd.concat([out, pd.DataFrame([{
        "locality": "Arlington", "state": "VA", "members": int(arl["members"]),
        "members_source": arl["members_source"], "residents": int(arl["residents"])}])],
        ignore_index=True)


if __name__ == "__main__":
    write(build(), "localities_southeastern")
