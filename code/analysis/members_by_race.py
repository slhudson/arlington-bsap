"""Board seats by race/ethnicity, 1870-2026 -> figures/members_by_race.pdf, .png

A stacked step area of seat-years in style.RACE, on the frame
members_by_gender and members_by_party share, with the 1932 rule. Blank
years are gaps. A category with no seat in any year gets no band and no
legend entry.
"""
import charts
import members
import paths
import style

race = {k: (style.CROSSED_LABELS.get(k, label), colour) for k, (label, colour) in style.RACE.items()}

for profile in style.PROFILES:
    style.apply(profile)

    d = paths.read("members_by_year")
    fig = charts.seat_bands(profile, d, race, through=members.LAST + 1)
    paths.save(fig, profile)
