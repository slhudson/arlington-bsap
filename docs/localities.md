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

`localities_southeastern.csv` sets the Board's five at-large members beside
nineteen cities of 180,000 to 300,000 residents in nine southeastern states,
Richmond among them. The set is Appendix E of the Richmond Charter Review
Commission's 2023 report (`richmond2023`, printed p. 122), compiled for
Richmond and not for Arlington: it is a regional comparison, not a national
one, and it holds no county, where Arlington's form of government sits.

Each city's seats are the appendix's council members, and its at-large seats
are those its election column counts as at-large; a council printed as
"Ward" has none, and the two counts add to the members for every city. The
appendix counts a Mayor who sits and votes as one at-large seat, which is why
Norfolk is eight here and Appendix D's seven plus an at-large Mayor, and
leaves out the Mayor of a city where the Mayor is chief executive without a
seat, Richmond among them. That is the reading of the Mayor the peer set above
takes.

Nine of the nineteen elect every seat by ward and ten mix ward and at-large
seats; none, Arlington aside, elects every seat at large, and the largest
at-large share is Durham's four of seven. Huntsville's five, elected by ward, is the only council
as small as Arlington's. `localities_seats` shows it.

What rests on an assumption: that the appendix's counts are the councils
that sat in 2023. The report states no date for the table.
