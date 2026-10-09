"""Board seats by race and gender together, 1870-2026
-> figures/members_by_race_gender.pdf, .png

Before 1932 the three bands are the three district seats, each coloured by
who held it; from 1932 a stacked step area of seat-years, one band per
combination, the smallest group at the bottom, with the 1932 rule. docs/figures.md has the colours and the
legend grid.
"""
import charts
import members
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)
    d = paths.read("members_by_year")
    fig, ax = charts.figure(profile)

    at_large = d[d.year >= style.EXPANSION_YEAR]
    columns = list(style.RACE_GENDER)
    # Smallest group at the bottom, by seat-years over the whole record.
    held = sorted((c for c in columns if d[c].sum() > 0), key=lambda c: d[c].sum())
    # The one exception: Latina women sit just under White women (docs/figures.md).
    if "hisp_women" in held:
        held.remove("hisp_women")
        held.insert(held.index("white_women"), "hisp_women")
    ordered = {k: style.RACE_GENDER[k] for k in held}
    spans = charts.runs(at_large[columns].notna().any(axis=1).to_numpy())
    bands = charts.series(at_large.fillna(0), {k: (k, c) for k, (_, c) in ordered.items()})
    charts.stacked_steps(ax, at_large.year.to_numpy(), bands, spans)
    roster = paths.read("members")
    charts.district_lanes(ax, roster)

    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year", through=members.LAST + 1,
                 begin=roster.held_from.min() / 12)
    charts.rule(ax)
    charts.legend_grid(fig, style.RACE_GENDER_GRID, style.RACE_GENDER, held)
    paths.save(fig, profile)
