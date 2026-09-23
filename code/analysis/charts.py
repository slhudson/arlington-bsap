"""The chart types this report uses, with Urban's conventions already applied.

A figure script supplies data and says which chart it wants. It does not set a
colour, a size, a legend position or a margin: those are decisions the style
layer already made, and a script that makes them again is how a set of figures
drifts apart.

Four types, which is all the report needs:

    lines()         a series over time, labelled at its own right-hand end
    stacked_bars()  composition at intervals, counts or shares
    stacked_steps() composition over continuous years, with gaps preserved
    panels()        two of any of the above, side by side

Legends follow Urban: stretched horizontally across the top, outside the axes,
one row, in stacking order. Notes that belong to the document rather than the
image - sources, caveats - are not drawn here at all; they go in the LaTeX
caption. An annotation attached to a mark, such as the 1932 rule, does belong
in the panel, and rule() draws it.
"""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator, PercentFormatter

import style

THOUSANDS = FuncFormatter(lambda v, _: f"{int(v):,}")


def figure(ratio=0.62, profile=style.DEFAULT_PROFILE):
    """One panel at this profile's width."""
    fig, ax = plt.subplots(figsize=style.figsize(ratio, profile))
    return fig, ax


def panels(ratio=0.80, profile=style.DEFAULT_PROFILE):
    """Two panels side by side, sharing nothing but the figure.

    Side by side rather than stacked because a composition panel needs to be
    taller than it is wide when its early values are small.
    """
    fig, axes = plt.subplots(1, 2, figsize=style.figsize(ratio, profile))
    return fig, axes


def lines(ax, x, series):
    """One line per series. series is an ordered {label: (values, colour)}.

    Labels are not drawn here: see end_labels(), which has to run after the
    axis limits are set.
    """
    for label, (values, color) in series.items():
        ax.plot(x, values, color=color, marker="o", zorder=3, label=label)


def end_labels(ax, x, series, gap=0.015):
    """Name each line at its own right-hand end, with its final value.

    Urban prefers this to a legend where the lines allow it: "directly label
    the data series ... at the far right of the graph, slightly outside the
    graph space, but left-aligned."

    Drawn in data coordinates inside the axes, not as an annotation offset
    beyond them. Constrained layout reserves room for things it knows about -
    ticks, labels, titles - and an annotation hanging outside the axes is not
    one of them, so it silently runs off the page. Call this after the x limit
    is set, and leave room in that limit.
    """
    lo, hi = ax.get_xlim()
    at = float(np.asarray(x)[-1]) + (hi - lo) * gap
    for label, (values, color) in series.items():
        last = float(np.asarray(values)[-1])
        ax.text(at, last, f"{label}\n{int(round(last)):,}", color=color,
                ha="left", va="center", linespacing=1.3,
                fontsize=plt.rcParams["font.size"])


def stacked_bars(ax, x, series, width=7, residual=None):
    """Stacked bars. series is an ordered {label: (values, colour)}.

    Urban sets bar width at about twice the gap between bars; with decade
    spacing that is a width of 6.7 years, which is what the default gives.
    """
    bottom = np.zeros(len(x))
    for label, (values, color) in series.items():
        v = np.asarray(values, dtype=float)
        ax.bar(x, v, bottom=bottom, width=width, color=color, label=label)
        bottom = bottom + v
    if residual is not None:
        label, values, color, edge = residual
        ax.bar(x, values, bottom=bottom, width=width, color=color,
               edgecolor=edge, linewidth=0.4, hatch="////", label=label)


def runs(reported):
    """Index ranges of consecutive reported years, as (first, last) inclusive.

    A stacked area drawn straight through a year the source does not report
    invents a value for it. Filling each run separately keeps a gap a gap.
    """
    out, start = [], None
    for i, ok in enumerate(reported):
        if ok and start is None:
            start = i
        if (not ok or i == len(reported) - 1) and start is not None:
            out.append((start, i if ok else i - 1))
            start = None
    return out


def stacked_steps(ax, years, series, spans):
    """Stacked step-area; each year's value spans [year, year + 1)."""
    years = np.asarray(years)
    cum = np.zeros(len(years))
    for label, (values, color) in series.items():
        top = cum + np.asarray(values, dtype=float)
        first = True
        for a, b in spans:
            xs = np.append(years[a:b + 1], years[b] + 1)
            lo = np.append(cum[a:b + 1], cum[b])
            hi = np.append(top[a:b + 1], top[b])
            ax.fill_between(xs, lo, hi, step="post", facecolor=color,
                            edgecolor="white", linewidth=0.3,
                            label=label if first else None)
            first = False
        cum = top


def legend(fig, entries):
    """One legend for the whole figure, across the top, one row.

    entries is an ordered {label: colour}, in stacking order, which is the
    order Urban asks a legend to follow. Patches are built here rather than
    collected from the axes so that a figure with two panels showing the same
    groups gets one legend rather than two.
    """
    handles = [Patch(facecolor=c, label=l) for l, c in entries.items()]
    fig.legend(handles=handles, labels=list(entries), loc="outside upper center",
               ncol=len(entries))


def rule(ax, year=style.EXPANSION_YEAR, note=style.EXPANSION_NOTE, y=0.97):
    """A dated vertical rule with its annotation inside the panel.

    The note is an annotation attached to a mark, not a source note, so it
    stays in the image. It is drawn once per figure, not once per panel.
    """
    ax.axvline(year, zorder=5, **style.EXPANSION_LINE)
    ax.text(year + 4, y, note, transform=ax.get_xaxis_transform(),
            ha="left", va="top", zorder=6,
            fontsize=plt.rcParams["font.size"])


def years(ax, first, last, step=10, rotate=False, label="census year",
          headroom=0.0):
    """A year axis. headroom is extra span past `last`, as a fraction, for
    anything drawn at the right-hand end - end labels, mainly."""
    span = last - first
    ax.set_xlim(first - span * 0.03, last + span * (0.03 + headroom))
    ax.set_xticks(range(first, last + 1, step))
    if rotate:
        ax.tick_params(axis="x", labelrotation=90)
        ax.set_xlabel("")
    else:
        ax.set_xlabel(label)


def counts(ax, top, step, label="residents"):
    """A count axis ending on a round tick rather than just clear of the data."""
    ax.set_ylim(0, top)
    ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.yaxis.set_major_formatter(THOUSANDS)
    ax.set_ylabel(label)


def shares(ax, label="share of residents"):
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
    ax.set_ylabel(label)


def seats(ax, label="board seats"):
    ax.set_ylim(0, 5)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_ylabel(label)
    ax.grid(axis="y", color="white", alpha=0.8, linewidth=0.8)
    ax.set_axisbelow(False)          # seat guides read over the fills
