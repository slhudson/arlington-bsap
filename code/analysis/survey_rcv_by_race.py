"""The share of the 2025 survey's voters who would want ranked choice voting
used again for the County Board, by race and ethnicity, with the margin the
survey's own weights imply.

The five-point answers are too few to publish for every group but White, so
this figure shows the share supporting - strongly or somewhat - which the
survey reports for all of them. The whiskers are why: thirty-seven Hispanic
respondents behave like twenty-three once the weights are counted, and carry
a margin of twenty points. An interval is held inside the scale, so a bar
near either end shows a short whisker on that side rather than one running
off the frame.
"""
import charts
import paths
import style

QUESTION = "Ranked in future"
ROLLUP = "Support (strongly or somewhat)"
GROUP = "Race and ethnicity"
CATEGORIES = ["White", "Black", "Hispanic", "Asian", "Other race"]
EVERYONE = "All respondents"


def main():
    style.apply()
    answers = paths.read("survey_rcv")
    answers = answers[(answers.question == QUESTION) & (answers.answer == ROLLUP)]
    margins = paths.read("survey_rcv_precision")

    def share(group, category):
        row = answers[(answers.group == group) & (answers.category == category)]
        margin = margins[(margins.group == group) & (margins.category == category)]
        return 100 * row.share.iloc[0], margin.margin_points.iloc[0]

    labels = CATEGORIES + ["all respondents"]
    pairs = [share(GROUP, c) for c in CATEGORIES] + [share(EVERYONE, EVERYONE)]
    values = [v for v, _ in pairs]
    fig, ax = charts.figure()
    charts.hbars(ax, labels, values, style.SURVEY_SHARE[1])
    charts.hwhiskers(ax, range(len(labels)), values, [m for _, m in pairs], style.DARK)
    charts.share_axis(ax, "would want ranked choice voting used again", top=100, step=20)
    paths.save(fig)


if __name__ == "__main__":
    main()
