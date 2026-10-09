"""Where a name sits beside its dot.

The geometry behind charts.dot_label(): a name is placed in the first of
PLACES where it touches no dot and no other name, stays inside the frame,
and sits nearer its own dot than any other. charts.fit() calls place() last,
against the figure's final size, because a place that is clear at one size
is not clear at another.

Nothing here is a figure's own choice, so no figure script imports this
module; it reaches a script through charts (CLAUDE.md). docs/figures.md
holds the reasoning for the conventions the constants state.
"""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.text import Text
from matplotlib.transforms import Bbox

import style

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


# After every place beside the dot has failed, the same places again, stood
# off by this many LEADERs more each time and joined to the dot by a line,
# before the build gives up.
RINGS = 3

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
    # Every name carries a leader, drawn only where place() stands it off.
    line = dict(arrowstyle="-", color=style.GREY, lw=plt.rcParams["axes.linewidth"],
                shrinkA=1, shrinkB=np.sqrt(area) / 2 + 1)
    ann = ax.annotate(text, (x, y), xytext=(0, 0), textcoords="offset points",
                      color=color, fontweight="bold" if bold else "normal",
                      fontsize=plt.rcParams["font.size"], arrowprops=line)
    # Placed last, against the final geometry, so layout must not make room for it.
    ann.set_in_layout(False)
    ann.arrow_patch.set_visible(leader)
    if not hasattr(ax, "dot_labels"):
        ax.dot_labels = []
    ax.dot_labels.append((ann, x, y, area, first, bold, leader))


def place(fig):
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
        # Either side of a broken axis lets a name run on into the gap
        # between them: nothing is drawn there.
        beyond = getattr(ax, "label_overflow", None)
        if beyond is not None:
            other = beyond.get_window_extent(r)
            frame = Bbox.from_extents(min(frame.x0, other.x1), frame.y0,
                                      max(frame.x1, other.x0), frame.y1)
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
                why = {}
                near = ([first] if first else []) + [p for p in PLACES if p != first]
                # Beside the dot first; then every place again, farther out
                # each time, with a leader line.
                for ring, place in [(0, p) for p in near] + [(r, p) for r in range(1, RINGS + 1) for p in near]:
                    lead = leader or ring > 0
                    stand = (ring + bool(leader)) * LEADER * size if lead else 0
                    across = np.sqrt(area) / 2 + GAP_ACROSS * size + stand
                    updown = np.sqrt(area) / 2 + GAP_UPDOWN * size + stand
                    ann.arrow_patch.set_visible(lead)
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
                    key = f"{place}+{ring}" if ring else place
                    if not inside:
                        why[key] = "leaves the frame"
                    elif hit:
                        why[key] = f"touches {hit[0]!r}"
                    elif any(d < 0 for i, d in enumerate(dist) if i != own):
                        why[key] = "covers another dot"
                    # A leader may start inside a dot that overlaps its own;
                    # past that it must clear every dot.
                    elif lead and any(_to_segment(dx, dy, (cx, cy), _nearest(cx, cy, b)) < rad + pad
                                        for i, (dx, dy, rad) in enumerate(dots)
                                        if i != own and np.hypot(dx - cx, dy - cy) > rad + dots[own][2]):
                        why[key] = "its leader crosses another dot"
                    elif not lead and min((d for i, d in enumerate(dist) if i != own),
                                            default=np.inf) < CLEAR * max(dist[own], pad):
                        why[key] = "sits too near another dot"
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
                f"no clear place beside its dot, or stood off with a leader, for the name "
                f"{queue[0][0].get_text()!r}: " + "; ".join(f"{p} {w}" for p, w in why.items()))


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
