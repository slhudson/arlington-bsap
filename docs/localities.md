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
residents or more, eighteen in all, and leave the choice of peer to the
reader: places Arlington's size in `localities_residents`, places as dense
in `localities_density`.

A city's council is the Richmond Charter Review Commission's count
(`richmond2023`, Appendix D). A Mayor elected at large counts as a member,
because the appendix's notes say most vote on council; Richmond's is the one
the notes name as sitting outside it. A Mayor chosen from council is already
among its members. A county board's count includes a chair elected at large.
Residents are the 2020 census; land area is the 2020 Gazetteer's.

Arlington carries about 48,000 residents per member, beside Loudoun and
Virginia Beach. Cities of its size carry about half that, and Alexandria,
the one place as dense, about 23,000; the larger counties, Henrico,
Chesterfield, Prince William and Fairfax, carry more.
