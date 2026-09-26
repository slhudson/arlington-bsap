"""Residents per member and density, Arlington beside Virginia's other large
localities -> figures/board_peers_density.pdf, .png

Every city and county of at least peers.SMALLEST residents in 2020:
residents per square mile across, residents per member of the governing
body up. Arlington in its own colour; the named dots are those the prose
discusses.
"""
import charts
import paths
import peers
import style

# The dots named: those the prose discusses, and at least one in every
# cluster. charts.place_labels() decides where each name sits.
NAMED = {"Arlington", "Alexandria", "Fairfax", "Chesterfield", "Henrico", "Prince William",
         "Loudoun", "Virginia Beach", "Norfolk", "Richmond", "Chesapeake", "Hanover",
         "Roanoke"}

for profile in style.PROFILES:
    style.apply(profile)

    d = peers.load(profile)
    d["density"] = d["residents"] / d["land_sq_mi"]
    d["per_member"] = d["residents"] / d["members"]

    fig, ax = charts.scatter(profile)
    charts.dots(ax, d["density"], d["per_member"], d["area"], d["color"])
    for _, r in d[d["locality"].isin(NAMED)].iterrows():
        peers.name(ax, r, "density", "per_member")
    charts.comma_axis(ax.xaxis, 12_000, 2_000, "residents per square mile")
    charts.comma_axis(ax.yaxis, 120_000, 20_000, "residents per member")

    charts.dot_legend(fig, peers.LEGEND, profile)
    paths.save(fig, "board_peers_density", profile)
