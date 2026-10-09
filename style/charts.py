"""The chart types this report uses, with the conventions in style applied.

A figure script supplies data and says which chart it wants; it does not
set a colour, a size, a legend position or a margin. The reasoning behind
each placement is in docs/figures.md.

    figure()        one panel; panels() two side by side
    series()        a {label: (values, colour)} from a table and a frame
    lines()         a series over time; off_scale() marks where one leaves the axis
    stacked_bars()  composition at intervals
    hspans()        a bar per named category over a span of years, or ticks
                    on a row that is a set of dated items rather than a span
    stacked_steps() composition over continuous years; runs() finds the gaps
    age_band()      youngest to oldest as a band; strokes() draws tenures over it
    scatter()       one scatter, squarer than a time series
    scatter_pair()  two scatters stacked, each with its own broken x axis; break_x() draws a break whose far side holds one outlier, break_x_floor() one whose near side is the empty run to zero, title_broken() titles either
    dots()          a scatter, dot area from dot_area(), named by dot_label()
    events()        a timeline strip: a dot per event at its year, filled or a ring
    map_figure()    a map of polygons, with areas() to fill them, edges() to outline them, area_names() to name them and map_legend() to key them
    legend()        one legend for the figure, one row, below the axes
    legend_family() the same, stacked, with a heading and its entries indented under it
    dot_legend()    the same with a dot per colour, or a ring
    rule()          a dated vertical rule with its note above the frame
    years() counts() comma_axis() ages() shares() seats()   the axes
    fit()           the figure's size and margins, called by paths.save();
                    labels.place() then sets every name beside its dot

The geometry of a name beside a dot is labels.py, which a figure script
never imports: dot_label() reaches it from here.
"""
import numpy as np
import shapely.geometry as sg
import shapely.ops as so
from matplotlib import pyplot as plt
from matplotlib.legend_handler import HandlerBase, HandlerLine2D
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon
from matplotlib.text import Text
from matplotlib.transforms import ScaledTranslation
from matplotlib.ticker import (FixedLocator, FuncFormatter, MultipleLocator,
                               PercentFormatter)

import labels
import style

THOUSANDS = FuncFormatter(lambda v, _: f"{int(v):,}")

# A figure script names a dot through charts, like every other chart type it
# asks for; where the name then goes is labels.py's business, not its.
dot_label = labels.dot_label


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


def lines(ax, x, entries, marker=True, bridge=False, dashed=False, zorder=3):
    """One line per entry of an ordered {label: (values, colour)}. A marker
    on every point unless marker=False, dashed in the figure's standard dash
    (style.EXPANSION_LINE) if dashed=True - a reference series laid over
    something busier, where a marker at every point would be clutter and the
    dash says "not the thing itself" (docs/figures.md). A missing value
    breaks the line; with bridge=True a dotted segment joins the points
    either side of the gap, so the gap reads as a gap and not as the end of
    a series (docs/figures.md)."""
    ls = style.EXPANSION_LINE["ls"] if dashed else "-"
    for label, (values, color) in entries.items():
        ax.plot(x, values, color=color, ls=ls, marker="o" if marker else None,
                zorder=zorder, label=label)
        if bridge:
            known = [i for i, v in enumerate(values) if v == v]  # not NaN
            for a, b in zip(known, known[1:]):
                if b - a > 1:
                    ax.plot([x[a], x[b]], [values[a], values[b]], color=color,
                            ls=(0, (1, 3)), lw=plt.rcParams["lines.linewidth"], zorder=2)


def marks(ax, x, values, colour, marker="o", filled=True):
    """Separate markers with no line between them, open where `filled` is
    false: a ring is a count that is partial, not a different series.
    Missing values are skipped."""
    ring = {} if filled else dict(markerfacecolor="white")
    ax.plot(x, values, ls="", marker=marker, color=colour, zorder=4, **ring)


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


def stacked_bars(ax, x, entries, width=7):
    """Stacked bars, one per entry of an ordered {label: (values, colour)},
    from the axis upward. No texture."""
    bottom = np.zeros(len(x))
    for label, (values, color) in entries.items():
        v = np.asarray(values, dtype=float)
        ax.bar(x, v, bottom=bottom, width=width, color=color, label=label)
        bottom = bottom + v


def _hcategories(ax, ticks, names, headings=()):
    """Name the rows of a horizontal chart, top first, with any block
    headings in bold and no tick marks."""
    ax.set_yticks(ticks)
    ax.set_yticklabels(names)
    for tick, name in zip(ax.get_yticklabels(), names):
        if name in headings:
            tick.set_fontweight("bold")
    ax.tick_params(axis="y", length=0)


def _hrows(labels, groups=None):
    """Row positions for a horizontal chart: (tick positions, tick names,
    the centre of each bar), with a gap and a heading above each block."""
    ticks, names, centres = [], [], []
    y = 0.0
    for heading, n in (groups or {"": len(labels)}).items():
        if heading:
            y += style.GROUP_GAP
            ticks.append(y); names.append(heading)
            y += style.GROUP_GAP
        for label in labels[len(centres):len(centres) + n]:
            ticks.append(y); names.append(label); centres.append(y)
            y += 1.0
    return ticks, names, np.array(centres, dtype=float)


def hbars(ax, labels, values, color, groups=None):
    """Horizontal bars over named categories, first at the top. `groups` is
    an ordered {heading: n} splitting them into blocks, each under a heading
    that sits in the axis labels so nothing is hand-placed."""
    ticks, names, centres = _hrows(labels, groups)
    ax.barh(centres, values, height=0.72, color=color, zorder=3)
    _hcategories(ax, ticks, names, groups or {})
    ax.set_ylim(max(ticks) + 0.5, -0.8)


def hspans(ax, entries):
    """Horizontal bars over named categories, first at the top, from an
    ordered {label: (span, colour)}: a (first, last) pair draws a bar from
    first to last in `colour`; a sequence of years instead draws a row of
    narrow bars, one per year, for a category that is a set of dated items
    rather than a single span. `colour` there may be one value for the row,
    or a sequence the same length as the years, one colour per item, where
    the items are of more than one kind. The ticks are bars themselves,
    style.SPAN_TICK wide, so the row reads with the rest of the figure; two
    items the same year sit side by side rather than one over the other."""
    labels = list(entries)
    ticks, names, centres = _hrows(labels)
    for y, (span, color) in zip(centres, entries.values()):
        if len(span) == 2 and not hasattr(span[0], "__len__") and not hasattr(span[1], "__iter__"):
            first, last = span
            ax.barh([y], [last - first], left=[first], height=0.72, color=color, zorder=3)
        else:
            colors = color if isinstance(color, (list, tuple)) else [color] * len(span)
            seen = {}
            for xi, c in zip(span, colors):
                k = seen.get(xi, 0)
                seen[xi] = k + 1
                ax.bar(xi + k * style.SPAN_TICK, 0.72, bottom=y - 0.36,
                       width=style.SPAN_TICK, color=c, zorder=4)
    _hcategories(ax, ticks, names)
    ax.set_ylim(max(ticks) + 0.5, -0.8)


def hstacked_bars(ax, labels, entries, height=0.55, groups=None):
    """Horizontal stacked bars, one row per label, first at the top, from the
    left edge rightward over an ordered {label: (values, colour)}. `groups`
    splits the rows into blocks the way hbars() does."""
    ticks, names, y = _hrows(labels, groups)
    left = np.zeros(len(labels))
    for label, (values, color) in entries.items():
        v = np.asarray(values, dtype=float)
        ax.barh(y, v, left=left, height=height, color=color, label=label, zorder=3)
        left = left + v
    _hcategories(ax, ticks, names, groups or {})
    ax.set_ylim(max(ticks) + 0.5, -0.5 if not groups else -0.8)


def hdots(ax, labels, entries, line=True):
    """One row per label, a dot per entry of an ordered
    {label: (values, colour)}, joined by a rule so a row reads as one item."""
    y = np.arange(len(labels), dtype=float)
    if line:
        values = np.array([v for v, _ in entries.values()], dtype=float)
        for i, row in enumerate(values.T):
            good = row[~np.isnan(row)]
            if len(good) > 1:
                ax.plot([good.min(), good.max()], [y[i], y[i]],
                        color=style.UNRECORDED, lw=2.0, zorder=2,
                        solid_capstyle="round")
    for label, (values, color) in entries.items():
        ax.scatter(np.asarray(values, dtype=float), y, s=style.DOT,
                   color=color, label=label, zorder=3)
    _hcategories(ax, y, labels)
    ax.set_ylim(len(labels) - 0.5, -0.5)


def hgrouped_bars(ax, labels, entries, height=0.36):
    """Horizontal bars in pairs, one per entry of an ordered
    {label: (values, colour)}, the first entry uppermost in each pair."""
    y = np.arange(len(labels), dtype=float)
    n = len(entries)
    for i, (label, (values, color)) in enumerate(entries.items()):
        offset = (i - (n - 1) / 2) * height
        ax.barh(y + offset, np.asarray(values, dtype=float), height=height,
                color=color, label=label, zorder=3)
    _hcategories(ax, y, labels)
    ax.set_ylim(len(labels) - 0.5, -0.5)


def hwhiskers(ax, centres, values, margins, color, within=(0, 100)):
    """A 95 per cent interval through each bar, drawn over the fill so the
    eye reads the bar's end as one estimate among a range. The interval is
    held inside `within`, since a share cannot pass either end of its own
    scale and an arrow through 100 per cent would say it had."""
    low, high = within
    v = np.asarray(values, dtype=float)
    m = np.asarray(margins, dtype=float)
    ax.errorbar(v, centres, xerr=[np.minimum(m, v - low), np.minimum(m, high - v)],
                fmt="none", ecolor=color, elinewidth=1.4, capsize=4,
                capthick=1.4, zorder=4)


def share_axis(ax, label, top=100, step=20):
    """A share along the x axis, 0 to `top`, labelled every `step`."""
    ax.set_xlim(0, top)
    ax.xaxis.set_major_locator(MultipleLocator(step))
    ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))
    ax.set_xlabel(label)
    ax.grid(axis="x", color="white", alpha=0.8, linewidth=0.8)
    ax.set_axisbelow(False)


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


def seat_bands(profile, frame, palette, through):
    """Seat-years by one cut of the Board, as members_by_gender,
    members_by_race and members_by_party all draw them: a stacked step area
    in `palette`, a seats axis, the 1932 rule, years to `through`, and a
    legend. The three share one frame on purpose, so that a reader can set
    them beside each other; docs/figures.md says why.

    A year no source reports for this cut is a gap in the bands. Within a
    cut the columns are blank together - members_by_year.csv writes a cut
    whole - so which years are reported is read off the palette's columns
    rather than named. A category holding no seat in any year gets no band
    and no legend entry.
    """
    columns = list(palette)
    held = [c for c in columns if frame[c].fillna(0).sum() > 0]
    if not held:
        raise AssertionError(
            f"no seat is attributed to any of {', '.join(columns)} - check the build")
    spans = runs(frame[columns].notna().any(axis=1).to_numpy())
    bands = series(frame.fillna(0), palette, held)

    fig, ax = figure(profile)
    stacked_steps(ax, frame["year"].to_numpy(), bands, spans)
    seats(ax)
    years(ax, 1870, 2020, step=20, label="year", through=through)
    rule(ax)
    legend(fig, bands)
    return fig


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
    labels.place(fig)


def _row_major(items, ncol):
    """`items` reordered so that matplotlib, which fills a legend column by
    column, lays them out left to right along each row instead. See
    docs/figures.md."""
    rows = [items[i:i + ncol] for i in range(0, len(items), ncol)]
    return [row[c] for c in range(ncol) for row in rows if c < len(row)]


def legend(fig, entries, ncol=None, hollow=(), lines=(), dashed=()):
    """One legend for the whole figure, below it, one row unless ncol is
    given. entries is ordered {label: colour} or the {label: (values, colour)}
    a chart took; the labels in `hollow` get an open swatch, as the open
    markers they stand for, and the labels in `lines` a line swatch instead
    of a box, solid unless the label is also in `dashed`, matching whichever
    the chart drew it with. A legend that wraps reads left to right along
    each row."""
    colors = [v if isinstance(v, str) else v[1] for v in entries.values()]
    pairs = list(zip(list(entries), colors))
    if ncol:
        pairs = _row_major(pairs, ncol)

    def handle(label, c):
        if label in lines:
            return Line2D([0], [0], color=c, ls=style.EXPANSION_LINE["ls"] if label in dashed else "-")
        if label in hollow:
            return Patch(facecolor="white", edgecolor=c, linewidth=1.5)
        return Patch(facecolor=c)

    fig.legend(handles=[handle(label, c) for label, c in pairs],
               labels=[label for label, _ in pairs],
               loc="outside lower center", ncol=ncol or len(entries))


class _Under(Line2D):
    """A legend swatch set under a heading: see legend_family()."""


class _Heading(Line2D):
    """A legend row that is a heading: its label is drawn by the handler,
    flush left, because a legend's own label column starts after the swatches."""


class _UnderHandler(HandlerLine2D):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height,
                       fontsize, trans):
        cut = width * style.LEGEND_INDENT
        return super().create_artists(legend, orig_handle, xdescent - cut, ydescent,
                                      width - cut, height, fontsize, trans)


class _HeadingHandler(HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height,
                       fontsize, trans):
        return [Text(-xdescent, -ydescent + height / 2, orig_handle.get_label(),
                     ha="left", va="center_baseline", fontsize=fontsize, transform=trans)]


def legend_family(fig, singles, heading, family):
    """One legend, stacked: the `singles` ({label: (colour, marker)}, a line
    each) first, then `heading`, a name with no swatch of its own, and under
    it the `family` ({label: (colour, marker, line)}), each indented. A
    marker with no line is a bare mark, as the squares of a count that is not
    a series. The heading names the family once, so its entries do not repeat
    it (docs/figures.md, Legend)."""
    def swatch(cls, label, colour, marker, line=True):
        return cls([0], [0], color=colour, marker=marker, ls="-" if line else "", label=label)

    handles = [swatch(Line2D, label, colour, marker) for label, (colour, marker) in singles.items()]
    handles.append(_Heading([], [], label=heading))
    handles += [swatch(_Under, label, colour, marker, line)
                for label, (colour, marker, line) in family.items()]
    fig.legend(handles=handles, labels=[h.get_label() for h in handles],
               handler_map={_Under: _UnderHandler(), _Heading: _HeadingHandler()},
               loc="outside lower center", ncol=1)
    for text, handle in zip(fig.legends[-1].get_texts(), handles):
        if isinstance(handle, _Heading):
            text.set_text("")


def scatter(profile=style.DEFAULT_PROFILE):
    """One scatter, squarer than a time series."""
    return figure(profile, aspect=style.SQUARE)


def _broken_pair(fig, rect, ratio):
    """Two axes splitting `rect` ((x0, y0, x1, y1), figure fraction) by
    `ratio`, style.BREAK_GAP apart; add_axes(), not a nested gridspec, so
    the gap is exact (docs/figures.md, localities_per_member)."""
    x0, y0, x1, y1 = rect
    near_w = (x1 - x0 - style.BREAK_GAP) * ratio[0] / sum(ratio)
    far_w = (x1 - x0 - style.BREAK_GAP) - near_w
    near = fig.add_axes([x0, y0, near_w, y1 - y0])
    far = fig.add_axes([x0 + near_w + style.BREAK_GAP, y0, far_w, y1 - y0], sharey=near)
    near.break_ratio = ratio
    return near, far


def scatter_pair(profile=style.DEFAULT_PROFILE, ratios=(style.BROKEN, style.BROKEN)):
    """Two scatters stacked, each at full width with its own broken x axis:
    returns fig, (near, far), (near, far). `ratios` is each panel's (near,
    far) widths: style.BROKEN where far holds one outlier, style.BROKEN_FLOOR
    where near is only the run up from zero."""
    width = style.figsize(profile)[0]
    fig = plt.figure(figsize=(width, width * 1.6), layout="none")
    fig.plot_aspect = style.PAIR
    outer = fig.add_gridspec(2, 1, hspace=style.PAIR_HSPACE)
    top = _broken_pair(fig, outer[0].get_position(fig).extents, ratios[0])
    bottom = _broken_pair(fig, outer[1].get_position(fig).extents, ratios[1])
    return fig, top, bottom


def _middle(near):
    """The middle of a broken axis's two sides, in the near side's axes fraction."""
    ratio = near.break_ratio
    return sum(ratio) / 2 / ratio[0]


def title_broken(near, text):
    """A panel title centred over both sides of a broken axis."""
    near.set_title(text, x=_middle(near))


def _break(near, far, label, per):
    """What every broken x axis shares: the label centred under both sides,
    names allowed to run into the gap, the facing spines hidden and the cut
    drawn the same length on each side."""
    near.set_xlabel(label)
    near.xaxis.label.set_x(_middle(near))
    near.label_overflow = far
    far.label_overflow = near
    for ax in (near, far):
        ax.xaxis.set_major_formatter(THOUSANDS if per == 1 else FuncFormatter(lambda v, _: f"{int(v / per):,}"))
    near.spines["right"].set_visible(False)
    far.spines["left"].set_visible(False)
    far.tick_params(axis="y", left=False, labelleft=False)
    ratio = near.break_ratio[0] / near.break_ratio[1]
    base = 0.012
    for ax, x, dx in ((near, 1, base * max(1, 1 / ratio)), (far, 0, base * max(1, ratio))):
        ax.plot([x - dx, x + dx], [-0.02, 0.02], transform=ax.transAxes,
                color=plt.rcParams["axes.edgecolor"], lw=plt.rcParams["axes.linewidth"],
                clip_on=False)


def break_x(near, far, label, far_limits, far_tick, per=1):
    """A broken x axis whose far side holds one outlier: the far side runs
    over `far_limits` with one labelled tick at `far_tick`."""
    far.set_xlim(*far_limits)
    far.xaxis.set_major_locator(FixedLocator([far_tick]))
    _break(near, far, label, per)


def break_x_floor(near, far, label, near_top, far_limits, far_step, per=1):
    """A broken x axis whose near side is only the run up from zero, to
    `near_top`, with its 0 tick: the far side holds the data over
    `far_limits`, ticked every `far_step`."""
    near.set_xlim(0, near_top)
    near.xaxis.set_major_locator(FixedLocator([0]))
    far.set_xlim(*far_limits)
    far.xaxis.set_major_locator(MultipleLocator(far_step))
    _break(near, far, label, per)


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
        # A ring draws over the filled dots, so a loss a year from a win stays visible.
        ax.scatter([xi], [0], s=area, transform=ax.transData + lift, zorder=6 if f else 7,
                   clip_on=False, facecolors=colour if f else "white", edgecolors=colour,
                   linewidths=0.0 if f else ring)
    ax.set_ylim(0, 1)
    ax.yaxis.set_visible(False)
    ax.grid(False, axis="y")


def map_figure(profile, shapes):
    """A map of `shapes`, a list of Nx2 arrays of longitude and latitude: one
    panel at style.MAP_WIDTH, its plot exactly the shapes' extent with a
    degree of longitude scaled by cos(latitude), and no axes."""
    points = np.concatenate(shapes)
    (x0, y0), (x1, y1) = points.min(axis=0), points.max(axis=0)
    stretch = 1 / np.cos(np.radians(points[:, 1].mean()))
    fig, ax = figure(profile, of_width=style.MAP_WIDTH, aspect=(x1 - x0) / (stretch * (y1 - y0)))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect(stretch)
    ax.set_axis_off()
    return fig, ax


def areas(ax, shapes, color):
    """`shapes` filled `color`, with no edge of their own: the edges are
    drawn once, by edges()."""
    for shape in shapes:
        ax.add_patch(Polygon(shape, closed=True, facecolor=color, edgecolor=color, linewidth=0.2))


def edges(ax, shapes):
    """The outline of `shapes` taken together, in the edge ink, over the
    fills: a district drawn whole, whatever inside it is filled otherwise."""
    whole = so.unary_union([sg.Polygon(s).buffer(0) for s in shapes])
    for part in getattr(whole, "geoms", [whole]):
        ax.add_patch(Polygon(np.asarray(part.exterior.coords), closed=True, facecolor="none",
                             edgecolor=style.AREA_EDGE_COLOR, linewidth=style.AREA_EDGE, zorder=3))


def area_names(ax, names):
    """Each area's name set at its centroid, in the ink that reads on its
    fill; a map names its districts where they are. `names` is
    {label: (shapes, colour)}. A centroid that falls outside its own area
    stops the build, since the name would then sit on another."""
    size = plt.rcParams["font.size"]
    for label, (shapes, color) in names.items():
        area = so.unary_union([sg.Polygon(s).buffer(0) for s in shapes])
        centre = area.centroid
        if not area.contains(centre):
            raise AssertionError(f"{label!r}: its centroid falls outside it; name it some other way")
        ax.text(centre.x, centre.y, label, ha="center", va="center", fontsize=size,
                color=style.ink_on(color), linespacing=1.15)


def map_legend(ax, heading, entries):
    """A map's key, stacked inside the frame in the corner the shape leaves
    empty: `heading`, then `entries` ({label: colour}) as swatches under it."""
    handles = [Patch(facecolor=c, label=l) for l, c in entries.items()]
    ax.legend(handles=handles, title=heading, alignment="left", loc=style.MAP_LEGEND_AT,
              frameon=False, borderaxespad=0)


def draft_mark(ax, text=style.DRAFT_TEXT):
    """A grey diagonal watermark across the axes, for a figure still
    waiting on a decision, so a reader who meets it loose knows it is not
    final. One line in the figure script adds it and one removes it."""
    ax.text(*style.DRAFT_AT, text, transform=ax.transAxes, ha="center", va="center",
            rotation=style.DRAFT_ANGLE, color=style.DRAFT_COLOR, alpha=style.DRAFT_ALPHA,
            fontsize=plt.rcParams["font.size"] * style.DRAFT_SCALE, fontweight="bold", zorder=10)


def comma_axis(axis, top, step, label, per=1):
    """A count axis from 0 to `top`, labelled every `step` with thousands
    separators. `axis` is ax.xaxis or ax.yaxis. `per` divides the labels, for
    an axis whose label says "(thousands)"."""
    ax = axis.axes
    (ax.set_xlim if axis is ax.xaxis else ax.set_ylim)(0, top)
    axis.set_major_locator(MultipleLocator(step))
    axis.set_major_formatter(THOUSANDS if per == 1 else FuncFormatter(lambda v, _: f"{int(v / per):,}"))
    axis.set_label_text(label)


def rule(ax, year=style.EXPANSION_YEAR, note=style.EXPANSION_NOTE, ha="center", tier=0):
    """A dated vertical rule, with its note above the frame; note=None for
    the rule alone. `ha` is which way the note runs from the rule: "right"
    ends it there and "left" starts it there, so two rules close together
    keep their notes apart. `tier` raises the note, and the rule's tick with
    it, by that many lines, for notes the width of the frame cannot keep apart."""
    ax.axvline(year, zorder=5, **style.EXPANSION_LINE)
    if note is None:
        return
    size = plt.rcParams["font.size"]
    lift = ScaledTranslation(0, tier * 1.5 * size / 72, ax.figure.dpi_scale_trans)
    ax.plot([year, year], [1.0, 1.045], transform=ax.get_xaxis_transform(),
            clip_on=False, zorder=5, **style.EXPANSION_LINE)
    if tier:
        ax.annotate("", xy=(year, 1.045), xycoords=ax.get_xaxis_transform(),
                    xytext=(0, tier * 1.5 * size), textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", shrinkA=0, shrinkB=0,
                                    color=style.EXPANSION_LINE["color"],
                                    lw=style.EXPANSION_LINE["lw"],
                                    ls=style.EXPANSION_LINE["ls"]),
                    annotation_clip=False, zorder=5)
    ax.text(year, 1.06, note, transform=ax.get_xaxis_transform() + lift,
            ha=ha, va="bottom", zorder=6, clip_on=False, fontsize=size)


def years(ax, first, last, step=10, label="census year", minor=10, through=None,
          bars=None, dense=False):
    """A year axis labelled every `step` years, anchored on `last`, with an
    unlabelled tick every `minor` years between. `through` is where the axis
    ends; otherwise a little clear of `last`. `bars` is the width the bars
    on this axis were drawn at: the limits then clear half a bar, so that
    the first and last are drawn whole rather than sliced by the frame.
    `dense` names every year of a close sequence at style.DENSE_TICKS."""
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
    if dense:
        ax.tick_params(axis="x", labelsize=plt.rcParams["xtick.labelsize"] * style.DENSE_TICKS)
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
