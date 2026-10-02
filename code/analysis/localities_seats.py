"""Seats and how they are elected, Arlington beside nineteen southeastern
cities of its size -> figures/localities_seats.pdf, .png

The share of council seats elected at large across, council seats up. Arlington in
its own colour; one name per cluster of cities that share a dot.
"""
import charts
import paths
import style

# One name per cluster; charts.place_labels() decides where each sits.
NAMED = {"Arlington", "Richmond", "Huntsville", "Baton Rouge", "Durham", "Knoxville",
         "Norfolk", "Little Rock", "Augusta", "Mobile", "Greensboro"}
# Named with a short line to the dot: too crowded to name beside it.
LEADERS = {"Huntsville", "Mobile", "Richmond", "Augusta", "Baton Rouge"}
CITY = style.LOCALITIES["city"][1]

for profile in style.PROFILES:
    style.apply(profile)

    d = paths.read("localities_southeastern")
    d["share"] = d["at_large_members"] / d["members"]
    d["arlington"] = d["locality"] == "Arlington"
    d = d.sort_values("arlington")
    d["color"] = [style.ARLINGTON if a else CITY for a in d["arlington"]]
    d["area"] = [charts.dot_area(a, profile) for a in d["arlington"]]

    fig, ax = charts.scatter(profile)
    charts.dots(ax, d["share"], d["members"], d["area"], d["color"])
    for _, r in d[d["locality"].isin(NAMED)].iterrows():
        charts.dot_label(ax, r["share"], r["members"], r["locality"], r["area"],
                         r["color"] if r["arlington"] else "black", bold=r["arlington"],
                         leader=r["locality"] in LEADERS)
    ax.set_xlim(-0.2, 1.05)
    ax.set_xticks([0, .25, .5, .75, 1])
    ax.set_xticklabels(["0%", "25", "50", "75", "100"])
    ax.set_xlabel("council seats elected at large")
    ax.set_ylim(0, 14)
    ax.set_yticks(range(0, 15, 2))
    ax.set_ylabel("council seats")

    charts.dot_legend(fig, {"Arlington": style.ARLINGTON, "southeastern city": CITY}, profile)
    paths.save(fig, profile)
