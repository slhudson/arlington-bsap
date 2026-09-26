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

# The sequential profile: one hue, light to dark, for categories that are
# ordered. ramp(n) is n steps of it, lightest first; an ordered figure takes
# its colours from here and defines none of its own. See docs/figures.md.
SEQUENTIAL = ("#D3EBDD", "#1B6B4A")


def ramp(n):
    """n colours from the sequential profile, lightest first."""
    lo, hi = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in SEQUENTIAL)
    return ["#" + "".join(f"{round(a + (b - a) * k / (n - 1)):02X}" for a, b in zip(lo, hi))
            for k in range(n)]


# One table per subject: column -> (legend label, colour), in stacking
# order, axis upward.
RACE = {
    "black": ("Black", OKABE_ITO["orange"]),
    "hisp":  ("Hispanic or Latino", OKABE_ITO["bluish_green"]),
    "aapi":  ("Asian & Pacific Islander", OKABE_ITO["blue"]),
    "white": ("White", SAND),
}
RESIDUAL = ("Other or Multiracial", GREY)
# Black candidacies for the Board: the race figures' Black, filled for a
# seat won and an open ring for a race lost.
CANDIDACY = {"won": ("won", RACE["black"][1], True),
             "lost": ("lost", RACE["black"][1], False)}
# The county's crossed census tables, from 1980: race and Hispanic origin are
# two questions, so Black and White there are the non-Hispanic cells. Only
# the residents figure reads them; the Board's race is not a crosstab.
CROSSED_LABELS = {"black": "Black, not Hispanic", "white": "White, not Hispanic"}
CROSSED_YEAR = 1980
RESIDENTS = {**{k: RACE[k] for k in ("black", "hisp", "aapi")},
             "other": RESIDUAL, "white": RACE["white"]}
RESIDENTS_CROSSED = {k: (CROSSED_LABELS.get(k, label), colour)
                     for k, (label, colour) in RESIDENTS.items()}
# The county by age band, youngest at the base. Ordered, so it takes the
# sequential profile, darker with age.
RESIDENT_AGES = dict(zip(
    ("ageunder18", "age18to24", "age25to34", "age35to44", "age45to54", "age55to64", "age65plus"),
    zip(("under 18", "18 to 24", "25 to 34", "35 to 44", "45 to 54", "55 to 64", "65 and over"),
        ramp(7))))
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
# Arlington beside Virginia's other governing bodies: the others in two
# neutrals, Arlington in the per-seat vermilion. See docs/figures.md.
LOCALITIES = {
    "city":   ("city", DARK),
    "county": ("county", SAND_LINE),
}
ARLINGTON = OKABE_ITO["vermilion"]
# A scatter's dot, in points squared at scale 1; Arlington's a little larger.
DOT = 40
DOT_HIGHLIGHT = 70
# Which sitting members have a birth year: the mass in sand, none in the
# no-evidence grey.
AGE_COVERAGE = {
    "known":   ("with a birth year", SAND),
    "unknown": ("without", UNRECORDED),
}
# The sitting Board's ages on a Lexis diagram: the span from youngest to
# oldest in the near-neutral, each member's tenure a stroke in the dark grey.
AGE_SPAN = {
    "band":   ("youngest to oldest sitting", SAND),
    "member": ("member", DARK),
}
# How exactly the sitting Board's homes are known: ordered, so the sequential
# profile, darker the more exactly the place is named, and the no-evidence
# grey for no place at all.
RESIDENCE = dict(zip(
    ("address", "street", "neighborhood", "side_or_district"),
    zip(("street address", "street name", "neighborhood", "north/south side or district"),
        reversed(ramp(4)))))
RESIDENCE["none"] = ("no location", UNRECORDED)
PRESIDENT = ("voted for President", DARK)
CYCLE = {
    "president": ("presidential year", OKABE_ITO["vermilion"]),
    "governor":  ("governor's year", OKABE_ITO["orange"]),
    "midterm":   ("midterm year", OKABE_ITO["bluish_green"]),
    "delegates": ("House of Delegates year", OKABE_ITO["black"]),
}

# Same figure code, two destinations: the memo's PDF and the deck's PNG.
PROFILES = {
    "print": {"width": 6.25, "scale": 1.0, "dpi": 300, "format": "pdf", "aspect": 2.2},
    "screen": {"width": 10.0, "scale": 1.45, "dpi": 200, "format": "png", "aspect": 3.0},
}
DEFAULT_PROFILE = "print"

# Each profile's "aspect" is how many times as wide as tall its plot is;
# charts.fit() solves the height from it. See docs/figures.md, Size and margins.
NARROW = 0.7          # the fraction of the profile's width a few-category figure takes; see docs/figures.md
SQUARE = 1.2          # the aspect of a scatter, whose two axes are both measures; see docs/figures.md
STRIP = 7.0           # the aspect of a timeline of events, whose y axis carries no measure; see docs/figures.md
BROKEN = (5, 1)       # widths of the two sides of a broken x axis, near and far
MARGIN = 0.037        # white on all four sides, as a fraction of the width, measured to ink
LEGEND_GAP = 0.2      # inches between the lowest ink of the plot and the legend

EXPANSION_YEAR = 1932
EXPANSION_NOTE = "1932: Board expands from 3 to 5 seats"
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


def figsize(profile=DEFAULT_PROFILE, of_width=1.0):
    """A starting size for this profile. charts.fit() sets the real height."""
    w = PROFILES[profile]["width"] * of_width
    return (w, w * 0.62)
