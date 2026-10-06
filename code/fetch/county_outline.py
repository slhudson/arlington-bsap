"""The modern county outline -> data/raw/arlington_county/county_outline.geojson.gz

Run by hand, output committed; the build never touches the network
(CLAUDE.md).

    .venv/bin/python code/fetch/county_outline.py

Arlington County's own GIS Open Data service, the one polygon for the
county as a whole. Used for orientation and, in code/clean/district_lines.py,
to turn the 1907 magisterial district lines in
data/transcribed/by_claude/district_lines.csv into the three districts'
areas: a division of this polygon is also what removes the 1915 and 1930
annexations to Alexandria, since the land they took is not part of this
polygon.
"""
import json
import urllib.request

import paths

URL = ("https://arlgis.arlingtonva.us/arcgis/rest/services/Open_Data/"
       "od_County_Polygon/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson")
OUT = paths.RAW / "arlington_county" / "county_outline.geojson.gz"


def main():
    with urllib.request.urlopen(URL, timeout=60) as r:
        data = json.load(r)
    if data.get("type") != "FeatureCollection" or len(data.get("features", [])) != 1:
        raise SystemExit(f"expected one polygon feature, got: {str(data)[:200]}")
    paths.write_text(OUT, json.dumps(data, indent=1))
    print(f"  {OUT.relative_to(paths.ROOT)}")


if __name__ == "__main__":
    main()
