"""Residents per member and density, Arlington beside Virginia's other large
localities -> figures/board_peers_density.pdf, .png

Every city and county of at least SMALLEST residents in 2020: residents per
square mile across, residents per member of the governing body up.
Arlington in its own colour; the named dots are those the prose discusses.
"""
import pandas as pd

import charts
import paths
import style

SMALLEST = 100_000
# The dots named: those the prose discusses, and at least one in every
# cluster. charts.place_labels() decides where each name sits.
NAMED = {"Arlington", "Alexandria", "Fairfax", "Chesterfield", "Henrico", "Prince William",
         "Loudoun", "Virginia Beach", "Norfolk", "Richmond", "Chesapeake", "Hanover",
         "Roanoke"}

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.BOARD_PEERS)
    d = d[d["residents"] >= SMALLEST].copy()
    d["density"] = d["residents"] / d["land_sq_mi"]
    d["per_member"] = d["residents"] / d["members"]
    # Arlington last, so no other dot is drawn over it.
    d["arlington"] = d["locality"] == "Arlington"
    d = d.sort_values("arlington")
    d["color"] = d["kind"].map({k: c for k, (_, c) in style.PEERS.items()}).where(~d["arlington"], style.ARLINGTON)
    d["area"] = [charts.dot_area(a, profile) for a in d["arlington"]]

    fig, ax = charts.scatter(profile)
    charts.dots(ax, d["density"], d["per_member"], d["area"], d["color"])
    for _, r in d[d["locality"].isin(NAMED)].iterrows():
        charts.dot_label(ax, r["density"], r["per_member"], r["locality"], r["area"],
                         r["color"] if r["arlington"] else "black",
                         bold=r["arlington"])
    charts.comma_axis(ax.xaxis, 12_000, 2_000, "residents per square mile")
    charts.comma_axis(ax.yaxis, 120_000, 20_000, "residents per member")

    charts.dot_legend(fig, {label: c for label, c in style.PEERS.values()}, profile)
    paths.save(fig, "board_peers_density", profile)
