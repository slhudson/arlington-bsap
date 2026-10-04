"""Support for ranked choice voting, and awareness that it would be used,
among the voters the 2025 post-election survey reached, by whether they own
or rent and by race and ethnicity.

A bar the survey's own preparers marked as resting on too few respondents is
drawn faded, and the caption gives its respondents; dropping those cells
would leave the figure silent on every group but White and Black
(docs/survey_rcv.md).
"""
import charts
import paths
import style

GROUPS = {"home": ("Homeownership", ["Homeowner", "Renter"]),
          "race and ethnicity": ("Race and ethnicity",
                                 ["White", "Black", "Hispanic", "Asian", "Other race"])}
MEASURE = "support"


def main():
    style.apply()
    d = paths.read("survey_rcv")
    d = d[d.measure == MEASURE]
    labels, values, alphas, blocks = [], [], [], {}
    for heading, (group, categories) in GROUPS.items():
        rows = d[d.group == group].set_index("category").reindex(categories)
        blocks[heading] = len(categories)
        labels += categories
        values += (100 * rows.share).tolist()
        alphas += [style.THIN_ALPHA if t else 1.0 for t in rows.thin]
    fig, ax = charts.figure()
    charts.hbars(ax, labels, values, style.SURVEY_SHARE[1], blocks, alphas)
    charts.share_axis(ax, "would support ranked choice voting again", top=100, step=20)
    paths.save(fig)


if __name__ == "__main__":
    main()
