"""Visual conventions. Every figure imports these; none redeclares them.

This folder holds how a number is *shown*, separately from code/analysis/,
which holds the substance. It sits outside code/ because most of it cannot be
executed - a typeface, and a table of rcParams - and code/ is for things you
can run.

The separation is structural rather than a habit: there is no paths.py here, so
nothing in style/ has a route to data/ at all. A chart helper that wanted to
reach a column has nothing to reach with - the same wall code/analysis/ already
has against data/raw/.

The conventions are the Urban Institute's data visualization style guide,

    https://urbaninstitute.github.io/graphics-styleguide/

loaded from urban.mplstyle. This module holds what rcParams cannot express:
the palette, the two output profiles, and which colour belongs to which group.

**Where this project departs from Urban, the departure is here with its
reason.** There are three.

*The palette is Okabe-Ito, not Urban's.* Urban's categorical colours are
designed for the web, not for colour vision deficiency. Okabe and Ito's set is
built for exactly that, and holds four separable hues under simulated
deuteranopia where Urban's does not. Urban's colours stay in gallery.py as
candidates so the choice remains reviewable.

*The legend sits below the figure, not above it.* Urban stretches it across the
top. Below reads better here, where several figures carry a note above the
plot.

*No group holds the lead colour.* Urban's hierarchy runs blue first, then
yellow and magenta, with grey for residuals. Applied straight down a stack
about racial representation that hands one group the primary colour, which is
a claim rather than a convention. So the neutral goes to the largest group -
in every one of these charts White is the background mass - and the saturated
hues go to the groups the section examines. Gender follows the same logic:
men are the mass and take the neutral.

*Sources and notes.* Urban puts them below the figure in the document. So does
this repository, in the LaTeX caption. The one exception is an annotation
attached to a mark, such as the 1932 rule, which stays in the panel.
"""
import colorsys
import pathlib

import matplotlib as mpl
import matplotlib.style
from matplotlib import font_manager

HERE = pathlib.Path(__file__).resolve().parent
MPLSTYLE = HERE / "urban.mplstyle"
FONTS = HERE / "fonts"

# --- the palette --------------------------------------------------------------
# Okabe and Ito's Color Universal Design set, built so that no two hues collapse
# into one another under colour vision deficiency. Urban's categorical colours
# are designed for the web and are not: under simulated deuteranopia Okabe-Ito
# holds four separable hues where Urban's magenta goes olive. It gives up some
# tonal spread in greyscale, which costs nothing unless the memo is printed in
# black and white. Both are drawn in figures/gallery/.
#
#   Masataka Okabe and Kei Ito, "Color Universal Design (CUD): How to make
#   figures and presentations that are friendly to colorblind people".
OKABE_ITO = {
    "orange":         "#E69F00",
    "sky_blue":       "#56B4E9",
    "bluish_green":   "#009E73",
    "yellow":         "#F0E442",
    "blue":           "#0072B2",
    "vermilion":      "#D55E00",
    "reddish_purple": "#CC79A7",
    "black":          "#000000",
}

# Two near-neutrals, not from the set, chosen for this report. No group holds a
# saturated lead colour on a chart about representation, so the largest group
# takes the neutral and the residual band takes the darker one.
SAND = "#D9D3C4"          # the mass: White residents
# The sand is tuned as a filled area and is close to invisible as a stroke on
# white paper. A line chart uses a darker taupe of the same hue, so White is
# recognisably the same category in both without being unreadable in one.
SAND_LINE = "#A3997F"
GREY = "#8C8C8C"          # the residual: Other or Multiracial

# Colours are assigned per subject rather than through numbered slots. A slot
# called "blue" that holds orange is how this got confusing once already.
#
# Nothing shares a colour with anything it appears beside. Asian/Pacific
# Islander takes Okabe-Ito's blue rather than its reddish purple, because the
# reddish purple carries women on the gender chart and the two should not read
# as the same category across a section.
RACE_COLORS = {
    "black": OKABE_ITO["orange"],
    "hisp":  OKABE_ITO["bluish_green"],
    "aapi":  OKABE_ITO["blue"],
    "white": SAND,
}
CENSUS_COLORS = {
    "nh_black": OKABE_ITO["orange"],
    "hispanic": OKABE_ITO["bluish_green"],
    "nh_aapi":  OKABE_ITO["blue"],
    "nh_white": SAND,
    "nh_other": GREY,
}
# Pink against the sand, not against blue. Urban's guide says: "Urban tries not
# to use color palettes that reinforce gender or racial stereotypes (e.g., pink
# for women and blue for men)." Pink and blue was tried and is the example the
# guide names. Half the pairing goes: men take the same near-neutral the
# largest group takes everywhere else in this report, so the figure reads the
# way the race figures do - the mass is the backdrop, the subject carries the
# colour - rather than as a gendered pair.
GENDER_COLORS = {
    "women": OKABE_ITO["reddish_purple"],
    "men":   SAND,
}
# The growth figure: two counts of people, no categories. It took Okabe-Ito's
# blue until that blue became Asian and Pacific Islander on the race charts, and
# the growth figure comes first in the report - so a reader would have met the
# colour as a series before meeting it as a category. Nothing here needs a hue
# to be identified: both lines are labelled where they run. Vermilion also
# carries Republican on the party chart, which is the one reuse in the set;
# it costs nothing here because the line is named where it runs, not by its
# colour.
SERIES_COLORS = {"population": "#5C5859", "per_seat": OKABE_ITO["vermilion"]}
# The turnout figure: three counts of people, no categories, every line
# named where it runs. The same two colours as the growth figure, in the
# same roles - vermilion for the series the figure is about, the Board's
# voters, and the dark grey for the count it is measured against, the
# presidential vote. Registered voters are the backdrop the other two sit
# under, and take the taupe that White takes as a line: the neutral for the
# mass, as everywhere else in the set.
TURNOUT_COLORS = {
    "board": OKABE_ITO["vermilion"],
    "president": "#5C5859",
    "registered": SAND_LINE,
}
# The Board's voters split by what else was on the ballot: four lines, one
# per year of the cycle, from the top of the ticket down. Vermilion stays
# with the presidential-year Board vote, the series the counts figure was
# about; the other three take hues in falling order of turnout, orange,
# bluish green and black. Each is a category elsewhere in the set (Black,
# Hispanic or Latino) and none reads as one here: the lines are named in
# the legend and never share a page with a race chart.
CYCLE_ORDER = ["president", "governor", "midterm", "delegates"]
CYCLE_COLORS = {
    "president": OKABE_ITO["vermilion"],
    "governor":  OKABE_ITO["orange"],
    "midterm":   OKABE_ITO["bluish_green"],
    "delegates": OKABE_ITO["black"],
}
CYCLE_LABELS = {
    "president": "presidential year",
    "governor":  "governor's year",
    "midterm":   "midterm year",
    "delegates": "House of Delegates year",
}

# Party. The two partisan hues are the ones readers bring with them, at
# Okabe-Ito's values: sky blue for Democratic and vermilion for Republican.
# Neither is Okabe-Ito's blue, which is Asian and Pacific Islander on the race
# charts. Yellow for ABC, the nonpartisan coalition allied with the Democrats,
# sits between the two on the stack. The near-neutral rule applied elsewhere -
# the largest group takes sand - is set aside here deliberately: partisan
# colours are a convention readers already hold, and a sand band labelled
# Democratic would be read against it. Independents take the same grey as the
# residual census band; "not recorded" takes a lighter grey still, so that an
# absence of evidence never reads as a category.
UNRECORDED = "#DDDDDD"
PARTY_COLORS = {
    "dem":        OKABE_ITO["sky_blue"],
    "abc":        OKABE_ITO["yellow"],
    "rep":        OKABE_ITO["vermilion"],
    "ind":        GREY,
    "unrecorded": UNRECORDED,
}
# Stacking order, axis upward. The two parties take the two edges of the
# frame: Democrats grow up from the axis, Republicans hang down from the
# five-seat line, and ABC, the unknown and the independents sit between them.
# Each category then keeps one place on the page for the whole run, and a
# majority reads as the block that crosses the middle. Sorting each year by
# size was tried and put the Democratic band on the floor in one decade and
# on the ceiling in the next.
PARTY_ORDER = ["dem", "abc", "unrecorded", "ind", "rep"]
# "ABC" rather than the full name: the legend is one row. The caption expands
# it. "independent" and "not recorded" are not proper nouns and stay lowercase.
PARTY_LABELS = {
    "dem": "Democratic",
    "abc": "ABC",
    "rep": "Republican",
    "ind": "independent",
    "unrecorded": "not recorded",
}

# The voters' side of the same comparison: the presidential vote in three
# bands, the same colours, so a reader moving between the two figures is not
# relearning them. "other" is every other candidate, and takes the
# independents' grey.
VOTERS_ORDER = ["dem", "other", "rep"]
VOTERS_COLORS = {"dem": PARTY_COLORS["dem"], "other": GREY, "rep": PARTY_COLORS["rep"]}
VOTERS_LABELS = {"dem": "Democratic", "other": "other", "rep": "Republican"}
# The County Board vote has the seat chart's bands, in the seat chart's order,
# with "other" standing where "independent" stands there: it holds the
# independents and every small group the county ever labelled.
BOARD_VOTE_ORDER = ["dem", "abc", "unrecorded", "other", "rep"]
BOARD_VOTE_COLORS = {**PARTY_COLORS, "other": GREY}
BOARD_VOTE_LABELS = {**PARTY_LABELS, "other": "other"}

RESIDUAL_COLOR = GREY

# Stacking order, axis upward.
GROUP_ORDER = ["black", "hisp", "aapi", "white"]

# The Bureau's own wording, and no slashes. The ampersand is for width: the
# legend is one row. "Asian and Pacific Islander" is what the 1980 dictionary
# calls this category; from 2000 the Bureau splits it into
# "Asian" and "Native Hawaiian and Other Pacific Islander", and this series
# combines them to stay consistent back to 1980, so the older name is the
# accurate one for the combination. "Hispanic or Latino" is the Bureau's wording
# from 2000; 1980 says "Spanish origin".
#
# Legend entries capitalise proper nouns and nothing else. Racial and ethnic
# identifiers are proper nouns and keep their capitals; "women" and "men" are
# not, under anyone's convention, and do not.
#
# "Multiracial" keeps its capital. It was lowercased once alongside women and
# men, which was the wrong company: it is a racial identifier and belongs with
# Black, White and Hispanic or Latino, not with a demographic descriptor. A
# lowercase entry sitting among the four it is the residual of would read as a
# lesser category rather than a smaller one. Urban asks for sentence case
# throughout a figure, which this follows in substance - the departure is only
# that a lowercase "white" beside "Black" would read as a slip rather than as a
# position, so both are capitalised. Axis labels and panel titles are
# lowercase.
#
# Both Black and White are capitalised. APA and AMA capitalise both; Urban
# capitalises Black and leaves white lowercase, which in a legend beside
# "Hispanic or Latino" reads as a typo rather than as a position.
GROUP_LABELS = {
    "black": "Black",
    "hisp": "Hispanic or Latino",
    "aapi": "Asian & Pacific Islander",
    "white": "White",
}

# The census basis, 1980 on: five groups that partition the county. Same
# colours, so a reader moving between the two bases is not relearning them.
# Other or Multiracial sits with the other groups, below White, not above it.
# It is a kind of not-White; stacking it on top splits that population in two
# and makes the county read as less diverse than it is.
CENSUS_ORDER = ["nh_black", "hispanic", "nh_aapi", "nh_other", "nh_white"]
# On this basis every group except Hispanic or Latino is non-Hispanic, so a
# legend that says so five times repeats itself; the caption says it once, as
# "groups other than Hispanic or Latino are non-Hispanic".
CENSUS_LABELS = {
    "nh_black": "Black",
    "hispanic": "Hispanic or Latino",
    "nh_aapi": "Asian & Pacific Islander",
    "nh_white": "White",
    "nh_other": "Other or Multiracial",
}

GENDER_ORDER = ["women", "men"]
GENDER_LABELS = {"women": "women", "men": "men"}

# The residual band. Not "unreported": nothing in it is. Before 1980 it is
# people in race categories the source did not break out, and it is tiny - 0 to
# 202 people, never above 0.12 per cent of the county. From 1980 it is American
# Indian and Alaska Native, some other race, and two or more races, all
# counted; in 2020 two or more races is 12,196 of its 13,945. Sentence case,
# which is Urban's rule for all text inside a figure.
OTHER_LABEL = "Other or Multiracial"


# --- output profiles --------------------------------------------------------
# Same figure code, two destinations. Width and text size differ; nothing else.
PROFILES = {
    # Urban's full-width PDF figure. Goes into the memo at natural size.
    "print": {"width": 6.25, "scale": 1.0, "dpi": 300, "format": "pdf"},
    # The deck, read on a laptop. Wider, and every size stepped up with it so
    # the type holds the same proportion to the frame.
    "screen": {"width": 10.0, "scale": 1.45, "dpi": 200, "format": "png"},
}
DEFAULT_PROFILE = "print"

# Figure heights, as a fraction of the profile's width. Named here rather than
# passed per script: three ad-hoc numbers in three files is how a set of
# figures stops looking like a set.
#
# Every figure is the same width. What differs is height, and how many panels
# share that width - a two-panel figure gives each panel about half, which is
# why its bars read narrower than a single-panel chart's even though the frame
# is identical.
SEATS = 0.52       # the 0-5 seat charts: a short frame, five gridlines
SERIES = 0.62      # a single panel of lines over time
PANELS = 0.80      # two panels side by side, each needing height to compensate

# 1932: the Board expands from three to five seats and magisterial districts
# are replaced by at-large elections. Drawn identically wherever it appears.
EXPANSION_YEAR = 1932
# Two namings. On a 0-5 seat axis the expansion is what the axis shows, so the
# numbers are worth stating; elsewhere it is context. That the districts became
# at-large is carried by the prose in both cases.
EXPANSION_NOTE = "1932 Board expansion"
EXPANSION_NOTE_SEATS = "1932: Board expands from 3 to 5 seats"
EXPANSION_LINE = dict(color="#000000", lw=1.0, ls=(0, (4, 2)))


def _register_fonts():
    """Make the bundled Lato findable without installing anything.

    Urban's typeface, and its type scale assumes it. The files are bundled
    under the OFL so a clone builds identical figures with no font install -
    the same standard the build holds for data.
    """
    for ttf in sorted(FONTS.glob("*.ttf")):
        font_manager.fontManager.addfont(str(ttf))



def apply(profile=DEFAULT_PROFILE):
    """Load Urban's rcParams, then this profile's width and type scale.

    Returns the profile, because figure code needs its width and format.
    """
    if profile not in PROFILES:
        raise KeyError(f"unknown profile {profile!r}; have {sorted(PROFILES)}")
    _register_fonts()
    mpl.style.use(str(MPLSTYLE))
    spec = PROFILES[profile]

    scale = spec["scale"]
    for key in ("font.size", "axes.labelsize", "axes.titlesize", "xtick.labelsize",
                "ytick.labelsize", "legend.fontsize", "figure.titlesize",
                "axes.titlepad", "axes.labelpad"):
        mpl.rcParams[key] = mpl.rcParams[key] * scale
    mpl.rcParams["savefig.dpi"] = spec["dpi"]
    return spec


def figsize(height_ratio=0.62, profile=DEFAULT_PROFILE):
    """Figure size for this profile at a given height-to-width ratio."""
    w = PROFILES[profile]["width"]
    return (w, w * height_ratio)


# Every figure's plotting area begins at the same fraction of the canvas, so a
# reader stacking two of them in a document sees their frames line up. Left to
# itself, constrained layout sizes each axes to its own tick labels: "0" to "5"
# on a seat chart needs far less room than "250,000" on a population one, and
# the two figures then start in different places despite being the same width.
# The value is the widest any current figure needs, with a little room; align()
# raises if a figure ever needs more rather than silently clipping its labels.
PLOT_LEFT = 0.135
PLOT_RIGHT = 0.984


def despine(ax):
    """Kept for figures that need it explicitly; the style already does it."""
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
