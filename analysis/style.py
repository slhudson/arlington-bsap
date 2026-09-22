"""Shared visual conventions. Every figure imports these; none redeclares them.

A palette or font change is a single edit here, and a group keeps the same
colour in every figure it appears in.
"""
import matplotlib as mpl

# Race/ethnicity. Order is the stacking order used by the area and bar charts.
BLACK = "#E69F00"
HISP = "#009E73"
AAPI = "#CC79A7"
WHITE = "#D9D3C4"

GROUPS = ["black", "hisp", "aapi", "white"]
GROUP_COLORS = [BLACK, HISP, AAPI, WHITE]
GROUP_LABELS = ["Black", "Hispanic/Latino", "Asian American/Pacific Islander", "White"]

# The pale sand above is close to invisible as a 1.6pt line on white paper, so
# line charts use a darker taupe for the same category.
WHITE_LINE = "#A3997F"
TOTAL_LINE = "#555555"

# Residual category: multiracial, other, or unreported.
OTHER = "#E6E6E6"
OTHER_EDGE = "#8C8C8C"

# Gender. Far apart in hue, so they stay distinct in greyscale and for
# colourblind readers.
WOMEN = "#E8A598"
MEN = "#A9BBCB"

# Residents-per-seat figure.
ACTUAL = "#3B4A5A"
BENCHMARK = "#C9794A"
GAP = "#EFE6DC"

GRID = "#DDDDDD"

# Figure dimensions, inches.
WIDE = (6.5, 4.6)        # standard single-panel figure at LaTeX text width
TALL = (4.0, 8.0)        # 1:2, so the early decades have visible height
STACKED = (6.5, 6.4)     # two panels sharing an x-axis
PER_SEAT = (6.5, 4.4)

# 1932: the Board expands from three to five seats and magisterial districts
# are replaced by at-large elections. Drawn identically wherever it appears.
EXPANSION_YEAR = 1932
EXPANSION_NOTE = ("1932: Board expands from 3 to 5 seats;\n"
                  "magisterial districts replaced by at-large elections")
EXPANSION_LINE = dict(color="black", lw=1.1, ls=(0, (4, 2)))

HALF_SEAT_NOTE = ("Note: Half seats occur when a Board member resigned or died "
                  "before the end of the year\nand was subsequently replaced.")


def apply(legend_fontsize=8):
    """Set the rcParams every figure shares.

    Computer Modern matches Overleaf's default body text, so figure labels sit
    in the same typeface as the surrounding prose. pdf.fonttype 42 embeds
    TrueType rather than Type 3, which keeps text selectable and searchable in
    the compiled PDF.
    """
    mpl.rcParams.update({
        "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
        "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
        "font.size": 9, "axes.labelsize": 9, "legend.fontsize": legend_fontsize,
        "pdf.fonttype": 42,
    })


def despine(ax):
    """Drop the top and right spines, as every figure here does."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
