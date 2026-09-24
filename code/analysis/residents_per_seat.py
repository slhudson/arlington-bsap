"""Residents and residents per Board seat, 1870-2020 -> figures/residents_per_seat.pdf, .png

Two series on one linear axis. Both are counts of people, so the vertical
distance between them means the same thing everywhere on the page - which a
second y-axis would not give: the Board held three seats before 1932 and five
after, so no single right-hand scale is right for the whole series, and picking
one decides which era looks like the exception.

Each line is named where it runs, on one line, with its final value. Urban puts
such a label at the far right just outside the plot; a label long enough to be
readable needs enough headroom past 2020 to visibly stretch the axis, which
distorts the series to make room for its own caption.

"Seat", not "member". The denominator is seats that exist - three through
1931 and five after - not members serving, and the two differ in 1873 and
1990, when a seat sat vacant (seats-that-exist in docs/questions.csv). "Per
member" reads better and would claim something the figure does not measure.

A cube-root-law benchmark was drawn and removed. The law is descriptive,
not normative, and its reference class is national parliaments; as drawn it
implied a 62-member Board. Peer localities would be the right comparison if
the report wants one (peer-localities in docs/questions.csv).
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.RESIDENTS)[["year", "total", "residents_per_seat"]].dropna()
    series = {
        "total population": (d["total"], style.SERIES_COLORS["population"]),
        "residents per Board seat": (d["residents_per_seat"],
                                       style.SERIES_COLORS["per_seat"]),
    }

    fig, ax = charts.figure(profile)
    charts.lines(ax, d["year"], series)
    charts.counts(ax, 250000, 50000)
    # Decades collide at this width, so labels every twenty years with an
    # unlabelled tick at each census between. The headroom is for the two end
    # labels, which sit inside the axes beside the points they name.
    charts.years(ax, 1870, 2020, step=20)

    # Each label goes where its own line leaves room, not by one rule.
    #
    # Population has empty space behind its last point, so the label sits to
    # its left, right-aligned so the text ends at the point. The gap is wider
    # than the default because the line climbs steeply into 2020 and would
    # otherwise cross the value beneath the name.
    #
    # Residents per seat has the population line only just above it and its own
    # line running under where a left-hand label would sit, so that label goes
    # directly over its point instead - and over three lines, because one long
    # line would reach back to 1985 for no reason. The block then matches the
    # shape of the population label rather than cutting across the panel.
    last = d.iloc[-1]
    charts.end_label(ax, 2020, last["total"],
                     f"2020 population:\n{int(last['total']):,}",
                     style.SERIES_COLORS["population"], gap=0.035)
    charts.end_label(ax, 2020, last["residents_per_seat"],
                     f"2020 residents\nper Board seat:\n"
                     f"{int(round(last['residents_per_seat'])):,}",
                     style.SERIES_COLORS["per_seat"], where="above", gap=0.02)

    charts.rule(ax)
    paths.save(fig, "residents_per_seat", profile)
