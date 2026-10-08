"""The county before 1915, in five areas -> data/clean/residents_by_district_boundaries.csv

The three magisterial districts as they stood from 1870 until the Board went
at-large in 1932, and the land Alexandria annexed in 1915 and 1930, each
piece of it marked with the district that held it. docs/residents.md, "Where the lines ran", has the
sources and the doubts.

The county then was the whole Virginia side of the ten-mile square less the
city. Today's Arlington outline gives most of it; the rest is the part of
today's Alexandria that lies northeast of the old District line, the
square's southwest edge, since the city has since taken in Fairfax land
beyond it. The city as it stood in 1912 is taken out. What remains is cut
into the land Alexandria annexed in 1915, the rest of today's Alexandria,
and what stayed in the county, and that is cut by the two lines noetzel1907
rules between the districts. Each cut is a decision about where a boundary
ran, which is why they are made here and not in the build.

data/built/ carries the keyed lines already extended past the county's
edges, so a line cuts the whole polygon. An area the cuts leave in two
parts is written as two, numbered in `part`.
"""
import numpy as np
import pandas as pd
import shapely.geometry as sg
import shapely.ops as so

from paths import built, typed, write

# North to south, since the two lines run roughly east-west.
DISTRICTS_NORTH_TO_SOUTH = ("Washington", "Arlington", "Jefferson")

# Gaps and slivers narrower than this are closed or dropped, in degrees: 20
# meters, about the width the fitted District line can sit from the county
# outline's own southwest edge. Not a position anyone claims.
CLOSE = 2e-4
DUST = 1e-7           # square degrees, about a quarter of an acre
SLIVER = 1.5e-3       # degrees, about 150 meters
SIMPLIFY = 5e-5       # degrees, about 5 meters: the outlines carry a vertex every few meters


def polygon(frame) -> sg.Polygon:
    d = typed(frame).sort_values("seq")
    return sg.Polygon(zip(d.lon, d.lat))


def keyed_line(frame, column, name) -> sg.LineString:
    d = frame[frame[column] == name].sort_values("seq")
    return sg.LineString(list(zip(d.lon, d.lat)))


def closed(shape):
    """Gaps narrower than CLOSE filled."""
    return shape.buffer(CLOSE).buffer(-CLOSE)


def opened(shape, width=CLOSE):
    """Slivers narrower than `width` dropped."""
    return shape.buffer(-width).buffer(width)


def parts(shape, what) -> list:
    """The polygons `shape` is, largest first, less any dust."""
    out = [g for g in getattr(shape, "geoms", [shape]) if g.geom_type == "Polygon" and g.area > DUST]
    if not out:
        raise AssertionError(f"{what} is empty")
    if any(g.interiors for g in out):
        raise AssertionError(f"{what} has a hole")
    return sorted(out, key=lambda g: -g.area)


def north_of(line, point) -> bool:
    """Whether `point` is on the left of `line` as keyed, west to east."""
    a = np.array(point.coords[0])
    best = None
    pts = list(line.coords)
    for p, q in zip(pts[:-1], pts[1:]):
        p, q = np.array(p), np.array(q)
        t = np.clip((a - p) @ (q - p) / ((q - p) @ (q - p)), 0, 1)
        dist = np.linalg.norm(a - (p + t * (q - p)))
        if best is None or dist < best[0]:
            best = (dist, (q - p)[0] * (a - p)[1] - (q - p)[1] * (a - p)[0])
    return best[1] > 0


def side_of(line, toward) -> sg.Polygon:
    """The half-plane on the side of `line` that holds the point `toward`."""
    a, b = (np.array(c) for c in line.coords)
    t = np.array(toward.coords[0])
    along = (b - a) / np.linalg.norm(b - a)
    normal = np.array([-along[1], along[0]])
    if (t - a) @ normal < 0:
        normal = -normal
    far = 2.0
    p0, p1 = a - along * far, b + along * far
    return sg.Polygon([p0, p1, p1 + normal * far, p0 + normal * far])


def snapped(shape, line):
    """`shape` with every vertex within CLOSE of `line` moved onto it, so an
    edge keyed along the line lies exactly on it."""
    pts = []
    for x, y in shape.exterior.coords[:-1]:
        p = sg.Point(x, y)
        if line.distance(p) < CLOSE:
            p = line.interpolate(line.project(p))
        pts.append((p.x, p.y))
    return sg.Polygon(pts)


def areas() -> dict:
    """{area name: [shapely polygons]} for the five areas."""
    limits = built("alexandria_limits_1912")
    district_line = keyed_line(typed(limits), "limit", "district_line")
    arlington = polygon(built("county_outline"))
    alexandria = polygon(built("alexandria_outline"))
    inside = arlington.representative_point()
    southeast_side = keyed_line(typed(limits), "limit", "southeast_side")
    # Today's Alexandria beyond Arlington, within the square, less any strip
    # narrower than SLIVER: the two counties' outlines come from different
    # surveys and disagree by up to a couple of hundred meters along their
    # shared edges, which would otherwise show as land of the city's.
    old_part = opened(alexandria.intersection(side_of(district_line, inside))
                      .intersection(side_of(southeast_side, inside)).difference(arlington), SLIVER)
    # The county had no holes: one left where the two outlines fail to meet
    # is their disagreement, and is filled.
    county = sg.Polygon(closed(arlington.union(old_part)).exterior)
    city = snapped(polygon(limits[limits.limit == "city_1912"]), district_line)
    land = opened(county.difference(city)).simplify(SIMPLIFY)

    # What Alexandria took in 1915 is the area its order described; what it
    # took in 1930 is the rest of today's city that lay in the county.
    in_1915 = polygon(typed(built("alexandria_annexation_1915"))).difference(city)
    a1915 = opened(land.intersection(in_1915))
    a1930 = opened(land.intersection(old_part.buffer(CLOSE)).difference(in_1915))
    left = opened(land.difference(a1915).difference(a1930))
    # A sliver of the county too thin to keep, where it borders the 1930
    # land, is the two surveys' disagreement, and goes with that land rather
    # than being drawn as no one's.
    dropped = land.difference(a1915).difference(a1930).difference(left)
    a1930 = so.unary_union([a1930] + [g for g in getattr(dropped, "geoms", [dropped])
                                      if g.distance(a1930) < CLOSE])

    lines = typed(built("district_lines"))
    wa = keyed_line(lines, "boundary", "washington_arlington")
    aj = keyed_line(lines, "boundary", "arlington_jefferson")
    pieces = list(left.geoms) if left.geom_type == "MultiPolygon" else [left]
    for cut in (wa, aj):
        pieces = [p for piece in pieces for p in so.split(piece, cut).geoms]
    named = {name: [] for name in DISTRICTS_NORTH_TO_SOUTH}
    for p in pieces:
        if p.area <= DUST:
            continue
        where = p.representative_point()
        name = ("Washington" if north_of(wa, where)
                else "Jefferson" if not north_of(aj, where) else "Arlington")
        named[name].append(p)
    empty = [n for n, g in named.items() if not g]
    if empty:
        raise AssertionError(
            f"the two lines split the county into {3 - len(empty)} districts, not 3: "
            f"a line in data/transcribed/by_claude/district_lines.csv no longer "
            f"crosses the whole county. Extend it past the county's edge.")
    out = {name: parts(so.unary_union(g), f"the {name} area") for name, g in named.items()}
    out["annexed 1915"] = parts(a1915, "the 1915 annexation")
    out["annexed 1930"] = parts(a1930, "the 1930 annexation")
    drawn = sum(g.area for shapes in out.values() for g in shapes)
    if abs(drawn - land.area) > 0.005 * land.area:
        raise AssertionError(
            f"the five areas cover {drawn:.6f} square degrees and the county less the 1912 city "
            f"{land.area:.6f}: a cut dropped or doubled land")
    return out


SOURCES = {"annexed 1915": "alexandria2024", "annexed 1930": "alexandria2024"}


def by_district(out: dict) -> list:
    """[(area, district, polygon)]: each annexed area cut by the
    noetzel1907 line between Arlington and Jefferson, so every piece of land
    says which district held it before Alexandria did."""
    aj = keyed_line(typed(built("district_lines")), "boundary", "arlington_jefferson")
    pieces = []
    for name, shapes in out.items():
        for shape in shapes:
            if name not in SOURCES:
                pieces.append((name, name, shape))
                continue
            for p in so.split(shape, aj).geoms:
                if p.area > DUST:
                    pieces.append((name, "Arlington" if north_of(aj, p.representative_point()) else "Jefferson", p))
    return pieces


def main():
    rows, parts = [], {}
    for name, district, shape in by_district(areas()):
        part = parts[name] = parts.get(name, 0) + 1
        for seq, (lon, lat) in enumerate(shape.exterior.coords, start=1):
            rows.append({"area": name, "district": district, "part": part, "seq": seq,
                         "lon": lon, "lat": lat, "source": SOURCES.get(name, "noetzel1907")})
    write(pd.DataFrame(rows), "residents_by_district_boundaries")


if __name__ == "__main__":
    main()
