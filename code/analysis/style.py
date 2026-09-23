"""Shared visual conventions. Every figure imports these; none redeclares them.

A palette or font change is a single edit here, and a category keeps the same
colour in every figure it appears in.
"""
import matplotlib as mpl

# Race/ethnicity. Order is the stacking order used by the bar and area charts.
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

# Type scale, points. Two sizes.
#
# TEXT is everything that labels a point or a mark: tick labels, axis labels,
# legend entries, annotations. On these figures none of those outranks another,
# and sizing them differently is a matplotlib habit rather than a distinction a
# reader uses.
#
# TITLE is the one real exception: a panel title names a whole region rather
# than a point, and in a two-panel figure it has to read as belonging to the
# panel rather than to the axis.
#
# Type scale, points. Taken from the Urban Institute data visualization style
# guide's figures for PDF products, which is a published convention for policy
# research rather than a judgement made here:
#
#   urbaninstitute.github.io/graphics-styleguide/
#   axis titles 8.5 | axis labels 8.5 | data labels 8.5 | legend 9.5 | notes 8
#
# Journal guidance brackets the same range: ACS sets a floor of 8pt, Elsevier
# 7pt, Cell 6-8pt, Nature 5-7pt. Nothing published puts figure text at 10.
#
# One departure, and the reason for it. Urban's sizes assume Lato or Arial.
# These figures are set in Computer Modern to match the paper's body text, and
# CM has a smaller x-height and thinner strokes, so it reads smaller at the
# same size. PANEL is Urban's legend size rather than a new one.
#
# Urban puts the title and subtitle in the document rather than in the chart.
# So does this repository: the caption in paper/arlington-bsap.tex carries it,
# and no figure draws a headline. PANEL is only for the (a)/(b) labels that
# name a panel within a figure.
#
# A script that passes fontsize= is how a set of figures ends up with six.
NOTE = 8                 # annotations and notes
TEXT = 8.5               # axis titles, tick labels, data labels
PANEL = 9.5              # legend text, and the (a)/(b) panel labels

# Figure dimensions, inches. Width is LaTeX text width throughout.
WIDE = (6.5, 4.6)        # single panel
TALL = (4.0, 8.0)        # 1:2, so the early decades have visible height
TWO_PANEL = (6.5, 6.4)   # two panels stacked
SIDE_BY_SIDE = (6.5, 5.0)  # two panels left and right
SEATS = (6.5, 3.8)       # the 0-5 seat charts, a matched pair
PER_SEAT = (6.5, 4.4)

# Space left around a saved figure, inches. Legends and rotated tick labels sit
# outside the axes, and a tight box crops to them exactly, which reads as
# cramped on the page.
PAD = 0.2

# 1932: the Board expands from three to five seats and magisterial districts
# are replaced by at-large elections. Drawn identically wherever it appears.
EXPANSION_YEAR = 1932
# Two namings, because the rule is doing different work in different figures.
# On a 0-5 seat axis the expansion is the thing the axis shows, so the numbers
# are worth stating. Elsewhere it is context, and four words are enough. That
# the districts were replaced by at-large elections is carried by the prose in
# both cases, not repeated on every chart that draws the rule.
EXPANSION_NOTE = "1932 Board expansion"
EXPANSION_NOTE_SEATS = "1932: Board expands from 3 to 5 seats"
EXPANSION_LINE = dict(color="black", lw=1.1, ls=(0, (4, 2)))

HALF_SEAT_NOTE = ("Note: Half seats occur when a Board member resigned or died "
                  "before the end of the year\nand was subsequently replaced.")


def apply(legend_fontsize=None):
    """Set the rcParams every figure shares.

    Computer Modern matches Overleaf's default body text, so figure labels sit
    in the same typeface as the surrounding prose. pdf.fonttype 42 embeds
    TrueType rather than Type 3, keeping text selectable in the compiled PDF.
    """
    mpl.rcParams.update({
        "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
        "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
        "font.size": TEXT, "axes.labelsize": TEXT, "axes.titlesize": PANEL,
        "xtick.labelsize": TEXT, "ytick.labelsize": TEXT,
        "legend.fontsize": legend_fontsize or PANEL,
        "pdf.fonttype": 42,
    })


def despine(ax):
    """Drop the top and right spines, as every figure here does."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
