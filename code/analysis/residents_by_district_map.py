"""The county before 1915, in its three districts -> figures/residents_by_district_map.pdf, .png

Orientation for residents_by_district_race_adults: where each district was, 1870
to 1931, since the lines ended with the Board's at-large expansion in 1932
and nothing after draws them. The land Alexandria annexed in 1915 and 1930
is Jefferson's, in two tints of its colour. docs/residents.md, "Where the
lines ran", has what the lines rest on.
"""
import charts
import paths
import style

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
    # A name is wrapped after its first word, so "Arlington District" stands
    # on two lines; the 1915 area, too small for its name, is named beside it.
    names = {AREAS[area][0].replace(" ", "\n", 1) if area != "annexed 1915" else AREAS[area][0]:
             (shapes[area], AREAS[area][1]) for area in ORDER}
    charts.area_names(ax, names, beside=[AREAS["annexed 1915"][0]])
    charts.draft_mark(ax)        # until annexation-1915-line is settled (docs/questions.csv)
    paths.save(fig, profile)
