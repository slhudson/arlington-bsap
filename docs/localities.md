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


## Southeastern cities of Arlington's size

`localities_southeastern.csv` sets the Board's five members beside nineteen
cities of 180,000 to 300,000 residents in nine southeastern states,
Richmond among them: council seats and residents, and from them residents per
member, the measure the Virginia figures use. The set is a rule, not a
selection: every incorporated place with 180,000 to 300,000 residents in the
2020 census in the nine states Appendix E names (Alabama, Arkansas, Georgia,
Louisiana, Mississippi, North Carolina, South Carolina, Tennessee and
Virginia). The Census Bureau's 2020 place populations (`censusapi`) give
exactly these nineteen, and the build stops if the appendix and the rule
disagree. Mississippi and South Carolina have none that size. The nine states
are the commission's choice of region, not ours; 81 places nationally, census-designated places included, fall in
the size range. The appendix (`richmond2023`, printed p. 122) was compiled
for Richmond and holds no county, where Arlington's form of government sits.

A city's seats are the appendix's council members. The appendix counts a Mayor
who sits and votes as one seat, which is why its Norfolk is eight and Appendix
D's seven plus an at-large Mayor, and leaves out the Mayor of a city where the
Mayor is chief executive without a seat, Richmond among them. Residents are the
appendix's thousands, so a peer's figure is good to the nearest thousand;
Arlington's is the 2020 census total.

Arlington carries about 48,000 residents per member, more than any of the
nineteen; Huntsville, with five seats, is next at about 43,000, and the rest
carry between 18,000 and 41,000. `localities_southeastern` shows it.

The appendix also prints how each council is elected, ward or at large. It is
keyed but not used: proportional at-large methods mean at-largeness does not
by itself say how well a council represents.

What rests on an assumption: that the appendix's counts are the councils that
sat in 2023. The report states no date for the table.

## Non-interference clauses in city charters

The Virginia city charters carry non-interference clauses of their own: most
have some clause, some are stronger than § 15.2-703, and some have none. Only
Alexandria and Danville share Arlington's carve-out letting the board discuss
personnel with the manager.
