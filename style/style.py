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

DARK = "#5C5859"          # a reference series

# One table per subject: column -> (legend label, colour), in stacking
# order, axis upward.
RACE = {
    "black": ("Black", OKABE_ITO["orange"]),
    "hisp":  ("Hispanic or Latino", OKABE_ITO["bluish_green"]),
    "aapi":  ("Asian & Pacific Islander", OKABE_ITO["blue"]),
    "white": ("White", SAND),
}
RESIDUAL = ("Other or Multiracial", GREY)
RESIDENTS = {**{k: RACE[k] for k in ("black", "hisp", "aapi")},
             "other": RESIDUAL, "white": RACE["white"]}
GENDER = {
    "women": ("women", OKABE_ITO["reddish_purple"]),
    "men":   ("men", SAND),
}
PARTY = {
    "dem":        ("Democratic", OKABE_ITO["sky_blue"]),
    "abc":        ("ABC", OKABE_ITO["yellow"]),
    "unrecorded": ("not recorded", UNRECORDED),
    "ind":        ("independent", GREY),
    "rep":        ("Republican", OKABE_ITO["vermilion"]),
}
VOTERS = {"dem": PARTY["dem"], "other": ("other", GREY), "rep": PARTY["rep"]}
BOARD_VOTE = {**{k: PARTY[k] for k in ("dem", "abc", "unrecorded")},
              "other": ("other", GREY), "rep": PARTY["rep"]}
POPULATION = ("total population", DARK)
PER_SEAT = ("residents per seat", OKABE_ITO["vermilion"])
# Which sitting members have a birth year: the mass in sand, none in the
# no-evidence grey.
AGE_COVERAGE = {
    "known":   ("with a birth year", SAND),
    "unknown": ("without", UNRECORDED),
}
# The sitting Board's ages: the envelope in the stroke neutral, the median dark.
AGES = {
    "oldest":   ("oldest", SAND_LINE),
    "median":   ("median", DARK),
    "youngest": ("youngest", SAND_LINE),
}
# The sitting Board by age band, youngest at the base; the members with no
# birth year in the no-evidence grey on top.
AGE_BANDS = {
    "under40": ("under 40", OKABE_ITO["bluish_green"]),
    "40to59":  ("40 to 59", SAND),
    "60plus":  ("60 and over", OKABE_ITO["orange"]),
    "unknown": ("no birth year", UNRECORDED),
}
# How exactly the sitting Board's homes are known: one hue, darker the more
# exactly the place is named, and the no-evidence grey for no place at all.
RESIDENCE = {
    "address":      ("street address", "#1B6B4A"),
    "street":       ("street name", "#4FA37D"),
    "neighborhood": ("neighborhood", "#9CCFB3"),
    "side":         ("north/south side", "#D3EBDD"),
    "none":         ("no place found", UNRECORDED),
}
PRESIDENT = ("voted for President", DARK)
CYCLE = {
    "president": ("presidential year", OKABE_ITO["vermilion"]),
    "governor":  ("governor's year", OKABE_ITO["orange"]),
    "midterm":   ("midterm year", OKABE_ITO["bluish_green"]),
    "delegates": ("House of Delegates year", OKABE_ITO["black"]),
}

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
