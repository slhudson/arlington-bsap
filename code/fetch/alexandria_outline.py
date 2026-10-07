"""The modern city of Alexandria's outline -> sources/government/federal/us_census_bureau/alexandria_outline.geojson.gz

Run by hand, output committed; the build never touches the network
(CLAUDE.md).

    .venv/bin/python code/fetch/alexandria_outline.py

The Census Bureau's TIGERweb State_County service, the independent city's
polygon (GEOID 51510). Joined in code/clean/residents_by_district_boundaries.py
with Arlington's own outline to give the county as it stood before 1915: the
part of today's city that lay in Alexandria County is the land the city
annexed in 1915 and 1930.
"""
import json
import urllib.request

import paths

URL = ("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/"
       "MapServer/1/query?where=GEOID%3D%2751510%27&outFields=GEOID%2CNAME&f=geojson")
OUT = paths.CENSUS_BUREAU / "alexandria_outline.geojson.gz"


def main():
    with urllib.request.urlopen(URL, timeout=60) as r:
        data = json.load(r)
    features = data.get("features", [])
    if len(features) != 1 or features[0]["properties"].get("GEOID") != "51510":
        raise SystemExit(f"expected one feature with GEOID 51510, got: {str(data)[:200]}")
    paths.write_text(OUT, json.dumps(data, indent=1))
    print(f"  {OUT.relative_to(paths.ROOT)}")


if __name__ == "__main__":
    main()
