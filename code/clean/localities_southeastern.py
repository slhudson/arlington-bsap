"""Arlington's Board beside the southeastern cities and counties of its size
-> data/clean/localities_southeastern.csv

One row per body: its voting seats and its 2020 census residents, Arlington
last. A body's seats are keyed in from three places: Appendix E of Richmond's
charter review for the nineteen cities it tabulates (its council members, a
Mayor who sits and votes included as the appendix counts one), Virginia's own
table (data/clean/localities.csv) for the Virginia bodies it holds, and the
body's own page for every other (transcribed/by_claude/southeastern_bodies.csv).
Residents are the Census Bureau's 2020 count for the place or county, which is
what the rule below reads.

The peer set is a rule, not a choice (docs/localities.md): every incorporated
place and every county or parish of 150,000 to 300,000 residents in 2020 in
the nine states the appendix names and Maryland. A county is left out where
the county is not the body that governs it: a Virginia independent city is
a city, and a consolidated city-county is the city it is named for. The step
stops if the rule finds a body no table keys, or a table keys one the rule
does not find.
"""
import re

import pandas as pd

import paths
from paths import write

LOW, HIGH = 150_000, 300_000
# The nine states of the appendix's note and Maryland, by FIPS code.
STATES = {"01": "AL", "05": "AR", "13": "GA", "22": "LA", "24": "MD", "28": "MS",
          "37": "NC", "45": "SC", "47": "TN", "51": "VA"}
# Counties whose government is a city's: Georgia's consolidated governments.
# Each is counted as the city it is named for, so the county is not a second body.
COUNTY_IS_CITY = {"Bibb County, GA": "Macon-Bibb County, GA",
                  "Muscogee County, GA": "Columbus, GA",
                  "Richmond County, GA": "Augusta, GA"}


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


def county_name(name: str, state: str) -> str:
    """"Cherokee County, Georgia" -> "Cherokee County, GA"; a Louisiana
    parish keeps its name."""
    return f"{name.rsplit(', ', 1)[0]}, {STATES[state]}"


def places_in_range() -> dict:
    """{"Mobile, AL": 187041} for every incorporated place in these states
    whose 2020 population is within LOW and HIGH."""
    p = paths.built("localities_places")
    p = p[p["state_fips"].isin(STATES) & p["residents"].astype(int).between(LOW, HIGH)]
    found = {}
    for n, s, r in zip(p["place_name"], p["state_fips"], p["residents"]):
        c = city_key(n, s)
        if c:
            found[f"{c}, {STATES[s]}"] = int(r)
    return found


def counties_in_range() -> dict:
    """{"Cherokee County, GA": 266620} for every county or parish in these
    states within LOW and HIGH, less Arlington itself, the Virginia
    independent cities (the Bureau lists them as counties) and the
    consolidated governments COUNTY_IS_CITY names."""
    c = paths.built("localities_counties")
    c = c[c["state_fips"].isin(STATES) & c["residents"].astype(int).between(LOW, HIGH)]
    found = {county_name(n, s): int(r)
             for n, s, r in zip(c["county_name"], c["state_fips"], c["residents"])
             if " city, " not in n}
    found.pop("Arlington County, VA", None)
    for county in COUNTY_IS_CITY:
        found.pop(county, None)
    return found


def keyed(found: set) -> pd.DataFrame:
    """Every body keyed: Appendix E first, then the bodies' own pages, then
    Virginia's table for the Virginia bodies the rule finds that neither
    carries, whose seats fill_virginia() reads later. A body keyed twice stops
    the step, so each count has one source."""
    a = paths.built("localities_southeastern")
    appendix = pd.DataFrame({"key": a["city"], "kind": "city",
                             "members": a["council_members"].astype(int),
                             "source": a["source"]})
    b = paths.built("localities_southeastern_bodies")
    own = pd.DataFrame({"key": b["body"], "kind": b["kind"],
                        "members": b["members"].astype(int), "source": b["source"]})
    out = pd.concat([appendix, own], ignore_index=True)
    twice = out[out["key"].duplicated()]["key"].tolist()
    if twice:
        raise AssertionError(f"keyed from more than one source: {sorted(twice)}")
    v = paths.built("localities")
    v["key"] = [f"{n} County, VA" if k == "county" else f"{n}, VA"
                for n, k in zip(v["locality"], v["kind"])]
    v = v[v["key"].isin(found - set(out["key"]))]
    return pd.concat([out, pd.DataFrame({"key": v["key"], "kind": v["kind"],
                                         "members": 0, "source": "virginia"})],
                     ignore_index=True)


def fill_virginia(k: pd.DataFrame) -> pd.DataFrame:
    """The seats and source of the Virginia bodies from Virginia's own
    table, read only once every body is known to be keyed."""
    v = paths.read("localities").set_index("locality")
    k = k.copy()
    for i in k.index[k["source"] == "virginia"]:
        name = k.at[i, "key"].rsplit(", ", 1)[0].replace(" County", "")
        k.at[i, "members"] = int(v.loc[name, "members"])
        k.at[i, "source"] = v.loc[name, "members_source"]
    return k


def build() -> pd.DataFrame:
    residents = {**places_in_range(), **counties_in_range()}
    kind = {**dict.fromkeys(places_in_range(), "city"),
            **dict.fromkeys(counties_in_range(), "county")}
    keyed_bodies = keyed(set(residents))
    listed = set(keyed_bodies["key"])
    found = set(residents)
    for county, city in COUNTY_IS_CITY.items():
        if city not in found:
            raise AssertionError(f"{county} is counted as {city}, which the rule does not find")
    if listed != found:
        raise AssertionError(
            f"The tables do not hold every body of {LOW:,} to {HIGH:,} residents in these states.\n"
            f"  found, not keyed: {sorted(found - listed)}\n"
            f"  keyed, not found: {sorted(listed - found)}")
    wrong = keyed_bodies[keyed_bodies["key"].map(kind) != keyed_bodies["kind"]]
    if len(wrong):
        raise AssertionError(f"keyed as the wrong kind: {sorted(wrong['key'])}")
    keyed_bodies = fill_virginia(keyed_bodies)
    name = keyed_bodies["key"].str.rsplit(", ", n=1).str[0]
    out = pd.DataFrame({
        "locality": name.str.replace(r" (County|Parish)$", "", regex=True),
        "state": keyed_bodies["key"].str.rsplit(", ", n=1).str[1],
        "kind": keyed_bodies["kind"],
        "members": keyed_bodies["members"],
        "members_source": keyed_bodies["source"],
        "residents": keyed_bodies["key"].map(residents),
    }).sort_values(["state", "kind", "locality"]).reset_index(drop=True)
    if out.duplicated(["locality", "state", "kind"]).any():
        raise AssertionError("two bodies share a name, state and kind")
    own = paths.read("localities")
    arl = own[own["locality"] == "Arlington"].iloc[0]
    return pd.concat([out, pd.DataFrame([{
        "locality": "Arlington", "state": "VA", "kind": "county",
        "members": int(arl["members"]), "members_source": arl["members_source"],
        "residents": int(arl["residents"])}])], ignore_index=True)


if __name__ == "__main__":
    write(build(), "localities_southeastern")
