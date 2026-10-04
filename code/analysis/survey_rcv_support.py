"""How the voters the 2025 post-election survey reached answered whether they
would want ranked choice voting used again for the County Board, by whether
they own or rent, by gender and by age.

The whole five-point scale, in the hues the satisfaction survey's agreement
scale uses. Only the cuts whose every answer clears the survey's small-cell
floor appear: race is in survey_rcv_by_race, where the answers are too few to
break out and the share supporting carries its margin instead.
"""
import charts
import paths
import style

QUESTION = "Ranked in future"
GROUPS = {"home": ("Homeownership", ["Homeowner", "Renter"]),
          "gender": ("Gender", ["Female", "Male"]),
          "age": ("Age band", ["45-64", "65+"])}


def main():
    style.apply()
    d = paths.read("survey_rcv")
    d = d[(d.question == QUESTION) & (d.kind == "answer")]
    labels, rows, blocks = [], [], {}
    for heading, (group, categories) in GROUPS.items():
        blocks[heading] = len(categories)
        labels += categories
        for category in categories:
            cell = d[(d.group == group) & (d.category == category)]
            rows.append(cell.set_index("answer").share.reindex(style.SUPPORT))
    entries = {label: ([100 * r.loc[k] for r in rows], colour)
               for k, (label, colour) in style.SUPPORT.items()}
    fig, ax = charts.figure()
    charts.hstacked_bars(ax, labels, entries, groups=blocks)
    charts.share_axis(ax, "share of respondents answering")
    charts.legend(fig, entries, ncol=3)
    paths.save(fig)


if __name__ == "__main__":
    main()
