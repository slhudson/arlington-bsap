"""Visual conventions. Every figure imports these; none redeclares them.

This folder holds how a number is *shown*, separately from code/analysis/,
which holds the substance. It sits outside code/ because most of it cannot be
executed - a typeface, and a table of rcParams - and code/ is for things you
can run.

The separation is structural rather than a habit: there is no files.py here, so
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
GREY = "#8C8C8C"          # the residual: other, multiracial or unreported

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
GENDER_COLORS = {
    "women": OKABE_ITO["reddish_purple"],
    "men":   OKABE_ITO["sky_blue"],
}
# The growth figure: two counts of people, no categories.
SERIES_COLORS = {"population": "#5C5859", "per_seat": OKABE_ITO["blue"]}

RESIDUAL_COLOR = GREY

# Stacking order, axis upward.
GROUP_ORDER = ["black", "hisp", "aapi", "white"]
GROUP_LABELS = {
    "black": "Black",
    "hisp": "Hispanic/Latino",
    "aapi": "Asian/Pacific Islander",
    "white": "White",
}

# The census basis, 1980 on: five groups that partition the county. Same
# colours, so a reader moving between the two bases is not relearning them.
CENSUS_ORDER = ["nh_black", "hispanic", "nh_aapi", "nh_white", "nh_other"]
# On this basis every group except Hispanic/Latino is non-Hispanic, so a legend
# that says so five times repeats itself; the caption says it once. Five long
# labels also cannot fit one row at Urban's width, and one row is the rule.
CENSUS_LABELS = {
    "nh_black": "Black",
    "hispanic": "Hispanic/Latino",
    "nh_aapi": "Asian/Pacific Islander",
    "nh_white": "White",
    "nh_other": "Other or multiracial",
}

GENDER_ORDER = ["women", "men"]
GENDER_LABELS = {"women": "Women", "men": "Men"}

# The residual band on the old basis: everything the four categories miss.
OTHER_LABEL = "Other, multiracial or unreported"


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
                "ytick.labelsize", "legend.fontsize", "figure.titlesize"):
        mpl.rcParams[key] = mpl.rcParams[key] * scale
    mpl.rcParams["savefig.dpi"] = spec["dpi"]
    return spec


def figsize(height_ratio=0.62, profile=DEFAULT_PROFILE):
    """Figure size for this profile at a given height-to-width ratio."""
    w = PROFILES[profile]["width"]
    return (w, w * height_ratio)


def despine(ax):
    """Kept for figures that need it explicitly; the style already does it."""
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
