"""The three magisterial districts' areas -> figures/residents_by_district_map.pdf, .png

Orientation for residents_by_district_race: where each district was, 1870
to 1931, since the lines ended with the Board's at-large expansion in 1932
and nothing after draws them. No basemap and no roads - the county's own
outline and the three districts, each in the colour residents_by_district_race
already gives it.
"""
import matplotlib.patches as mpatches
import numpy as np

import charts
import paths
import style


def polygons() -> dict:
    """{district: Nx2 array of lon, lat, closed} from data/clean/."""
    d = paths.read("residents_by_district_boundaries")
    return {district: g.sort_values("seq")[["lon", "lat"]].to_numpy()
            for district, g in d.groupby("district")}


for profile in style.PROFILES:
    style.apply(profile)

    areas = polygons()
    assert set(areas) == set(style.DISTRICTS), f"a district with no area drawn: {areas.keys()}"

    fig, ax = charts.figure(profile, aspect=style.MAP_ASPECT)
    for district, (label, color) in style.DISTRICTS.items():
        ax.add_patch(mpatches.Polygon(areas[district], closed=True,
                                      facecolor=color, edgecolor="white", linewidth=1.0))
    all_points = np.concatenate(list(areas.values()))
    ax.set_xlim(all_points[:, 0].min(), all_points[:, 0].max())
    ax.set_ylim(all_points[:, 1].min(), all_points[:, 1].max())
    ax.set_aspect(1 / np.cos(np.radians(all_points[:, 1].mean())))
    ax.set_axis_off()
    charts.legend(fig, {l: c for l, c in style.DISTRICTS.values()})
    paths.save(fig, profile)
