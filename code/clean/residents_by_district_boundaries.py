"""The three magisterial districts' areas -> data/clean/residents_by_district_boundaries.csv

data/built/district_lines.csv carries the two lines noetzel1907 rules
between the districts, each already extended past the county's edges so it
cuts the county polygon cleanly. Splitting the county polygon on both lines
is the decision this step makes: which side of each line is which district,
and that the annexations Alexandria took in 1915 and 1930 are removed by
using the modern county outline rather than 1907's, so no separate
annexation geometry is needed (docs/residents.md). The split is otherwise
mechanical - the same two lines always cut the same county the same way -
which is why it is one function and the module holds no other judgment.
"""
import pandas as pd
import shapely.geometry
import shapely.ops

from paths import built, typed, write

# North to south, since the two lines run roughly east-west and nothing in
# hand says the district order was ever otherwise. style/ names the same
# three and their colours for the figure; this stage has no path to style/
# (CLAUDE.md), so the names are repeated here rather than imported.
DISTRICTS_NORTH_TO_SOUTH = ("Washington", "Arlington", "Jefferson")


def county_polygon():
    """The modern county outline as a shapely polygon."""
    d = typed(built("county_outline")).sort_values("seq")
    return shapely.geometry.Polygon(zip(d.lon, d.lat))


def cutting_line(lines, boundary):
    """One boundary's vertices from data/built/district_lines.csv, in order,
    as a shapely line."""
    d = lines[lines.boundary == boundary].sort_values("seq")
    return shapely.geometry.LineString(list(zip(d.lon, d.lat)))


def districts() -> dict:
    """{district name: shapely polygon}, split from the county outline by
    both lines in turn."""
    lines = typed(built("district_lines"))
    county = county_polygon()
    pieces = list(shapely.ops.split(county, cutting_line(lines, "washington_arlington")).geoms)
    split_again = []
    for piece in pieces:
        split_again += list(shapely.ops.split(piece, cutting_line(lines, "arlington_jefferson")).geoms)
    if len(split_again) != 3:
        raise AssertionError(
            f"the two lines split the county into {len(split_again)} pieces, not 3: "
            f"a line in data/transcribed/by_claude/district_lines.csv no longer "
            f"crosses the whole county. Extend it past the county's edge.")
    by_latitude = sorted(split_again, key=lambda g: -g.centroid.y)
    return dict(zip(DISTRICTS_NORTH_TO_SOUTH, by_latitude))


def main():
    rows = []
    for district, polygon in districts().items():
        for seq, (lon, lat) in enumerate(polygon.exterior.coords, start=1):
            rows.append({"district": district, "seq": seq, "lon": lon, "lat": lat,
                         "source": "noetzel1907"})
    write(pd.DataFrame(rows), "residents_by_district_boundaries")


if __name__ == "__main__":
    main()
