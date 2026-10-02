# Localities

This write-up covers the governing body of every Virginia locality Arlington's
Board is set beside, and how large each place is: what each number in
`data/clean/localities.csv` is, what backs it, and what is assumed where nothing
does. How a decision was reached is in the git history rather than here.
`code/citekeys.py` explains the placeholders in the `source` columns, and
`docs/questions.csv` holds what is still open.


## What rests on an assumption

Nothing. Which localities are shown is a decision, and it is below.

---


## The peer set
`localities.csv` sets Arlington's Board beside the governing body of every
Virginia independent city and of fourteen counties: the thirteen largest
other than Arlington, and Rockingham. The figures show those of 100,000
residents or more and leave the choice of peer to the
reader: places Arlington's size in `localities_residents`, places as dense
in `localities_density`.

A city's council is the Richmond Charter Review Commission's count
(`richmond2023`, Appendix D). A Mayor elected at large counts as a member,
because the appendix's notes say most vote on council; Richmond's is the one
the notes name as sitting outside it. A Mayor chosen from council is already
among its members. A county board's count includes a chair elected at large.
Residents are the 2020 census; land area is the 2020 Gazetteer's.

Each Arlington member stands for about as many residents as each member
in Loudoun and Virginia Beach, and for far more than each member in a city
of its size. Alexandria, the one place as dense, has far fewer residents per
member; only the larger counties, Henrico, Chesterfield, Prince William and
Fairfax, have more.


## Southeastern cities and counties of Arlington's size

`localities_southeastern.csv` sets the Board's five members beside eighty
governing bodies of 150,000 to 300,000 residents in ten southeastern states:
26 cities and 54 counties. Each row is seats and residents, and from them
residents per member, the measure the Virginia figures use. The set is a rule,
not a selection: every incorporated place, and every county or parish, with
150,000 to 300,000 residents in the 2020 census in the nine states Appendix E
of the Richmond charter review names (Alabama, Arkansas, Georgia, Louisiana,
Mississippi, North Carolina, South Carolina, Tennessee and Virginia) and in
Maryland. Maryland has no incorporated place that size, so it enters by county.
The build stops if the rule finds a body no table keys, or a table keys one
the rule does not find. The states are the commission's choice of region and
the floor and the counties are ours: the commission's 180,000 floor and its
cities-only list answer Richmond's question, and Arlington's form of
government is a county's.

A county is left out where the Bureau's county is not the body that governs
it. Virginia's independent cities are counted as cities, and three Georgia
counties are the consolidated governments of Augusta, Columbus and
Macon-Bibb County, counted once as those cities. Arlington is the subject, not
a peer.

A body's seats come from the place that holds its count. The nineteen cities
Appendix E tabulates are its council members (`richmond2023`, printed p. 122),
a Mayor who sits and votes counted as one seat, which is why its Norfolk is
eight and Appendix D's seven plus an at-large Mayor; Alexandria and Stafford are
Virginia's own rows above. Every other body is keyed from its own charter or
official page (`southeastern_bodies.csv`, one citekey per body). The same rule
holds throughout: every member who sits and votes counts, a chair or Mayor
elected at large included; a chief executive who does not sit, or who votes
only to break a tie, does not. Residents are the 2020 census count for the
place or county, not the source's.

Arlington carries about 48,000 residents per member. Five peers carry more:
Clayton, Baldwin, Cherokee, Forsyth and Lafayette, all counties of five seats
or fewer. The other 75 carry between 7,000 and 48,000. Cities top out at
about 43,000, in Huntsville, which has five seats; the lowest are Tennessee's
county commissions, Sullivan, Sumner and Williamson with 24 seats each. `localities_southeastern` shows it, cities and
counties in two colours.

The appendix also prints how each council is elected, ward or at large. It is
keyed but not used: proportional at-large methods mean at-largeness does not
by itself say how well a council represents.

What rests on an assumption: that the appendix's counts are the councils that
sat in 2023; the report states no date for the table. Each other body's count
is the one its page shows in September and October 2026. Clarksville is
twelve ward seats; a 2009 Tennessee Attorney General opinion reads its
charter as giving the Mayor a vote, which would make thirteen. St. Tammany's
council may change after a special election on 3 November 2026. Where a page
lists members without stating the structure in words (Hall, Cherokee, Henry,
Paulding, Davidson, Onslow, Sullivan, Anderson, Beaufort), the count is the
roster's.

## Non-interference clauses in city charters

The Virginia city charters carry non-interference clauses of their own: most
have some clause, some are stronger than § 15.2-703, and some have none. Only
Alexandria and Danville share Arlington's carve-out letting the board discuss
personnel with the manager.
