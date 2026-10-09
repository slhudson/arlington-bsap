"""Arlington beside its peers -> figures/localities_per_member.pdf, .png

Residents per member against residents: (a) Virginia's cities and counties
of at least localities.SMALLEST residents, its axis broken so Fairfax stays
in view; (b) the southeastern cities and counties of 150,000 to 300,000,
its axis broken so the run up from zero is cut. One legend; Arlington in
its own colour.
"""
import charts
import paths
import style
import localities

NEAR_A = 640_000                  # (a): room for a name to the right of Virginia Beach
FAR_A = (1_050_000, 1_250_000)
FAR_TICK_A = 1_200_000
NEAR_B = 40_000                   # (b): just the 0
FAR_B = (140_000, 300_000)       # (b): the set starts at 150,000; a margin keeps its first dot off the cut

# (a) names as many Virginia places as fit, the reader's own; (b) only
# Arlington, since what it adds is where Arlington stands, not which peer is which.
NAMED_A = {"Arlington", "Fairfax", "Richmond", "Norfolk", "Chesapeake", "Chesterfield", "Henrico",
           "Loudoun", "Prince William", "Virginia Beach", "Albemarle", "Alexandria"}
LEADERS_A = {"Alexandria", "Norfolk"}
NAMED_B = {"Arlington"}
LEADERS_B = {"Arlington"}

SE_COLORS = {kind: color for kind, (_, color) in style.LOCALITIES.items()}

for profile in style.PROFILES:
    style.apply(profile)

    fig, (near_a, far_a), (near_b, far_b) = charts.scatter_pair(
        profile, ratios=(style.BROKEN, style.BROKEN_FLOOR))

    d = localities.load(profile)
    d["per_member"] = d["residents"] / d["members"]
    for ax, side in ((near_a, d[d["residents"] <= NEAR_A]), (far_a, d[d["residents"] > NEAR_A])):
        charts.dots(ax, side["residents"], side["per_member"], side["area"], side["color"])
        for _, r in side[side["locality"].isin(NAMED_A)].iterrows():
            localities.name(ax, r, "residents", "per_member", leader=r["locality"] in LEADERS_A)
    charts.comma_axis(near_a.yaxis, 120_000, 20_000, "residents per member (thousands)", per=1000)
    charts.comma_axis(near_a.xaxis, NEAR_A, 200_000, "", per=1000)
    charts.break_x(near_a, far_a, "residents (thousands)", FAR_A, FAR_TICK_A, per=1000)
    charts.title_broken(near_a, "(a) Virginia localities with 100,000 or more residents")

    se = paths.read("localities_southeastern")
    se["per_member"] = se["residents"] / se["members"]
    se["arlington"] = se["locality"] == "Arlington"
    se = se.sort_values("arlington")
    se["color"] = [style.ARLINGTON if a else SE_COLORS[k] for a, k in zip(se["arlington"], se["kind"])]
    se["area"] = [charts.dot_area(a, profile) for a in se["arlington"]]
    charts.dots(far_b, se["residents"], se["per_member"], se["area"], se["color"])
    for _, r in se[se["locality"].isin(NAMED_B)].iterrows():
        charts.dot_label(far_b, r["residents"], r["per_member"], r["locality"], r["area"],
                         r["color"] if r["arlington"] else "black", bold=r["arlington"],
                         leader=r["locality"] in LEADERS_B,
                         first="above left")  # away from Lafayette, whose dot touches Arlington's
    charts.comma_axis(near_b.yaxis, 70_000, 10_000, "residents per member (thousands)", per=1000)
    charts.break_x_floor(near_b, far_b, "residents (thousands)", NEAR_B, FAR_B, 50_000, per=1000)
    charts.title_broken(near_b, "(b) southeastern localities with 150,000 to 300,000 residents")

    charts.dot_legend(fig, localities.LEGEND, profile)
    paths.save(fig, profile)
