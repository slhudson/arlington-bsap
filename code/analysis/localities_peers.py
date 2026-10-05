"""Arlington beside Virginia's other large localities, two ways
-> figures/localities_peers.pdf, .png

Every city and county of at least localities.SMALLEST residents in 2020.
(a) Residents across, members of the governing body up; the x axis breaks
after NEAR so that Fairfax stays in view. (b) Residents per square mile
across, residents per member up. One legend for both; Arlington in its own
colour; the named dots are those the prose discusses.
"""
import charts
import paths
import localities
import style

NEAR = 520_000                    # (a): the near side of the break
FAR = (1_050_000, 1_250_000)      # (a): the far side, labelled at FAR_TICK
FAR_TICK = 1_200_000
# The dots named in each panel: those the prose discusses, and at least one in
# every cluster. labels.place() decides where each name sits.
NAMED_A = {"Arlington", "Fairfax", "Richmond", "Norfolk",
           "Chesterfield", "Loudoun", "Prince William", "Virginia Beach", "Albemarle", "Alexandria"}
NAMED_B = {"Arlington", "Alexandria", "Fairfax", "Chesterfield", "Henrico", "Prince William",
           "Loudoun", "Virginia Beach", "Norfolk", "Stafford",
           "Roanoke"}
# Named with a short line to the dot: too close to its neighbours to name beside it.
LEADERS_A = {"Alexandria"}
LEADERS_B = {"Stafford", "Chesterfield"}  # too close to Henrico once panel (b) shrank for the 5 October height fix

for profile in style.PROFILES:
    style.apply(profile)

    d = localities.load(profile)
    d["density"] = d["residents"] / d["land_sq_mi"]
    d["per_member"] = d["residents"] / d["members"]

    fig, (near, far), b = charts.scatter_pair(profile)

    for ax, side in ((near, d[d["residents"] <= NEAR]), (far, d[d["residents"] > NEAR])):
        charts.dots(ax, side["residents"], side["members"], side["area"], side["color"])
        for _, r in side[side["locality"].isin(NAMED_A)].iterrows():
            localities.name(ax, r, "residents", "members", leader=r["locality"] in LEADERS_A)
    charts.comma_axis(near.xaxis, NEAR, 200_000, "", per=1000)
    charts.comma_axis(near.yaxis, 12, 2, "members")
    charts.break_x(near, far, "residents (thousands)", FAR, FAR_TICK, per=1000)
    charts.title_broken(near, "(a) members and residents")

    charts.dots(b, d["density"], d["per_member"], d["area"], d["color"])
    for _, r in d[d["locality"].isin(NAMED_B)].iterrows():
        localities.name(b, r, "density", "per_member", leader=r["locality"] in LEADERS_B)
    charts.comma_axis(b.xaxis, 12_000, 4_000, "residents per square mile")
    charts.comma_axis(b.yaxis, 120_000, 20_000, "residents per member (thousands)", per=1000)
    b.set_title("(b) residents per member and density")

    charts.dot_legend(fig, localities.LEGEND, profile)
    paths.save(fig, profile)
