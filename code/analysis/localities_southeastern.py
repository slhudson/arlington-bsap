"""Residents per member, Arlington beside nineteen southeastern cities of
its size -> figures/localities_southeastern.pdf, .png

Every city of the Richmond charter review's Appendix E: residents across,
residents per member of the council up. Arlington in its own colour; a name
only where the names would not collide: one per cluster.
"""
import charts
import paths
import style

# One name per cluster of cities that sit together; charts.place_labels() decides where.
NAMED = {"Arlington", "Huntsville", "Durham", "Greensboro", "Norfolk", "Richmond", "Mobile",
         "Baton Rouge", "Knoxville"}
# Named with a short line to the dot: too close to its neighbours to name beside it.
LEADERS = {"Mobile", "Knoxville", "Baton Rouge"}
CITY = style.LOCALITIES["city"][1]

for profile in style.PROFILES:
    style.apply(profile)

    d = paths.read("localities_southeastern")
    d["per_member"] = d["residents"] / d["members"]
    d["arlington"] = d["locality"] == "Arlington"
    d = d.sort_values("arlington")
    d["color"] = [style.ARLINGTON if a else CITY for a in d["arlington"]]
    d["area"] = [charts.dot_area(a, profile) for a in d["arlington"]]

    fig, ax = charts.scatter(profile)
    charts.dots(ax, d["residents"], d["per_member"], d["area"], d["color"])
    for _, r in d[d["locality"].isin(NAMED)].iterrows():
        charts.dot_label(ax, r["residents"], r["per_member"], r["locality"], r["area"],
                         r["color"] if r["arlington"] else "black", bold=r["arlington"],
                         leader=r["locality"] in LEADERS)
    charts.comma_axis(ax.xaxis, 300_000, 50_000, "residents")
    charts.comma_axis(ax.yaxis, 60_000, 10_000, "residents per member")

    charts.dot_legend(fig, {"Arlington": style.ARLINGTON, "southeastern city": CITY}, profile)
    paths.save(fig, profile)
