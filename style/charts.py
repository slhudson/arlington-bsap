"""The chart types this report uses, with the conventions in style applied.

A figure script supplies data and says which chart it wants; it does not
set a colour, a size, a legend position or a margin. The reasoning behind
each placement is in docs/figures.md.

    figure()        one panel; panels() two side by side
    series()        a {label: (values, colour)} from a table and a frame
    lines()         a series over time; off_scale() marks where one leaves the axis
    stacked_bars()  composition at intervals
    stacked_steps() composition over continuous years; runs() finds the gaps
    age_band()      youngest to oldest as a band; strokes() draws tenures over it
    scatter()       one scatter, squarer than a time series
    broken_scatter() the same with a broken x axis; break_x() draws the break
    dots()          a scatter, dot area from dot_area(), named by dot_label()
    events()        a timeline strip: a dot per event at its year, filled or a ring
    legend()        one legend for the figure, one row, below the axes
    dot_legend()    the same with a dot per colour, or a ring
    rule()          a dated vertical rule with its note above the frame
    years() counts() comma_axis() ages() shares() seats()   the axes
    fit()           the figure's size and margins, called by paths.save();
                    place_labels() then sets every name beside its dot
"""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text
from matplotlib.transforms import ScaledTranslation
from matplotlib.ticker import (FixedLocator, FuncFormatter, MultipleLocator,
                               PercentFormatter)

import style

THOUSANDS = FuncFormatter(lambda v, _: f"{int(v):,}")


def figure(profile=style.DEFAULT_PROFILE, of_width=1.0, aspect=None):
    """One panel at this profile's width. The height is solved by fit().
    `of_width` is the fraction of that width to take, for the few figures
    too narrow to fill the page, and `aspect` replaces the profile's for
    the few that are not time series; pass names from style, never numbers."""
    fig, ax = plt.subplots(figsize=style.figsize(profile, of_width))
    fig.plot_aspect = aspect
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


def lines(ax, x, entries, marker=True):
    """One line per entry of an ordered {label: (values, colour)}. A marker
    on every point unless marker=False."""
    for label, (values, color) in entries.items():
        ax.plot(x, values, color=color, marker="o" if marker else None, zorder=3, label=label)


def age_band(ax, x, low, high, spans, color, width=1.0):
    """The youngest-to-oldest span of the Board as a step area over samples
    at `x` (years, possibly fractional), each holding for `width` of a year.
    NaN samples are gaps, left open."""
    x = np.asarray(x, dtype=float)
    for a, b in spans:
        xs = np.append(x[a:b + 1], x[b] + width)
        ax.fill_between(xs, np.append(low[a:b + 1], low[b]), np.append(high[a:b + 1], high[b]),
                        step="post", facecolor=color, edgecolor="none", zorder=1)


def strokes(ax, segments, color, alpha=1.0):
    """One straight stroke per (x0, y0, x1, y1), over the band."""
    for x0, y0, x1, y1 in segments:
        ax.plot([x0, x1], [y0, y1], color=color, alpha=alpha, solid_capstyle="butt", zorder=3)


def stacked_bars(ax, x, entries, width=7):
    """Stacked bars, one per entry of an ordered {label: (values, colour)},
    from the axis upward. No texture."""
    bottom = np.zeros(len(x))
    for label, (values, color) in entries.items():
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


def stacked_steps(ax, years, entries, spans):
    """Stacked step-area, one band per entry of an ordered {label: (values,
    colour)}; each year's value spans [year, year + 1)."""
    years = np.asarray(years)
    cum = np.zeros(len(years))
    for label, (values, color) in entries.items():
        top = cum + np.asarray(values, dtype=float)
        for n, (a, b) in enumerate(spans):
            xs = np.append(years[a:b + 1], years[b] + 1)
            lo = np.append(cum[a:b + 1], cum[b])
            hi = np.append(top[a:b + 1], top[b])
            ax.fill_between(xs, lo, hi, step="post", facecolor=color,
                            edgecolor="white", linewidth=0.3,
                            label=label if n == 0 else None)
        cum = top


def fit(fig, profile=style.DEFAULT_PROFILE):
    """Size and place this figure: the canvas is the profile's width, the
    plot is the profile's aspect times as wide as tall, and style.MARGIN of
    white surrounds the ink on all four sides. Iterated, because the height
    depends on furniture that is only measurable once drawn."""
    aspect = getattr(fig, "plot_aspect", None) or style.PROFILES[profile]["aspect"]

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
        want = plot_w / aspect + furniture + 2 * m_in
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
    want_h = ((right - left) * w_in / aspect) / h_in
    if y1 - y0 > 1e-9:
        k = want_h / (y1 - y0)
        for ax, b in boxes:
            ax.set_position([b.x0, y0 + (b.y0 - y0) * k, b.width, b.height * k])

    # Re-place the legend under the plot at its final size, centred on the
    # plot region rather than the canvas (docs/figures.md, Legend).
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

    # Names beside dots are placed last, against the final geometry.
    place_labels(fig)


def legend(fig, entries, ncol=None):
    """One legend for the whole figure, below it, one row unless ncol is
    given. entries is ordered {label: colour} or the {label: (values, colour)}
    a chart took."""
    colors = [v if isinstance(v, str) else v[1] for v in entries.values()]
    fig.legend(handles=[Patch(facecolor=c) for c in colors], labels=list(entries),
               loc="outside lower center", ncol=ncol or len(entries))


def scatter(profile=style.DEFAULT_PROFILE):
    """One scatter, squarer than a time series."""
    return figure(profile, aspect=style.SQUARE)


def broken_scatter(profile=style.DEFAULT_PROFILE):
    """One scatter whose x axis is broken so that one far point stays in
    view: the near and far sides as two axes sharing y. break_x() draws
    the break once both sides have their limits."""
    fig, (near, far) = plt.subplots(1, 2, sharey=True, figsize=style.figsize(profile),
                                    gridspec_kw={"width_ratios": style.BROKEN})
    # The two sides sit close, as one axis with a gap, not two panels.
    fig.get_layout_engine().set(w_pad=0.02, wspace=0.0)
    fig.plot_aspect = style.SQUARE
    return fig, (near, far)


def break_x(near, far, label, far_limits, far_tick):
    """The break between the two sides of a broken x axis: the facing
    spines hidden and a short slash across the axis line on each side,
    and the axis label under the near side, which holds the data. The far
    side runs over `far_limits` with one labelled tick at `far_tick`."""
    near.set_xlabel(label)
    far.set_xlim(*far_limits)
    far.xaxis.set_major_locator(FixedLocator([far_tick]))
    far.xaxis.set_major_formatter(THOUSANDS)
    near.spines["right"].set_visible(False)
    far.spines["left"].set_visible(False)
    far.tick_params(axis="y", left=False, labelleft=False)
    ratio = style.BROKEN[0] / style.BROKEN[1]
    for ax, x, dx in ((near, 1, 0.012), (far, 0, 0.012 * ratio)):
        ax.plot([x - dx, x + dx], [-0.02, 0.02], transform=ax.transAxes,
                color=plt.rcParams["axes.edgecolor"], lw=plt.rcParams["axes.linewidth"],
                clip_on=False)


def dot_area(highlight=False, profile=style.DEFAULT_PROFILE):
    """A scatter dot's area in points squared, stepped up with the
    profile's type."""
    return (style.DOT_HIGHLIGHT if highlight else style.DOT) * style.PROFILES[profile]["scale"] ** 2


def dots(ax, x, y, area, colors):
    """One dot per point, area as given (one value or one per point).
    Every dot is remembered, so that place_labels() can keep names off it."""
    area = np.broadcast_to(np.asarray(area, dtype=float), np.shape(np.asarray(x)))
    ax.scatter(x, y, s=area, c=list(colors), edgecolors="white", linewidths=0.8,
               zorder=3, clip_on=False)
    if not hasattr(ax, "dots_drawn"):
        ax.dots_drawn = []
    ax.dots_drawn += list(zip(np.asarray(x, dtype=float), np.asarray(y, dtype=float), area))


# Where a name may sit beside its dot, in order of preference: offsets in
# units of the gap, and the text's alignment.
PLACES = {
    "right":       (1, 0, "left", "baseline"),
    "left":        (-1, 0, "right", "baseline"),
    "above":       (0, 1, "center", "bottom"),
    "below":       (0, -1, "center", "top"),
    "above right": (0.7, 0.7, "left", "bottom"),
    "above left":  (-0.7, 0.7, "right", "bottom"),
    "below right": (0.7, -0.7, "left", "top"),
    "below left":  (-0.7, -0.7, "right", "top"),
}


# A name belongs to its dot only if every other dot is at least this many
# times as far from it.
CLEAR = 2.0
# The white between a dot's edge and its name, as a fraction of the type
# size: across, and up or down, where the text's own line box already
# carries some.
GAP_ACROSS = 0.2
GAP_UPDOWN = 0.05
# How much farther a name with a leader stands off, in type sizes.
LEADER = 1.2
# Half the height of a capital, in type sizes: a name beside its dot drops
# its baseline by this much, so the letters, not the line box with its
# descenders, are centred on the dot.
HALF_CAP = 0.36


def dot_label(ax, x, y, text, area, color="black", bold=False, first=None, leader=False):
    """Name a dot. Where the name goes is chosen by place_labels() once the
    figure's size is final; `first` is a place from PLACES to try before
    the rest. `leader` stands the name off and draws a short line to the
    dot, for a dot in a row too tight to name beside it."""
    line = dict(arrowstyle="-", color=style.GREY, lw=plt.rcParams["axes.linewidth"],
                shrinkA=1, shrinkB=np.sqrt(area) / 2 + 1) if leader else None
    ann = ax.annotate(text, (x, y), xytext=(0, 0), textcoords="offset points",
                      color=color, fontweight="bold" if bold else "normal",
                      fontsize=plt.rcParams["font.size"], arrowprops=line)
    if not hasattr(ax, "dot_labels"):
        ax.dot_labels = []
    ax.dot_labels.append((ann, x, y, area, first, bold, leader))


def place_labels(fig):
    """Put every name from dot_label() in the first place, in PLACES order,
    where it touches no dot and no other name, stays inside the frame, and
    sits nearer its own dot than any other. Bold names choose first, then
    the most crowded. A name with no such place stops the build."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    px = fig.dpi / 72
    pad = plt.rcParams["font.size"] * 0.15 * px
    for ax in fig.axes:
        labels = getattr(ax, "dot_labels", [])
        if not labels:
            continue
        frame = ax.get_window_extent(r)
        dots = [(*ax.transData.transform((x, y)), np.sqrt(a) / 2 * px)
                for x, y, a in getattr(ax, "dots_drawn", [])]

        def crowd(item):
            _, x, y, _, _, bold, _ = item
            cx, cy = ax.transData.transform((x, y))
            return (not bold, -sum(np.hypot(cx - dx, cy - dy) < 60 * px for dx, dy, _ in dots))

        def attempt(queue):
            """Place the names in this order; the index and reasons of the
            first that finds no place, or None if all do."""
            placed = []
            for k, (ann, x, y, area, first, bold, leader) in enumerate(queue):
                cx, cy = ax.transData.transform((x, y))
                size = plt.rcParams["font.size"]
                stand = LEADER * size if leader else 0
                across = np.sqrt(area) / 2 + GAP_ACROSS * size + stand
                updown = np.sqrt(area) / 2 + GAP_UPDOWN * size + stand
                why = {}
                for place in ([first] if first else []) + [p for p in PLACES if p != first]:
                    ux, uy, ha, va = PLACES[place]
                    drop = HALF_CAP * size if va == "baseline" else 0
                    ann.set_position((ux * across, uy * updown - drop))
                    ann.set_ha(ha)
                    ann.set_va(va)
                    # The text alone: an annotation's own extent includes its leader.
                    b = Text.get_window_extent(ann, r)
                    box = (b.x0 - pad, b.y0 - pad, b.x1 + pad, b.y1 + pad)
                    inside = (b.x0 >= frame.x0 and b.x1 <= frame.x1
                              and b.y0 >= frame.y0 and b.y1 <= frame.y1)
                    # Distances to the text itself, not its padded box.
                    dist = [_to_box(dx, dy, (b.x0, b.y0, b.x1, b.y1)) - rad for dx, dy, rad in dots]
                    own = int(np.argmin([np.hypot(dx - cx, dy - cy) for dx, dy, _ in dots]))
                    hit = [p[4] for p in placed if _overlap(box, p)]
                    if not inside:
                        why[place] = "leaves the frame"
                    elif hit:
                        why[place] = f"touches {hit[0]!r}"
                    elif any(d < 0 for i, d in enumerate(dist) if i != own):
                        why[place] = "covers another dot"
                    # A leader may start inside a dot that overlaps its own;
                    # past that it must clear every dot.
                    elif leader and any(_to_segment(dx, dy, (cx, cy), _nearest(cx, cy, b)) < rad + pad
                                        for i, (dx, dy, rad) in enumerate(dots)
                                        if i != own and np.hypot(dx - cx, dy - cy) > rad + dots[own][2]):
                        why[place] = "its leader crosses another dot"
                    elif not leader and min((d for i, d in enumerate(dist) if i != own),
                                            default=np.inf) < CLEAR * max(dist[own], pad):
                        why[place] = "sits too near another dot"
                    else:
                        placed.append((*box, ann.get_text()))
                        break
                else:
                    return k, why
            return None

        # A name that finds no place moves to the front and every name is
        # placed again, until all fit or the order has been tried enough.
        queue = sorted(labels, key=crowd)
        for _ in range(3 * len(queue)):
            failed = attempt(queue)
            if failed is None:
                break
            k, why = failed
            queue.insert(0, queue.pop(k))
        else:
            raise AssertionError(
                f"no clear place beside its dot for the name {queue[0][0].get_text()!r}: "
                + "; ".join(f"{p} {w}" for p, w in why.items()))


def _overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _to_box(x, y, box):
    """Distance from a point to a box, zero inside it."""
    return np.hypot(max(box[0] - x, 0, x - box[2]), max(box[1] - y, 0, y - box[3]))


def _nearest(x, y, b):
    """The point of the text's box nearest (x, y)."""
    return min(max(x, b.x0), b.x1), min(max(y, b.y0), b.y1)


def _to_segment(x, y, a, b):
    """Distance from a point to the segment from a to b."""
    a, b, p = np.asarray(a), np.asarray(b), np.asarray((x, y))
    t = np.clip(np.dot(p - a, b - a) / max(np.dot(b - a, b - a), 1e-9), 0, 1)
    return float(np.hypot(*(p - (a + t * (b - a)))))


def dot_legend(fig, entries, profile=style.DEFAULT_PROFILE):
    """One legend below the figure, one row, a dot per entry in `entries`
    ({label: colour}, or {label: (colour, filled)} where some are rings),
    drawn at the scatter's own size."""
    size = float(np.sqrt(dot_area(profile=profile)))

    def handle(label, v):
        colour, filled = (v, True) if isinstance(v, str) else v
        ring = {} if filled else dict(markerfacecolor="white",
                                      markeredgewidth=RING * style.PROFILES[profile]["scale"])
        return Line2D([], [], marker="o", ls="", color=colour, markersize=size, label=label, **ring)
    fig.legend(handles=[handle(k, v) for k, v in entries.items()],
               loc="outside lower center", ncol=len(entries), handletextpad=0.3)


# An open ring's stroke, in points before the profile's scale.
RING = 1.2


def events(ax, x, filled, colour, profile=style.DEFAULT_PROFILE):
    """A timeline strip: one dot per event at its x, in the order given,
    events at the same x stacked dot on dot upward from the axis. A filled
    dot, or an open ring where `filled` is false. The y axis carries no
    measure, so it is hidden; the stack is measured in points, so it holds
    its shape whatever height fit() gives the plot. A filled dot has no
    white edge: events a year apart overlap, and an edge would cut the
    overlap into crescents that read as rings. Dots sit over a rule."""
    area = dot_area(profile=profile)
    step = 2 * np.sqrt(area / np.pi) / 72            # a dot's diameter, in inches
    ring = RING * style.PROFILES[profile]["scale"]
    level = {}
    for xi, f in zip(x, filled):
        k = level.get(xi, 0)
        level[xi] = k + 1
        lift = ScaledTranslation(0, (k + 0.6) * step, ax.figure.dpi_scale_trans)
        ax.scatter([xi], [0], s=area, transform=ax.transData + lift, zorder=6, clip_on=False,
                   facecolors=colour if f else "white", edgecolors=colour,
                   linewidths=0.0 if f else ring)
    ax.set_ylim(0, 1)
    ax.yaxis.set_visible(False)
    ax.grid(False, axis="y")


def comma_axis(axis, top, step, label):
    """A count axis from 0 to `top`, labelled every `step` with thousands
    separators. `axis` is ax.xaxis or ax.yaxis."""
    ax = axis.axes
    (ax.set_xlim if axis is ax.xaxis else ax.set_ylim)(0, top)
    axis.set_major_locator(MultipleLocator(step))
    axis.set_major_formatter(THOUSANDS)
    axis.set_label_text(label)


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
    comma_axis(ax.yaxis, top, step, label)
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
