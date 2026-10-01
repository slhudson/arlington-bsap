"""Board seats by party, 1932-2026 -> figures/members_by_party.pdf, .png

A stacked step area of seat-years in style.PARTY, on the frame
members_by_race and members_by_gender share, with the 1932 rule. Party is
recorded only from the at-large Board, so the years before it are gaps. A
category with no seat in any year gets no band and no legend entry.
"""
import charts
import members
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = paths.read("members_by_year")
    fig = charts.seat_bands(profile, d, style.PARTY, through=members.LAST + 1)
    paths.save(fig, profile)
