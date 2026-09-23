"""Visual conventions. Every figure imports these; none redeclares them.

The conventions are the Urban Institute's data visualization style guide,

    https://urbaninstitute.github.io/graphics-styleguide/

loaded from urban.mplstyle. This module holds what rcParams cannot express:
the palette, the two output profiles, and which colour belongs to which group.

**Where this project departs from Urban, the departure is here with its
reason.** There are three.

*The palette is desaturated.* Urban's categorical colours are pitched for the
web and read hot on a printed page beside body text. The hues and their
ordering are Urban's; the saturation is not. LEVELS gives three candidates.

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

# --- Urban's palette, as published ------------------------------------------
# Categorical, in the guide's own order of preference.
URBAN = {
    "blue":    "#1696D2",
    "yellow":  "#FDBF11",
    "magenta": "#EC008B",
    "green":   "#55B748",
    "grey":    "#D2D2D2",
    "black":   "#000000",
    "red":     "#DB2B27",
}
# A darker neutral for a second residual band, from Urban's grey ramp.
URBAN_SPACE_GREY = "#5C5859"


def _mute(hexcolor, amount):
    """Pull a colour toward neutral, keeping its hue and lightness.

    Saturation only. Shifting lightness as well would change which bands read
    as heavier, which is a different decision from taking the heat out.
    """
    r, g, b = mpl.colors.to_rgb(hexcolor)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return mpl.colors.to_hex(colorsys.hls_to_rgb(h, l, s * (1 - amount)))


# Three candidates to choose between. Each is the whole palette at one
# saturation; the hues and their order never change.
LEVELS = {"soft": 0.25, "muted": 0.45, "quiet": 0.65}
PALETTES = {name: {k: _mute(v, amount) if k not in ("grey", "black") else v
                   for k, v in URBAN.items()}
            for name, amount in LEVELS.items()}
DEFAULT_LEVEL = "muted"

# --- which colour belongs to which group ------------------------------------
# Stacking order, axis upward. The neutral goes to the largest group; see the
# module docstring for why that is a departure from Urban's hierarchy.
GROUP_ORDER = ["black", "hisp", "aapi", "white"]
GROUP_HUES = {"black": "blue", "hisp": "yellow", "aapi": "magenta", "white": "grey"}
GROUP_LABELS = {
    "black": "Black",
    "hisp": "Hispanic/Latino",
    "aapi": "Asian/Pacific Islander",
    "white": "White",
}

# The census basis, 1980 on: five groups that partition the county. Same hues,
# so a reader moving between the two bases is not also relearning the colours.
CENSUS_ORDER = ["nh_black", "hispanic", "nh_aapi", "nh_white", "nh_other"]
CENSUS_HUES = {"nh_black": "blue", "hispanic": "yellow", "nh_aapi": "magenta",
               "nh_white": "grey", "nh_other": "spacegrey"}
# On this basis every group except Hispanic/Latino is non-Hispanic, so a legend
# that says so five times is repeating itself. The qualifier goes in the
# caption once: "groups other than Hispanic/Latino are non-Hispanic". Five long
# labels also cannot fit one row at Urban's 6.25in width, and one row is the
# rule.
CENSUS_LABELS = {
    "nh_black": "Black",
    "hispanic": "Hispanic/Latino",
    "nh_aapi": "Asian/Pacific Islander",
    "nh_white": "White",
    "nh_other": "Other or multiracial",
}

GENDER_ORDER = ["women", "men"]
GENDER_HUES = {"women": "blue", "men": "grey"}
GENDER_LABELS = {"women": "Women", "men": "Men"}

# The residual band on the old basis: everything the four categories miss.
OTHER_LABEL = "Other, multiracial or unreported"

# Two series that are both counts of people, on the growth figure.
SERIES_HUES = {"population": "spacegrey", "per_seat": "blue"}

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


def palette(level=DEFAULT_LEVEL):
    p = dict(PALETTES[level])
    p["spacegrey"] = URBAN_SPACE_GREY
    return p


def colors(order, hues, level=DEFAULT_LEVEL):
    """Colours for a group order, in stacking order."""
    p = palette(level)
    return [p[hues[g]] for g in order]


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
