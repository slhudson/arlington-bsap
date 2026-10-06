"""The county before 1915, in its three districts -> figures/residents_by_district_map.pdf, .png

Orientation for residents_by_district_race: where each district was, 1870
to 1931, since the lines ended with the Board's at-large expansion in 1932
and nothing after draws them. The land Alexandria annexed in 1915 and 1930
is Jefferson's, in two tints of its colour. docs/residents.md, "Where the
lines ran", has what the lines rest on.
"""
import charts
import paths
import style

# North to south on the page, which is the order the legend reads.
AREAS = {**style.DISTRICTS, **style.ANNEXED}
ORDER = ("Washington", "Arlington", "Jefferson", "annexed 1915", "annexed 1930")


def outlines() -> dict:
    """{area: [Nx2 arrays of lon, lat]} from data/clean/."""
    d = paths.read("residents_by_district_boundaries")
    return {area: [g.sort_values("seq")[["lon", "lat"]].to_numpy() for _, g in a.groupby("part")]
            for area, a in d.groupby("area")}


for profile in style.PROFILES:
    style.apply(profile)

    shapes = outlines()
    assert set(shapes) == set(ORDER), f"an area with nothing drawn: {set(ORDER) ^ set(shapes)}"

    fig, ax = charts.map_figure(profile, [s for parts in shapes.values() for s in parts])
    for area in ORDER:
        charts.areas(ax, shapes[area], AREAS[area][1])
    charts.corner_legend(ax, {AREAS[area][0]: AREAS[area][1] for area in ORDER},
                         indented=[AREAS[a][0] for a in style.ANNEXED])
    paths.save(fig, profile)
