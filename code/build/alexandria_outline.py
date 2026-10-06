"""data/raw/us_census_bureau/alexandria_outline.geojson -> data/built/alexandria_outline.csv

A pass-through: the one polygon's exterior ring, unpacked from GeoJSON into
one row per vertex, in order. Every coordinate the source carries is still
here; nothing is simplified or closed differently.
"""
import json

import pandas as pd

import paths


def main():
    path = paths.RAW / "us_census_bureau" / "alexandria_outline.geojson"
    data = json.loads(path.read_text())
    ring = data["features"][0]["geometry"]["coordinates"][0]
    frame = pd.DataFrame({"seq": range(1, len(ring) + 1),
                          "lon": [c[0] for c in ring],
                          "lat": [c[1] for c in ring]})
    paths.write(frame, "alexandria_outline")


if __name__ == "__main__":
    main()
