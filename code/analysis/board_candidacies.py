"""Black candidacies for the Board, 1870-2026 -> figures/board_candidacies.pdf, .png

A timeline strip: one dot per Black candidate's run in a regular or special
election, at its year, filled if the candidate won and a ring if not;
runs in the same year stacked, earliest lowest. Primaries are in the table
and not drawn. A year with no dot is a year no source records a Black
candidacy. The 1932 rule marks the at-large Board.
"""
import pandas as pd

import charts
import members
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.BOARD_CANDIDACIES)
    runs = d[(d.claim == "candidacy") & (d.election != "primary")]
    assert len(runs), "no candidacy to draw - check the build"
    won = runs.won.astype(bool)
    shown = {label: (colour, filled) for key, (label, colour, filled) in style.CANDIDACY.items()
             if (won if key == "won" else ~won).any()}

    fig, ax = charts.figure(profile, aspect=style.STRIP)
    charts.events(ax, runs.year.to_numpy(), won.to_numpy(), style.CANDIDACY["won"][1], profile)
    charts.years(ax, 1870, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    charts.dot_legend(fig, shown, profile)
    paths.save(fig, "board_candidacies", profile)
