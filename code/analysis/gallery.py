"""Every chart type, in both profiles and each candidate palette.

    .venv/bin/python code/analysis/gallery.py

Not a run.sh step and not a report figure: it writes to figures/gallery/, which
run.sh does not scan. It exists so the style layer can be judged as a whole -
one sheet to react to rather than five figures one at a time - and so a palette
is chosen against the same real data the report uses, not against swatches.

Each palette sheet also shows the colours in greyscale and under simulated
red-green colourblindness. Desaturating a palette makes those two harder, not
easier, so the cost of the choice should be visible next to the benefit.
"""
import pathlib
import sys

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import charts
import files
import style

OUT = files.FIGURES / "gallery"

# Brettel-style linear approximation, adequate for judging whether two bands
# stay apart. Not a clinical simulation.
DEUTER = np.array([[0.625, 0.375, 0.0], [0.7, 0.3, 0.0], [0.0, 0.3, 0.7]])


def simulate(hexcolor, matrix=DEUTER):
    rgb = np.array(plt.matplotlib.colors.to_rgb(hexcolor))
    return plt.matplotlib.colors.to_hex(np.clip(matrix @ rgb, 0, 1))


def greyscale(hexcolor):
    r, g, b = plt.matplotlib.colors.to_rgb(hexcolor)
    v = 0.299 * r + 0.587 * g + 0.114 * b
    return plt.matplotlib.colors.to_hex((v, v, v))


def residents():
    d = pd.read_csv(files.RESIDENTS)
    return d


def board():
    return pd.read_csv(files.BOARD_SEATS)


def palette_sheet(level):
    """The palette as swatches, in colour, greyscale and simulated deuteranopia."""
    style.apply("print")
    p = style.palette(level)
    keys = ["blue", "yellow", "magenta", "green", "grey", "spacegrey"]
    fig, axes = plt.subplots(3, 1, figsize=(6.25, 2.6))
    for ax, (name, fn) in zip(axes, [("colour", lambda c: c),
                                     ("greyscale", greyscale),
                                     ("deuteranopia", simulate)]):
        for i, k in enumerate(keys):
            ax.add_patch(Rectangle((i, 0), 0.92, 1, facecolor=fn(p[k])))
            if name == "colour":
                ax.text(i + 0.46, -0.18, k, ha="center", va="top",
                        fontsize=plt.rcParams["font.size"] * 0.9)
        ax.set_xlim(-0.1, len(keys)); ax.set_ylim(0, 1)
        ax.set_ylabel(name, rotation=0, ha="right", va="center")
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
    amount = style.LEVELS[level]
    caption = ("the palette these figures already used (Okabe-Ito)"
               if amount is None else f"saturation reduced {int(amount * 100)}%")
    fig.suptitle(f"palette: {level}  ({caption})")
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"palette_{level}.png", dpi=200)
    plt.close(fig)


def chart_sheet(level, profile):
    """Every chart type the report uses, at one palette and one profile."""
    style.apply(profile)
    p = style.palette(level)
    d, b = residents(), board()
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. line: growth
    fig, ax = charts.figure(0.62, profile)
    g = d[["year", "total", "residents_per_seat"]].dropna()
    series = {
        "total population": (g.total, p[style.SERIES_HUES["population"]]),
        "residents per\nBoard seat": (g.residents_per_seat, p[style.SERIES_HUES["per_seat"]]),
    }
    charts.lines(ax, g.year, series)
    charts.counts(ax, 250000, 50000)
    # Decades collide at this width, so ticks every 20 years; headroom for the
    # end labels, which sit inside the axes.
    charts.years(ax, 1870, 2020, step=20, headroom=0.30)
    charts.end_labels(ax, g.year, series)
    charts.rule(ax)
    files_save(fig, f"{level}_{profile}_1_growth")

    # 2 & 3. stacked bars: census basis, counts and shares, side by side
    fig, (a1, a2) = charts.panels(0.80, profile)
    c = d[d.hispanic.notna()]
    order, hues, labels = style.CENSUS_ORDER, style.CENSUS_HUES, style.CENSUS_LABELS
    series = {labels[g]: (c[g].to_numpy(), p[hues[g]]) for g in order}
    charts.stacked_bars(a1, c.year, series, width=7)
    charts.counts(a1, 250000, 50000)
    charts.years(a1, 1980, 2020, rotate=True)
    a1.set_title("(a) number of residents")
    sh = {labels[g]: (c[g].to_numpy() / c.total.to_numpy() * 100, p[hues[g]]) for g in order}
    charts.stacked_bars(a2, c.year, sh, width=7)
    charts.shares(a2)
    charts.years(a2, 1980, 2020, rotate=True)
    a2.set_title("(b) share of residents")
    charts.legend(fig, {labels[g]: p[hues[g]] for g in order})
    files_save(fig, f"{level}_{profile}_2_residents_census_basis")

    # 4. stacked steps: board race
    fig, ax = charts.figure(0.52, profile)
    spans = charts.runs(b.white.notna().to_numpy())
    held = [g for g in style.GROUP_ORDER if b[g].fillna(0).sum() > 0]
    charts.stacked_steps(ax, b.year.to_numpy(),
                         {style.GROUP_LABELS[g]: (b[g].fillna(0).to_numpy(),
                                                  p[style.GROUP_HUES[g]]) for g in held},
                         spans)
    charts.seats(ax)
    charts.years(ax, 1880, 2020, step=20, label="year")
    ax.set_xlim(1866, 2027)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS, y=0.95)
    charts.legend(fig, {style.GROUP_LABELS[g]: p[style.GROUP_HUES[g]] for g in held})
    files_save(fig, f"{level}_{profile}_3_board_race")

    # 5. stacked steps: board gender
    fig, ax = charts.figure(0.52, profile)
    spans = charts.runs(b.women.notna().to_numpy())
    charts.stacked_steps(ax, b.year.to_numpy(),
                         {style.GENDER_LABELS[g]: (b[g].fillna(0).to_numpy(),
                                                   p[style.GENDER_HUES[g]])
                          for g in style.GENDER_ORDER}, spans)
    charts.seats(ax)
    charts.years(ax, 1880, 2020, step=20, label="year")
    ax.set_xlim(1866, 2027)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS, y=0.95)
    charts.legend(fig, {style.GENDER_LABELS[g]: p[style.GENDER_HUES[g]]
                        for g in style.GENDER_ORDER})
    files_save(fig, f"{level}_{profile}_4_board_gender")


def files_save(fig, stem):
    fig.savefig(OUT / f"{stem}.png", dpi=170)
    plt.close(fig)


def main():
    for level in style.LEVELS:
        palette_sheet(level)
        for profile in style.PROFILES:
            chart_sheet(level, profile)
    made = sorted(OUT.glob("*.png"))
    print(f"  figures/gallery/  {len(made)} sheets")
    for m in made:
        print(f"    {m.name}")


if __name__ == "__main__":
    main()
