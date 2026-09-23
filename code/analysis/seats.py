"""Drawing a seat series that has gaps in it.

Both seat charts - board_gender and board_race - face the same problem: the
source does not report every year, and a stacked area drawn straight through a
missing year invents a value for it. The fix is to fill each unbroken stretch
of reported years separately, so a gap stays a gap.

It lives here rather than in either figure because writing it twice is how the
two drift apart, and because a figure script should read as a description of
what it draws.
"""
import numpy as np


def runs(reported):
    """Index ranges of consecutive reported years, as (first, last) inclusive.

    `reported` is a boolean per row, normally df[col].notna().
    """
    out, start = [], None
    for i, ok in enumerate(reported):
        if ok and start is None:
            start = i
        if (not ok or i == len(reported) - 1) and start is not None:
            out.append((start, i if ok else i - 1))
            start = None
    return out


def stacked_step(ax, years, columns, colors, labels, spans):
    """Stacked step-area of seat counts; each year's value spans [year, year+1).

    `columns` is a list of arrays, stacked in order from the axis upward.
    `spans` comes from runs(). Only the first span of each series is labelled,
    so a series broken into three pieces still gets one legend entry.
    """
    cum = np.zeros(len(years))
    for values, color, label in zip(columns, colors, labels):
        top = cum + values
        first = True
        for a, b in spans:
            x = np.append(years[a:b + 1], years[b] + 1)
            ax.fill_between(x, np.append(cum[a:b + 1], cum[b]),
                            np.append(top[a:b + 1], top[b]), step="post",
                            facecolor=color, edgecolor="white", linewidth=0.3,
                            label=label if first else None)
            first = False
        cum = top
    return cum


def frame(ax, style):
    """The 0-5 seat frame both charts share: scale, guides and the 1932 rule."""
    from matplotlib.ticker import MultipleLocator
    ax.set_xlim(1866, 2027)
    ax.set_ylim(0, 5)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_xticks(range(1880, 2021, 20))
    ax.set_ylabel("board seats")
    ax.set_xlabel("year")
    ax.set_axisbelow(False)                      # seat guides sit over the fills
    ax.grid(axis="y", color="white", alpha=0.7, lw=0.5)
    ax.axvline(style.EXPANSION_YEAR, zorder=5, **style.EXPANSION_LINE)
    ax.plot([style.EXPANSION_YEAR] * 2, [1.0, 1.10],
            transform=ax.get_xaxis_transform(), clip_on=False, zorder=5,
            **style.EXPANSION_LINE)
    ax.text(1936, 1.03, style.EXPANSION_NOTE_SEATS, transform=ax.get_xaxis_transform(),
            ha="left", va="bottom", fontsize=style.NOTE)
    style.despine(ax)
