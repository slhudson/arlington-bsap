"""The county before 1915, in its three districts -> figures/residents_by_district_map.pdf, .png

Orientation for residents_by_district_race_adults: where each district was, 1870
to 1931, since the lines ended with the Board's at-large expansion in 1932
and nothing after draws them. Each district is drawn whole, as it stood
before 1915, and named; the land Alexandria annexed in 1915 and 1930 is the
only colour, keyed in the corner. docs/residents.md, "Where the lines ran",
has what the lines rest on.
"""
import charts
import paths
import style

DISTRICTS = ("Washington", "Arlington", "Jefferson")


def outlines() -> dict:
    """{(area, district): [Nx2 arrays of lon, lat]} from data/clean/."""
    d = paths.read("residents_by_district_boundaries")
    return {key: [g.sort_values("seq")[["lon", "lat"]].to_numpy() for _, g in a.groupby("part")]
            for key, a in d.groupby(["area", "district"])}


for profile in style.PROFILES:
    style.apply(profile)

    shapes = outlines()
    areas = {area for area, _ in shapes}
    assert areas == set(DISTRICTS) | set(style.ANNEXED), f"an area with nothing drawn: {areas}"

    fig, ax = charts.map_figure(profile, [s for parts in shapes.values() for s in parts])
    for (area, _), parts in shapes.items():
        charts.areas(ax, parts, style.ANNEXED[area][1] if area in style.ANNEXED else style.MAP_GROUND)
    for district in DISTRICTS:
        charts.edges(ax, [s for (_, d), parts in shapes.items() if d == district for s in parts])
    # A district is named at the centre of the land it kept, so Jefferson's
    # name stays off the annexed land.
    charts.area_names(ax, {style.DISTRICTS[d][0].replace(" ", "\n", 1): (shapes[(d, d)], style.MAP_GROUND)
                           for d in DISTRICTS})
    charts.map_legend(ax, style.ANNEXED_HEADING, dict(style.ANNEXED.values()))
    charts.draft_mark(ax)        # until annexation-1915-line is settled (docs/questions.csv)
    paths.save(fig, profile)
