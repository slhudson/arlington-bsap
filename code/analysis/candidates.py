"""Black candidacies for the Board, 1870-2026 -> figures/candidates.pdf, .png

A timeline strip: one dot per Black candidate's run for a seat, at its
year, filled if the candidate won and a ring if not; runs in the same year
stacked, earliest lowest. A primary and the general election of the same
year are one run, with the general's outcome; a primary the candidate lost
is a run lost, since in Arlington the primary decides the seat. A special
election is its own run. A year with no dot is a year no source records a
Black candidacy. The 1932 rule marks the at-large Board.
"""

import charts
import members
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = paths.read("candidates")
    c = d[d.claim == "candidacy"]
    # A primary is drawn only where no general election follows it that year.
    followed = c.set_index(["name", "year"]).index.isin(
        c[c.election == "regular"].set_index(["name", "year"]).index)
    runs = c[(c.election != "primary") | ~followed]
    assert len(runs), "no candidacy to draw - check the build"
    won = runs.won.astype(bool)
    shown = {label: (colour, filled) for key, (label, colour, filled) in style.CANDIDACY.items()
             if (won if key == "won" else ~won).any()}

    fig, ax = charts.figure(profile, aspect=style.STRIP)
    charts.events(ax, runs.year.to_numpy(), won.to_numpy(), style.CANDIDACY["won"][1], profile)
    charts.years(ax, 1870, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    charts.dot_legend(fig, shown, profile)
    paths.save(fig, profile)
