"""The chart types this report uses, with the conventions in style applied.

A figure script supplies data and says which chart it wants; it does not
set a colour, a size, a legend position or a margin. The reasoning behind
each placement is in docs/figures.md.

    series()        a {label: (values, colour)} from a table and a frame
    lines()         a series over time
    stacked_bars()  composition at intervals
    stacked_steps() composition over continuous years, with gaps preserved
    panels()        two of the above, side by side
    end_label()     a line named at its last point, inside the axes
    legend()        one legend for the figure, one row, below the axes
    rule()          a dated vertical rule with its note above the frame
    fit()           the figure's size and margins, called by paths.save()
"""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import (FixedLocator, FuncFormatter, MultipleLocator,
                               PercentFormatter)

import style

THOUSANDS = FuncFormatter(lambda v, _: f"{int(v):,}")


def figure(profile=style.DEFAULT_PROFILE, of_width=1.0):
    """One panel at this profile's width. The height is solved by fit().
    `of_width` is the fraction of that width to take, for the few figures
    too narrow to fill the page; pass a name from style, never a number."""
    fig, ax = plt.subplots(figsize=style.figsize(profile, of_width))
    return fig, ax


def panels(profile=style.DEFAULT_PROFILE):
    """Two panels side by side."""
    fig, axes = plt.subplots(1, 2, figsize=style.figsize(profile))
    return fig, axes


def series(frame, table, keys=None):
    """{label: (values, colour)} for the columns of `frame` named in `table`,
    a style table of column -> (label, colour), in its order; `keys` narrows
    it."""
    return {label: (frame[k].to_numpy(), colour) for k, (label, colour) in table.items()
            if keys is None or k in keys}


def lines(ax, x, series, marker=True):
    """One line per series. series is an ordered {label: (values, colour)}.
    A marker on every point unless marker=False."""
    for label, (values, color) in series.items():
        ax.plot(x, values, color=color, marker="o" if marker else None, zorder=3, label=label)


def age_band(ax, years, low, high, spans, color):
    """The youngest-to-oldest span of each year's Board as a step area; each
    year's value spans [year, year + 1). NaN years are gaps, left open."""
    years = np.asarray(years)
    for a, b in spans:
        xs = np.append(years[a:b + 1], years[b] + 1)
        ax.fill_between(xs, np.append(low[a:b + 1], low[b]), np.append(high[a:b + 1], high[b]),
                        step="post", facecolor=color, edgecolor="none", zorder=1)


def strokes(ax, segments, color, alpha=1.0):
    """One straight stroke per (x0, y0, x1, y1), over the band."""
    for x0, y0, x1, y1 in segments:
        ax.plot([x0, x1], [y0, y1], color=color, alpha=alpha, solid_capstyle="butt", zorder=3)


def end_label(ax, x, y, text, color, where="left", gap=0.012):
    """Name a line at (x, y), inside the axes: `left` ends the text at the
    point; `above` and `below` sit it over or under the point, right-aligned.
    gap is the offset as a fraction of the axis."""
    if where == "above":
        lo, hi = ax.get_ylim()
        x, y, ha, va = x, y + (hi - lo) * gap, "right", "bottom"
    elif where == "below":
        lo, hi = ax.get_ylim()
        x, y, ha, va = x, y - (hi - lo) * gap, "right", "top"
    else:
        lo, hi = ax.get_xlim()
        x, y, ha, va = x - (hi - lo) * gap, y, "right", "center"
    ax.text(x, y, text, color=color, ha=ha, va=va, linespacing=1.25,
            fontsize=plt.rcParams["font.size"])


def stacked_bars(ax, x, series, width=7):
    """Stacked bars. series is an ordered {label: (values, colour)} from the
    axis upward. No texture."""
    bottom = np.zeros(len(x))
    for label, (values, color) in series.items():
        v = np.asarray(values, dtype=float)
        ax.bar(x, v, bottom=bottom, width=width, color=color, label=label)
        bottom = bottom + v


def off_scale(ax, series_x, series_y, color, top):
    """Mark where a series leaves the top of the axis with a triangle at the
    crossing, interpolated between the points either side. Returns the x of
    the crossing, or None if the series never leaves."""
    x = np.asarray(series_x, dtype=float)
    y = np.asarray(series_y, dtype=float)
    i = int(np.argmax(y > top))
    if i == 0:
        return None
    frac = (top - y[i - 1]) / (y[i] - y[i - 1])
    at = x[i - 1] + frac * (x[i] - x[i - 1])
    ax.plot([at], [top], marker="^",
            markersize=plt.rcParams["lines.markersize"] * 2.6,
            color=color, clip_on=False, zorder=5)
    return at


def runs(reported):
    """Index ranges of consecutive reported years, as (first, last) inclusive."""
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
        for n, (a, b) in enumerate(spans):
            xs = np.append(years[a:b + 1], years[b] + 1)
            lo = np.append(cum[a:b + 1], cum[b])
            hi = np.append(top[a:b + 1], top[b])
            ax.fill_between(xs, lo, hi, step="post", facecolor=color,
                            edgecolor="white", linewidth=0.3,
                            label=label if n == 0 else None)
        cum = top


def fit(fig):
    """Size and place this figure: the canvas is the profile's width, the
    plot is style.PLOT_ASPECT times as wide as tall, and style.MARGIN of
    white surrounds the ink on all four sides. Iterated, because the height
    depends on furniture that is only measurable once drawn."""
    def ink(fig):
        """The drawn extent in figure fractions, from the rendered pixels."""
        fig.canvas.draw()
        a = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        mark = (a < 250).any(axis=2)
        cols, rows = np.where(mark.any(axis=0))[0], np.where(mark.any(axis=1))[0]
        if not len(cols):
            return 0.0, 1.0, 0.0, 1.0
        h, w = mark.shape
        return (cols.min() / w, (cols.max() + 1) / w,
                1 - (rows.max() + 1) / h, 1 - rows.min() / h)

    for _ in range(8):
        ix0, ix1, iy0, iy1 = ink(fig)
        boxes = [ax.get_position() for ax in fig.axes]
        if not boxes:
            return
        w_in, h_in = fig.get_size_inches()
        m_in = style.MARGIN * w_in
        lo, hi = min(b.x0 for b in boxes), max(b.x1 for b in boxes)
        y0, y1 = min(b.y0 for b in boxes), max(b.y1 for b in boxes)
        plot_w = (w_in - 2 * m_in) - (lo - ix0) * w_in - (ix1 - hi) * w_in
        furniture = (iy1 - iy0) * h_in - (y1 - y0) * h_in
        want = plot_w / style.PLOT_ASPECT + furniture + 2 * m_in
        if abs(want - h_in) < 0.002:
            break
        fig.set_size_inches(w_in, want)

    ix0, ix1, iy0, iy1 = ink(fig)
    w_in, h_in = fig.get_size_inches()
    m = style.MARGIN
    boxes = [(ax, ax.get_position()) for ax in fig.axes]
    lo, hi = min(b.x0 for _, b in boxes), max(b.x1 for _, b in boxes)

    left, right = m + (lo - ix0), 1 - m - (ix1 - hi)
    if left >= right:
        raise AssertionError(
            "this figure's labels reach across the whole canvas - they would "
            "leave no room for a plot inside the margins")
    fig.set_layout_engine("none")
    scale = (right - left) / (hi - lo)
    for ax, b in boxes:
        ax.set_position([left + (b.x0 - lo) * scale, b.y0,
                         b.width * scale, b.height])

    # Height from the placed width.
    boxes = [(ax, ax.get_position()) for ax in fig.axes]
    y0 = min(b.y0 for _, b in boxes)
    y1 = max(b.y1 for _, b in boxes)
    h_in = fig.get_size_inches()[1]
    want_h = ((right - left) * w_in / style.PLOT_ASPECT) / h_in
    if y1 - y0 > 1e-9:
        k = want_h / (y1 - y0)
        for ax, b in boxes:
            ax.set_position([b.x0, y0 + (b.y0 - y0) * k, b.width, b.height * k])

    # Re-place the legend under the plot at its final size: centred on the
    # plot region, not on the canvas. Centring on the canvas counts the
    # y-axis label and tick labels as part of what to centre under, which
    # pushes the legend left of the bars it names.
    if fig.legends:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        low = min(ax.get_tightbbox(r).y0 for ax in fig.axes) / fig.bbox.height
        gap = style.LEGEND_GAP / fig.get_size_inches()[1]
        placed = [ax.get_position() for ax in fig.axes]
        mid = (min(p.x0 for p in placed) + max(p.x1 for p in placed)) / 2
        for lg in fig.legends:
            b = lg.get_window_extent(r).transformed(fig.transFigure.inverted())
            lg.set_bbox_to_anchor((mid - b.width / 2, low - gap - b.height,
                                   b.width, b.height),
                                  transform=fig.transFigure)

    # Vertical margins, measured from the rendered white; height is changed
    # by adding inches, holding every element's size in inches.
    for _ in range(6):
        h_in = fig.get_size_inches()[1]
        m_in = style.MARGIN * w_in
        _, _, iy0, iy1 = ink(fig)
        short_bottom = m_in - iy0 * h_in
        short_top = m_in - (1 - iy1) * h_in
        if abs(short_bottom) < 0.005 and abs(short_top) < 0.005:
            break
        new_h = max(h_in + short_bottom + short_top, 1.0)
        k = h_in / new_h
        rise = short_bottom / new_h
        fig.set_size_inches(w_in, new_h, forward=True)
        for ax in fig.axes:
            b = ax.get_position()
            ax.set_position([b.x0, b.y0 * k + rise, b.width, b.height * k])
        for lg in fig.legends:
            b = lg.get_window_extent().transformed(fig.transFigure.inverted())
            lg.set_bbox_to_anchor((b.x0, b.y0 * k + rise, b.width, b.height * k),
                                  transform=fig.transFigure)


def legend(fig, entries, ncol=None):
    """One legend for the whole figure, below it, one row unless ncol is
    given. entries is ordered {label: colour} or the {label: (values, colour)}
    a chart took."""
    colors = [v if isinstance(v, str) else v[1] for v in entries.values()]
    fig.legend(handles=[Patch(facecolor=c) for c in colors], labels=list(entries),
               loc="outside lower center", ncol=ncol or len(entries))


def rule(ax, year=style.EXPANSION_YEAR, note=style.EXPANSION_NOTE):
    """A dated vertical rule, with its note above the frame; note=None for
    the rule alone."""
    ax.axvline(year, zorder=5, **style.EXPANSION_LINE)
    if note is None:
        return
    ax.plot([year, year], [1.0, 1.045], transform=ax.get_xaxis_transform(),
            clip_on=False, zorder=5, **style.EXPANSION_LINE)
    ax.text(year, 1.06, note, transform=ax.get_xaxis_transform(),
            ha="center", va="bottom", zorder=6, clip_on=False,
            fontsize=plt.rcParams["font.size"])


def years(ax, first, last, step=10, label="census year", minor=10, through=None,
          bars=None):
    """A year axis labelled every `step` years, anchored on `last`, with an
    unlabelled tick every `minor` years between. `through` is where the axis
    ends; otherwise a little clear of `last`. `bars` is the width the bars
    on this axis were drawn at: the limits then clear half a bar, so that
    the first and last are drawn whole rather than sliced by the frame."""
    span = last - first
    pad = span * 0.03
    if bars:
        pad = max(pad, bars / 2 + span * 0.01)
    ax.set_xlim(first - pad, through or last + pad)
    major = sorted(range(last, first - 1, -step))
    ax.set_xticks(major)
    if minor and minor < step:
        ax.xaxis.set_minor_locator(
            FixedLocator([y for y in range(first, last + 1, minor) if y not in major]))
    ax.set_xlabel(label)


def counts(ax, top, step, label="residents", minor=None):
    """A count axis from 0 to `top`, labelled every `step`, with a lighter
    gridline every `minor` if given."""
    ax.set_ylim(0, top)
    ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.yaxis.set_major_formatter(THOUSANDS)
    ax.set_ylabel(label)
    if minor:
        ax.yaxis.set_minor_locator(MultipleLocator(minor))
        ax.grid(axis="y", which="minor", color=plt.rcParams["grid.color"],
                linewidth=plt.rcParams["grid.linewidth"] * 0.7, alpha=1.0)


def ages(ax, low, high, step=10, label="age"):
    """An age axis from `low` to `high`, both round ticks, labelled every
    `step` years."""
    ax.set_ylim(low, high)
    ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.set_ylabel(label)


def shares(ax, label="share of residents"):
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
    ax.set_ylabel(label)


def seats(ax, label="board members"):
    ax.set_ylim(0, 5)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_ylabel(label)
    ax.grid(axis="y", color="white", alpha=0.8, linewidth=0.8)
    ax.set_axisbelow(False)          # guides over the fills
