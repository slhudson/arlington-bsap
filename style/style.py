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
# two questions, so Black and White there are the non-Hispanic cells. The
# residents figure reads them from 1980; the Board figure reads the same labels.
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
ELECTIONS_RESULTS = {"dem": PARTY["dem"], "other": ("other", GREY), "rep": PARTY["rep"]}
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
# What the sitting Board's race rests on: ordered, so the sequential profile,
# darker the more direct the source, and the no-evidence grey for the default.
RACE_BASIS = dict(zip(
    ("census", "published"),
    zip(("race from a census sheet", "race from the press or a profile"), reversed(ramp(2)))))
RACE_BASIS["default"] = ("assumed White, no source", UNRECORDED)
# The sitting Board's ages on a Lexis diagram: the span from youngest to
# oldest in the near-neutral, each member's tenure a stroke in the dark grey.
# The county's own adult median age is a dashed reference line over it, in
# the one saturated colour the figure uses. See docs/figures.md.
AGE_SPAN = {
    "band":   ("member age range", SAND),
    "member": ("member age", DARK),
    "county_median": ("county adult median age", OKABE_ITO["vermilion"]),
}
# How exactly the sitting Board's homes are known: ordered, so the sequential
# profile, darker the more exactly the place is named, and the no-evidence
# grey for no place at all.
RESIDENCE = dict(zip(
    ("address", "street", "neighborhood", "side_or_district"),
    zip(("street address", "street name", "neighborhood", "north/south side or district"),
        reversed(ramp(4)))))
RESIDENCE["none"] = ("no location", UNRECORDED)
# The three magisterial districts, with the county behind them as the
# reference: three unordered places, so Okabe-Ito, and the county in the
# reference neutral the growth and peer figures use. See docs/figures.md.
DISTRICTS = {
    "Arlington":  ("Arlington District", OKABE_ITO["bluish_green"]),
    "Jefferson":  ("Jefferson District", OKABE_ITO["blue"]),
    "Washington": ("Washington District", OKABE_ITO["reddish_purple"]),
}
WHOLE_COUNTY = ("Arlington County", DARK)


def tint(color, strength):
    """`color` mixed toward white: strength 1 is the colour itself, 0 is
    white. For land that is the same place under a later name."""
    rgb = mpl.colors.to_rgb(color)
    return mpl.colors.to_hex(tuple(1 - strength * (1 - c) for c in rgb))


# The land Alexandria annexed was Jefferson district's, so each year is a
# tint of Jefferson's blue, the earlier the darker. See docs/figures.md.
ANNEXED = {
    "annexed 1915": ("annexed by Alexandria, 1915", tint(DISTRICTS["Jefferson"][1], 0.55)),
    "annexed 1930": ("annexed by Alexandria, 1930", tint(DISTRICTS["Jefferson"][1], 0.28)),
}
# A map of the county is taller than wide, so it takes this fraction of the
# profile's width rather than the whole. See docs/figures.md.
MAP_WIDTH = 0.5
# A map's corner legend: a swatch is this many times the type's height, an
# entry set in under the one above is moved in by this many swatches, and the
# line between two areas is this many points wide.
SWATCH = 1.0
INDENT = 1.6
AREA_EDGE = 0.6

PRESIDENT = ("votes for President", DARK)
# The two presidential years with no state return found, drawn hollow on the line.
# The Board's own vote before 1931, set against the presidential vote: the
# per-seat vermilion, as the other Board series before the expansion take.
BOARD_VOTE_DISTRICTS = ("votes for County Board", OKABE_ITO["vermilion"])
# The two dated changes to who could vote that the pre-1932 turnout figures
# rule off: (year, note, which side of the rule the note runs to), so two
# notes eight years apart do not meet above the frame.
ELECTORATE_RULES = ((1894, "1894: Walton Act", "right"),
                    (1902, "1902: new constitution", "left"))
# The county-wide figure runs to 1928 and adds the year women vote; the
# by-district figure ends in 1919 and does not.
ELECTORATE_RULES_TO_1932 = ELECTORATE_RULES + ((1920, "1920: women vote", "left"),)
CYCLE = {
    "president": ("presidential year", OKABE_ITO["vermilion"]),
    "governor":  ("governor's year", OKABE_ITO["orange"]),
    "midterm":   ("midterm year", OKABE_ITO["bluish_green"]),
    "delegates": ("House of Delegates year", OKABE_ITO["black"]),
}

# The ranked choice voting survey's five-point support scale, left to right,
# in the same hues as AGREEMENT: the slides the County Board saw use green to
# red, which is the one pairing a red-green colourblind reader cannot separate
# at the two ends that matter. See docs/figures.md.
SUPPORT = {
    "Yes, Strongly Support": ("strongly support", OKABE_ITO["blue"]),
    "Yes, Somewhat Support": ("somewhat support", OKABE_ITO["sky_blue"]),
    "Not Sure":              ("not sure", UNRECORDED),
    "No, Somewhat Oppose":   ("somewhat oppose", OKABE_ITO["orange"]),
    "No, Strongly Oppose":   ("strongly oppose", OKABE_ITO["vermilion"]),
}

# The survey's five-point agreement and satisfaction scales, left to right.
# Bipolar rather than ordered by magnitude, so two hues from Okabe-Ito rather
# than the sequential ramp, and the middle point takes the no-evidence grey:
# on the Board's structure it is an abstention and not a midpoint. See
# docs/figures.md.
AGREEMENT = {
    "Strongly Agree":    ("strongly agree", OKABE_ITO["blue"]),
    "Agree":             ("agree", OKABE_ITO["sky_blue"]),
    "Neutral":           ("neutral", UNRECORDED),
    "Disagree":          ("disagree", OKABE_ITO["orange"]),
    "Strongly Disagree": ("strongly disagree", OKABE_ITO["vermilion"]),
}
# The survey's three waves. Ordered, so the sequential profile, darkest latest.
WAVES = dict(zip((2018, 2022, 2026), zip(("2018", "2022", "2026"), ramp(3))))
# The sample set against the county it is drawn from: the county in the
# reference neutral the growth figures use, the respondents in the lead.
SAMPLE = {"county": ("Arlington residents, 2020 census", DARK),
          "survey": ("survey respondents", OKABE_ITO["vermilion"])}
# One share measured across several cuts of one set of respondents: one
# series, so one colour, and the near-neutral rather than a lead.
SURVEY_SHARE = ("share of respondents", SAND_LINE)
# A document naming the Board either records who held a seat or who won one
# - the one substantive distinction among the sources themselves, so it
# stays in the one neutral family rather than taking a category's hue.
SOURCE_KIND = {
    "election": ("members elected", SAND),
    "service": ("members served", SAND_LINE),
}
# The gap between two blocks of a horizontal bar chart, in bar widths.
GROUP_GAP = 0.8

# Same figure code, two destinations: the memo's PDF and the deck's PNG.
PROFILES = {
    "print": {"width": 6.25, "scale": 1.0, "dpi": 300, "format": "pdf", "aspect": 2.2},
    "screen": {"width": 10.0, "scale": 1.45, "dpi": 200, "format": "png", "aspect": 3.0},
}
DEFAULT_PROFILE = "print"

# Each profile's "aspect" is how many times as wide as tall its plot is;
# charts.fit() solves the height from it. See docs/figures.md, Size and margins.
NARROW = 0.7          # the fraction of the profile's width a few-category figure takes; see docs/figures.md
SQUARE = 2.0          # the aspect of a scatter, whose two axes are both measures; see docs/figures.md
PAIR = 0.88           # the aspect of two scatters stacked one above the other, each the SQUARE shape at full width, filling most of a page; see docs/figures.md
STRIP = 7.0           # the aspect of a timeline of events, whose y axis carries no measure; see docs/figures.md
SPAN_TICK = 0.6        # the width, in years, of a dated item drawn as a tick on an hspans() row; see docs/figures.md
BROKEN = (5, 1)       # widths of the two sides of a broken x axis, near and far
MARGIN = 0.037        # white on all four sides, as a fraction of the width, measured to ink
LEGEND_GAP = 0.2      # inches between the lowest ink of the plot and the legend
DENSE_TICKS = 0.85    # tick label size, as a fraction of the profile's, where an axis names every year of a close sequence; see docs/figures.md

EXPANSION_YEAR = 1932
EXPANSION_NOTE = "1932: Board expansion"
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
