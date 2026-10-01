"""Board seats by gender, 1870-2026 -> figures/members_by_gender.pdf, .png

A stacked step area of seat-years, women then men, on the frame
members_by_race and members_by_party share, with the 1932 rule. Blank years
are gaps.
"""
import charts
import members
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = paths.read("members_by_year")
    fig = charts.seat_bands(profile, d, style.GENDER, through=members.LAST + 1)
    paths.save(fig, profile)
