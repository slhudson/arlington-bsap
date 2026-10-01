"""Members and residents, Arlington beside Virginia's other large localities
-> figures/localities_residents.pdf, .png

Every city and county of at least localities.SMALLEST residents in 2020:
residents across, members of the governing body up. The x axis breaks
after NEAR so that Fairfax stays in view. Arlington in its own colour; the
named dots are those the prose discusses.
"""
import charts
import paths
import localities
import style

NEAR = 560_000                    # the near side of the break
FAR = (1_050_000, 1_250_000)      # the far side, labelled at FAR_TICK
FAR_TICK = 1_200_000
# The dots named: those the prose discusses, and at least one in every
# cluster. charts.place_labels() decides where each name sits.
NAMED = {"Arlington", "Newport News", "Fairfax", "Richmond", "Chesapeake", "Norfolk", "Henrico",
         "Chesterfield", "Loudoun", "Prince William", "Virginia Beach", "Albemarle", "Alexandria"}
# Named with a short line to the dot: too close to its neighbours to name beside it.
LEADERS = {"Alexandria"}

for profile in style.PROFILES:
    style.apply(profile)

    d = localities.load(profile)
    fig, (near, far) = charts.broken_scatter(profile)
    for ax, side in ((near, d[d["residents"] <= NEAR]), (far, d[d["residents"] > NEAR])):
        charts.dots(ax, side["residents"], side["members"], side["area"], side["color"])
        for _, r in side[side["locality"].isin(NAMED)].iterrows():
            localities.name(ax, r, "residents", "members", leader=r["locality"] in LEADERS)

    charts.comma_axis(near.xaxis, NEAR, 100_000, "")
    charts.comma_axis(near.yaxis, 12, 2, "members")
    charts.break_x(near, far, "residents", FAR, FAR_TICK)

    charts.dot_legend(fig, localities.LEGEND, profile)
    paths.save(fig, profile)
