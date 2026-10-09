"""Board seats by race and gender together, 1870-2026
-> figures/members_by_race_gender.pdf, .png

Before 1932 the three bands are the three district seats, Jefferson at the
bottom and Washington on top, south to north, each coloured by who held it
and named in the empty years after 1893; from 1932 a stacked step area of
seat-years, one band per combination, with the 1932 rule. Men take their
race's hue and women its darker shade (docs/figures.md).

PROTOTYPE, agreed with Sally on 9 October 2026 (branch members-race-gender):
the colours, the legend grid and the district names are drawn here and
belong in the style layer; the thread that finishes the figure moves them.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import charts
import members
import paths
import style

AT_LARGE_FROM = style.EXPANSION_YEAR
LANES = {"Jefferson": 0, "Arlington": 1, "Washington": 2}   # south at the bottom, north on top
NAMES_AT = 1912                                              # the empty years after Willson


def dark(c, k=0.6):
    r, g, b = mpl.colors.to_rgb(c)
    return mpl.colors.to_hex((r * k, g * k, b * k))


COLOURS = {
    "black_men":   ("Black men", style.RACE["black"][1]),
    "hisp_men":    ("Latino men", style.RACE["hisp"][1]),
    "hisp_women":  ("Latino women", dark(style.RACE["hisp"][1])),
    "white_men":   ("White men", style.SAND),
    "white_women": ("White women", style.SAND_LINE),
}
ORDER = ["white_women", "hisp_women", "black_men", "hisp_men", "white_men"]   # bottom to top
GRID = [["black_men", "hisp_men", "white_men"], [None, "hisp_women", "white_women"]]
KEY = {("White", "woman"): "white_women", ("Hispanic", "woman"): "hisp_women",
       ("Black", "man"): "black_men", ("Hispanic", "man"): "hisp_men", ("White", "man"): "white_men"}


def legend_grid(fig, grid, held):
    handles, labels = [], []
    for col in range(len(grid[0])):
        for row in grid:
            k = row[col]
            if k is None or k not in held:
                handles.append(Patch(facecolor="none", edgecolor="none"))
                labels.append("")
            else:
                handles.append(Patch(facecolor=COLOURS[k][1]))
                labels.append(COLOURS[k][0])
    fig.legend(handles=handles, labels=labels, loc="outside lower center", ncol=len(grid[0]))


for profile in style.PROFILES:
    style.apply(profile)
    d = paths.read("members_by_year")
    m = paths.read("members")
    fig, ax = charts.figure(profile)

    # From 1932: the stack.
    at_large = d[d.year >= AT_LARGE_FROM]
    pal = {k: COLOURS[k] for k in ORDER}
    held = [c for c in pal if d[c].sum() > 0]
    spans = charts.runs(at_large[list(pal)].notna().any(axis=1).to_numpy())
    bands = charts.series(at_large.fillna(0), {k: (k, c) for k, (_, c) in pal.items()}, held)
    charts.stacked_steps(ax, at_large.year.to_numpy(), bands, spans)

    # Before 1932: the district seats, read in months from the roster.
    for _, t in m[m.district != "at large"].iterrows():
        a, b = t.held_from / 12, min(t.held_to / 12, AT_LARGE_FROM)
        lane = LANES[t.district]
        ax.fill_between([a, b], lane, lane + 1, facecolor=COLOURS[KEY[(t.race, t.gender)]][1], linewidth=0)
    size = plt.rcParams["xtick.labelsize"] * style.DENSE_TICKS
    for name, lane in LANES.items():
        ax.text(NAMES_AT, lane + 0.5, f"{name} District", ha="center", va="center", fontsize=size, zorder=6)

    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    legend_grid(fig, GRID, held)
    paths.save(fig, profile)
