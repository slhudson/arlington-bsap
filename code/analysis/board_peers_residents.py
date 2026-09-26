"""Members and residents, Arlington beside Virginia's other large localities
-> figures/board_peers_residents.pdf, .png

Every city and county of at least SMALLEST residents in 2020: residents
across, members of the governing body up. The x axis breaks after NEAR so
that Fairfax stays in view. Arlington in its own colour; the named dots
are those the prose discusses.
"""
import pandas as pd

import charts
import paths
import style

SMALLEST = 100_000
NEAR = 560_000                    # the near side of the break
FAR = (1_050_000, 1_250_000)      # the far side
# The dots named: those the prose discusses, and at least one in every
# cluster. charts.place_labels() decides where each name sits.
NAMED = {"Arlington", "Newport News", "Fairfax", "Richmond", "Chesapeake", "Norfolk", "Henrico",
         "Chesterfield", "Loudoun", "Prince William", "Virginia Beach", "Albemarle", "Alexandria"}
# Named with a short line to the dot: too close to its neighbours to name beside it.
LEADERS = {"Alexandria"}

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.BOARD_PEERS)
    d = d[d["residents"] >= SMALLEST].copy()
    # Arlington last, so no other dot is drawn over it.
    d["arlington"] = d["locality"] == "Arlington"
    d = d.sort_values("arlington")
    d["color"] = d["kind"].map({k: c for k, (_, c) in style.PEERS.items()}).where(~d["arlington"], style.ARLINGTON)
    d["area"] = [charts.dot_area(a, profile) for a in d["arlington"]]

    fig, (near, far) = charts.broken_scatter(profile)
    for ax, side in ((near, d[d["residents"] <= NEAR]), (far, d[d["residents"] > NEAR])):
        charts.dots(ax, side["residents"], side["members"], side["area"], side["color"])
        for _, r in side[side["locality"].isin(NAMED)].iterrows():
            charts.dot_label(ax, r["residents"], r["members"], r["locality"], r["area"],
                             r["color"] if r["arlington"] else "black",
                             bold=r["arlington"], leader=r["locality"] in LEADERS)

    charts.comma_axis(near.xaxis, NEAR, 100_000, "")
    charts.comma_axis(near.yaxis, 12, 2, "members")
    far.set_xlim(*FAR)
    far.xaxis.set_major_locator(charts.FixedLocator([1_200_000]))
    far.xaxis.set_major_formatter(charts.THOUSANDS)
    charts.break_x(near, far, "residents")

    charts.dot_legend(fig, {label: c for label, c in style.PEERS.values()}, profile)
    paths.save(fig, "board_peers_residents", profile)
