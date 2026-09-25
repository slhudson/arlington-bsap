"""Visual conventions. Every figure imports these; none redeclares them.

The values only. The reasoning behind each, and the departures from the
Urban Institute style guide that urban.mplstyle loads, are in
docs/figures.md.
"""
import pathlib

import matplotlib as mpl
import matplotlib.style
from matplotlib import font_manager

HERE = pathlib.Path(__file__).resolve().parent
MPLSTYLE = HERE / "urban.mplstyle"
FONTS = HERE / "fonts"

# Okabe and Ito's Color Universal Design set.
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
SAND = "#D9D3C4"          # the largest group, as a fill
SAND_LINE = "#A3997F"     # the same, as a stroke
GREY = "#8C8C8C"          # the residual
UNRECORDED = "#DDDDDD"    # no evidence

RACE_COLORS = {
    "black": OKABE_ITO["orange"],
    "hisp":  OKABE_ITO["bluish_green"],
    "aapi":  OKABE_ITO["blue"],
    "white": SAND,
}
GENDER_COLORS = {
    "women": OKABE_ITO["reddish_purple"],
    "men":   SAND,
}
SERIES_COLORS = {"population": "#5C5859", "per_seat": OKABE_ITO["vermilion"]}
TURNOUT_COLORS = {"president": "#5C5859"}
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
PARTY_COLORS = {
    "dem":        OKABE_ITO["sky_blue"],
    "abc":        OKABE_ITO["yellow"],
    "rep":        OKABE_ITO["vermilion"],
    "ind":        GREY,
    "unrecorded": UNRECORDED,
}
PARTY_ORDER = ["dem", "abc", "unrecorded", "ind", "rep"]        # axis upward
PARTY_LABELS = {
    "dem": "Democratic",
    "abc": "ABC",
    "rep": "Republican",
    "ind": "independent",
    "unrecorded": "not recorded",
}
VOTERS_ORDER = ["dem", "other", "rep"]
VOTERS_COLORS = {"dem": PARTY_COLORS["dem"], "other": GREY, "rep": PARTY_COLORS["rep"]}
VOTERS_LABELS = {"dem": "Democratic", "other": "other", "rep": "Republican"}
BOARD_VOTE_ORDER = ["dem", "abc", "unrecorded", "other", "rep"]
BOARD_VOTE_COLORS = {**PARTY_COLORS, "other": GREY}
BOARD_VOTE_LABELS = {**PARTY_LABELS, "other": "other"}

RESIDUAL_COLOR = GREY
GROUP_ORDER = ["black", "hisp", "aapi", "white"]                 # axis upward
GROUP_LABELS = {
    "black": "Black",
    "hisp": "Hispanic or Latino",
    "aapi": "Asian & Pacific Islander",
    "white": "White",
}
GENDER_ORDER = ["women", "men"]
GENDER_LABELS = {"women": "women", "men": "men"}
OTHER_LABEL = "Other or Multiracial"

# Same figure code, two destinations: the memo's PDF and the deck's PNG.
PROFILES = {
    "print": {"width": 6.25, "scale": 1.0, "dpi": 300, "format": "pdf"},
    "screen": {"width": 10.0, "scale": 1.45, "dpi": 200, "format": "png"},
}
DEFAULT_PROFILE = "print"

PLOT_ASPECT = 2.2     # every plot is this many times as wide as it is tall; charts.fit() solves the height
MARGIN = 0.037        # white on all four sides, as a fraction of the width, measured to ink
LEGEND_GAP = 0.2      # inches between the lowest ink of the plot and the legend

EXPANSION_YEAR = 1932
EXPANSION_NOTE = "1932 Board expansion"
EXPANSION_NOTE_SEATS = "1932: Board expands from 3 to 5 seats"
EXPANSION_LINE = dict(color="#000000", lw=1.0, ls=(0, (4, 2)))


def _register_fonts():
    """Make the bundled Lato findable without installing anything."""
    for ttf in sorted(FONTS.glob("*.ttf")):
        font_manager.fontManager.addfont(str(ttf))


def apply(profile=DEFAULT_PROFILE):
    """Load Urban's rcParams, then this profile's width and type scale.
    Returns the profile."""
    if profile not in PROFILES:
        raise KeyError(f"unknown profile {profile!r}; have {sorted(PROFILES)}")
    _register_fonts()
    mpl.style.use(str(MPLSTYLE))
    spec = PROFILES[profile]
    for key in ("font.size", "axes.labelsize", "axes.titlesize", "xtick.labelsize",
                "ytick.labelsize", "legend.fontsize", "figure.titlesize",
                "axes.titlepad", "axes.labelpad"):
        mpl.rcParams[key] = mpl.rcParams[key] * spec["scale"]
    mpl.rcParams["savefig.dpi"] = spec["dpi"]
    # Constrained layout's pad is in inches and MARGIN is a fraction of the width.
    pad = MARGIN * spec["width"]
    mpl.rcParams["figure.constrained_layout.h_pad"] = pad
    mpl.rcParams["figure.constrained_layout.w_pad"] = pad
    return spec


def figsize(profile=DEFAULT_PROFILE):
    """A starting size for this profile. charts.fit() sets the real height."""
    w = PROFILES[profile]["width"]
    return (w, w * 0.62)
