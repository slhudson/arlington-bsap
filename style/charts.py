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
from matplotlib.ticker import (FixedLocator, FuncFormatter, MultipleLocator,
                               PercentFormatter)

import style

THOUSANDS = FuncFormatter(lambda v, _: f"{int(v):,}")


def figure(profile=style.DEFAULT_PROFILE):
    """One panel at this profile's width. The height is solved by fit()."""
    fig, ax = plt.subplots(figsize=style.figsize(profile))
    return fig, ax


def panels(profile=style.DEFAULT_PROFILE):
    """Two panels side by side, sharing nothing but the figure.

    Side by side rather than stacked because a composition panel needs to be
    taller than it is wide when its early values are small.
    """
    fig, axes = plt.subplots(1, 2, figsize=style.figsize(profile))
    return fig, axes


def lines(ax, x, series, marker=True):
    """One line per series. series is an ordered {label: (values, colour)}.

    A marker on every point, unless the series is annual: ninety dots on a
    line are noise, and a point is worth marking when the points are the
    observations - one per census, one per presidential election.

    Labels are not drawn here: see end_labels(), which has to run after the
    axis limits are set.
    """
    for label, (values, color) in series.items():
        ax.plot(x, values, color=color, marker="o" if marker else None, zorder=3, label=label)


def label_line(ax, x, y, text, color, ha="left", va="center"):
    """Name a line where it runs, on one line of text, inside the axes.

    Urban puts line labels at the far right, just outside the plot. That needs
    headroom past the last data point, and a label long enough to be readable
    needs enough of it to visibly stretch the axis - which distorts the series
    to buy room for its own caption. Putting the label in the space the chart
    already has costs nothing.

    One line, not two. A label wrapped over two or three lines is read rather
    than glanced at, which is the opposite of what direct labelling is for.
    """
    ax.text(x, y, text, color=color, ha=ha, va=va, linespacing=1.25,
            fontsize=plt.rcParams["font.size"])


def end_label(ax, x, y, text, color, where="left", gap=0.012):
    """Name a line at the point it describes, on whichever side has room.

    Never to the right of the last point: that needs headroom the axis does not
    otherwise want, and buying room for a caption by stretching the series is
    the wrong trade. The space inside the plot is already there.

    Which side depends on the line, not on a rule. `left` right-aligns the text
    so it ends at the point, which suits a line with empty space behind it.
    `above` sits it over the point, still right-aligned so it ends there rather
    than straddling it, which suits a line running close under where a
    left-hand label would go. `below` is the same under the point, for a line
    that arrives at its last point from above. Wrap the name over as many lines as it
    takes to stay clear.
    """
    if where == "above":
        lo, hi = ax.get_ylim()
        label_line(ax, x, y + (hi - lo) * gap, text, color, ha="right", va="bottom")
    elif where == "below":
        lo, hi = ax.get_ylim()
        label_line(ax, x, y - (hi - lo) * gap, text, color, ha="right", va="top")
    else:
        lo, hi = ax.get_xlim()
        label_line(ax, x - (hi - lo) * gap, y, text, color, ha="right", va="center")


def stacked_bars(ax, x, series, width=7):
    """Stacked bars. series is an ordered {label: (values, colour)} from the
    axis upward.

    Every band is a member of the stack, including a residual. A residual is
    not drawn last and on top: where it is a kind of one of the other groups,
    sitting it above them splits that population in two and makes it read as
    smaller than it is.

    No band is textured. A single hatched band among flat ones reads as
    emphasis, and a residual is the last thing that should be emphasised.

    Urban sets bar width at about twice the gap between bars; with decade
    spacing that is a width of 6.7 years, which is what the default gives.
    """
    bottom = np.zeros(len(x))
    for label, (values, color) in series.items():
        v = np.asarray(values, dtype=float)
        ax.bar(x, v, bottom=bottom, width=width, color=color, label=label)
        bottom = bottom + v


def off_scale(ax, series_x, series_y, color, top):
    """Mark where a series leaves the top of the axis.

    For a series on scale for part of its range and far off it for the rest:
    plot it, let the axis clip it, and put a triangle where it exits, so the
    exit is a statement rather than a line that stops for no reason.

    A triangle, not an arrow with a shaft. A shaft is a second stroke at its
    own angle, which reads as another series; a marker sits on the line's own
    last point and adds nothing to argue with. Where the series goes is the
    caption's business - the legend has already named the colour.

    Returns the year it crosses, interpolated between the two censuses either
    side, so nothing is written in by hand.
    """
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


def fit(fig):
    """Size and place this figure so the set looks like a set.

    Three things want to be constant across the figures and only two can be:
    the canvas width, the margin of white around the edge, and the plot region.
    They are tied together - canvas = margin + labels + plot + margin - and the
    label block is not the same width in every figure, because "0" to "5" on a
    seat chart is narrower than "250,000" on a population one, by about a third
    of an inch.

    The canvas width and the margin are held; the plot absorbs the difference.
    Plots come out within about 7 per cent of each other in size and identical
    in shape, which is invisible between figures that never sit side by side,
    and it costs nothing downstream: every figure is still exactly one text
    width, so nothing that places them has to know about this.

    Held: the canvas is the profile's width; style.MARGIN of white on all four
    sides, the same number of inches on each; and a plot style.PLOT_ASPECT
    times as wide as it is tall.

    Measured to ink rather than to the frame, at every edge. A frame-based
    margin looks wrong because what a reader sees as the edge of a figure is
    where its ink starts, and the ink reaches different distances past the
    frame on each side - the y labels a long way on the left, the last year's
    label half its own width on the right, nothing much at the top.

    Iterated, because a figure's height is its plot plus its furniture, the
    furniture is only measurable once drawn, and resizing can reflow a legend
    onto another row and change it again. Width and height are solved together
    each pass: solving the height first and placing afterwards leaves the
    aspect short, because the placement widens the plot after the height has
    been fixed to the narrower one.

    Called by paths.save(), so a figure script never has to remember any of it.
    """
    def ink(fig):
        """The figure's drawn extent, in figure fractions, from the pixels.

        Measured off the rendered image rather than from get_tightbbox, which
        counts the figure's own background patch and so always answers "the
        whole canvas". What is wanted here is where the marks are.
        """
        fig.canvas.draw()
        a = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        mark = (a < 250).any(axis=2)
        cols, rows = np.where(mark.any(axis=0))[0], np.where(mark.any(axis=1))[0]
        if not len(cols):
            return 0.0, 1.0, 0.0, 1.0
        h, w = mark.shape
        # Rows come down the image and figure fractions go up it.
        return (cols.min() / w, (cols.max() + 1) / w,
                1 - (rows.max() + 1) / h, 1 - rows.min() / h)

    for _ in range(8):
        ix0, ix1, iy0, iy1 = ink(fig)
        boxes = [ax.get_position() for ax in fig.axes]
        if not boxes:
            return
        w_in, h_in = fig.get_size_inches()
        m_in = style.MARGIN * w_in                     # the same white everywhere
        lo, hi = min(b.x0 for b in boxes), max(b.x1 for b in boxes)
        y0, y1 = min(b.y0 for b in boxes), max(b.y1 for b in boxes)

        # What the placement below will give the plot, and what sits above and
        # below it - title, axis label, legend - which the margin does not touch.
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

    # The plot's width is settled only now, by the placement above, so its
    # height is set from that rather than from the estimate the loop used.
    boxes = [(ax, ax.get_position()) for ax in fig.axes]
    y0 = min(b.y0 for _, b in boxes)
    y1 = max(b.y1 for _, b in boxes)
    h_in = fig.get_size_inches()[1]
    want_h = ((right - left) * w_in / style.PLOT_ASPECT) / h_in
    if y1 - y0 > 1e-9:
        k = want_h / (y1 - y0)
        for ax, b in boxes:
            ax.set_position([b.x0, y0 + (b.y0 - y0) * k, b.width, b.height * k])

    # Re-place the legend under the plot, now that the plot is its final size.
    # Constrained layout put it below the axes it saw before any of this; the
    # step above resized those axes and left the legend where it was, which
    # opens a gap between the two.
    if fig.legends:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        low = min(ax.get_tightbbox(r).y0 for ax in fig.axes) / fig.bbox.height
        gap = style.LEGEND_GAP / fig.get_size_inches()[1]
        for lg in fig.legends:
            b = lg.get_window_extent(r).transformed(fig.transFigure.inverted())
            lg.set_bbox_to_anchor((b.x0, low - gap - b.height, b.width, b.height),
                                  transform=fig.transFigure)

    # Vertical, now that nothing will move it back. Constrained layout pads the
    # top and the bottom by different rules - a title carries its own padding,
    # and an "outside lower center" legend sits by its own - so the two edges
    # come out unequal however the pad is set. This measures the rendered white
    # and fixes it directly.
    #
    # Height is changed by adding inches and holding every element's size in
    # inches, not by scaling: growing the figure with fractional positions
    # scales the contents too, so the white grows with it and nothing moves.
    for _ in range(6):
        h_in = fig.get_size_inches()[1]
        m_in = style.MARGIN * w_in
        _, _, iy0, iy1 = ink(fig)
        short_bottom = m_in - iy0 * h_in
        short_top = m_in - (1 - iy1) * h_in
        if abs(short_bottom) < 0.005 and abs(short_top) < 0.005:
            break
        # Signed: an edge with too much white is pulled in as well as an edge
        # with too little pushed out, or a generous top never corrects.
        new_h = max(h_in + short_bottom + short_top, 1.0)
        k = h_in / new_h                                  # keep inches, not fractions
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
    """One legend for the whole figure, below it, one row.

    entries is an ordered {label: colour}, in stacking order, which is the
    order Urban asks a legend to follow. Patches are built here rather than
    collected from the axes so that a figure with two panels showing the same
    groups gets one legend rather than two.

    Below rather than Urban's across-the-top: several of these figures carry a
    note above the plot, and the two compete for the same band.

    ncol wraps it onto more than one row. One row is the default and the
    preference, but five long category names in a row are read by scanning a
    line of text rather than by glancing at a key, which is the opposite of
    what a legend is for.
    """
    handles = [Patch(facecolor=c) for c in entries.values()]
    fig.legend(handles=handles, labels=list(entries), loc="outside lower center",
               ncol=ncol or len(entries))


def rule(ax, year=style.EXPANSION_YEAR, note=style.EXPANSION_NOTE, inside_y=None):
    """A dated vertical rule, with its note above the plot rather than in it.

    The note is an annotation attached to a mark, not a source note, so it
    belongs to the image rather than the caption. But inside the axes it sits
    on whatever the chart has drawn there - on a filled seat chart that is a
    solid band, and the text stops being legible. So it goes above the top of
    the frame, and the rule is extended up to meet it.

    The note is drawn once per figure even when the rule is drawn on every
    panel: the line is the mark, the note explains it, and explaining it twice
    in one figure is noise.

    inside_y places the note within the axes at that fraction of their height,
    for a figure whose band above the frame is already taken by a panel title.
    Pass a fraction that lands in white space, not on the data.
    """
    ax.axvline(year, zorder=5, **style.EXPANSION_LINE)
    if note is None:
        return
    if inside_y is not None:
        ax.text(year, inside_y, " " + note, transform=ax.get_xaxis_transform(),
                ha="left", va="center", zorder=6,
                fontsize=plt.rcParams["font.size"])
        return
    ax.plot([year, year], [1.0, 1.045], transform=ax.get_xaxis_transform(),
            clip_on=False, zorder=5, **style.EXPANSION_LINE)
    ax.text(year, 1.06, note, transform=ax.get_xaxis_transform(),
            ha="center", va="bottom", zorder=6, clip_on=False,
            fontsize=plt.rcParams["font.size"])


def years(ax, first, last, step=10, rotate=False, label="census year",
          headroom=0.0, minor=10):
    """A year axis.

    `step` is the labelled interval. `minor` adds an unlabelled tick at every
    census in between, so a reader can locate 1890 or 1910 on an axis that only
    names every twentieth year. Skipped where the labelled interval is already
    the census interval, which would only double the ticks.

    `headroom` is extra span past `last`, as a fraction, for anything drawn at
    the right-hand end - end labels, mainly.
    """
    span = last - first
    ax.set_xlim(first - span * 0.03, last + span * (0.03 + headroom))
    # Anchored on the last year, not the first. With a twenty-year step from
    # 1870 the labels stop at 2010 and the most recent census - the one a
    # reader looks for - goes unnamed.
    major = sorted(range(last, first - 1, -step))
    ax.set_xticks(major)
    if minor and minor < step:
        ax.xaxis.set_minor_locator(
            FixedLocator([y for y in range(first, last + 1, minor) if y not in major]))
    if rotate:
        ax.tick_params(axis="x", labelrotation=90)
        ax.set_xlabel("")
    else:
        ax.set_xlabel(label)


def counts(ax, top, step, label="residents", minor=None):
    """A count axis ending on a round tick rather than just clear of the data.

    `minor` adds an unlabelled gridline between the labelled ones, for reading
    a value off a line chart more closely than the labels allow.
    """
    ax.set_ylim(0, top)
    ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.yaxis.set_major_formatter(THOUSANDS)
    ax.set_ylabel(label)
    if minor:
        ax.yaxis.set_minor_locator(MultipleLocator(minor))
        ax.grid(axis="y", which="minor", color=plt.rcParams["grid.color"],
                linewidth=plt.rcParams["grid.linewidth"] * 0.7, alpha=0.6)


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
