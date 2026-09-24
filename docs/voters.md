# Voters

Who voted, for whom, and how many: what each number in `data/clean/voters.csv`
and `data/clean/turnout.csv` is, what backs it, what is assumed where nothing
does, and why. Present tense; how a decision was reached is in the git
history. The placeholders in the `source` columns are explained in
`docs/sources.md`, and what is still open is in `docs/questions.csv`.

---

## Voters

`data/clean/voters.csv` is Arlington's vote by party for two offices, one row
per election and office.

**For President**, every fourth year from 1872. Virginia has no party
registration, so nothing counts residents by party; the presidential vote is
the standard proxy and the one measure that arrives as a dataset. It counts
voters, not residents, and before 1966 the electorate was the one the 1902
constitution allowed, poll tax and literacy test, and before 1920 it was men.
The comparison the figures invite is therefore the Board against the people
who were allowed to vote, which the file name and axis label say so that no
caption has to. 1872–1920 is O'Leary's compilation of the Alexandria Gazette,
transcribed verbatim and parsed in `code/build/voters.py`. Party before 1924
is the nominee's, named in the build, since O'Leary prints it for 1912 only;
a name the build does not know stops it rather than falling into "other".
Three elections are kept and marked incomplete, and the figure leaves them
out: 1896, where the Washington district and the total are printed "?", and
1904 and 1908, of which O'Leary writes that the returns "appear incomplete"
(1904 sums to 256 votes against 826 four years earlier). 1924–2024 is the
state database's locality rows, which carry party on every candidate; its
Arlington rows for this office begin in 1924. The county's own candidate
history prints the same returns from 1920 and is read as a check: it agrees
with the state within five per cent in every year but 1980, where the
county's Carter figure is 25,003 against the state's 26,502 and the state's
canvass is kept. The "other" band is small except in 1912, 1968, 1980 and
1992; whether a two-line figure of the Democratic and Republican shares would
read better than three stacked bands has not been tried.

**The 1938 staggered-terms referendum** is in the county's candidate history
(`arlingtonelections2021` p.11) as 1,539 for, 1,487 against. The *Sun* of
11 November 1938 (`sun1938referendum`) prints returns for all eleven
precincts totalling 1,540 to 1,479, both columns tying to their totals, and
says of them "These figures are unofficial". The likeliest reconciliation is
that the county's is the certified canvass and the Sun's the count as known
three days out, an ordinary correction of 8 votes on one side and 1 on the
other; it has not been shown, the *Sun* of 18 November (`sun1938womenvoters`)
being about the ballot's wording rather than the tally. If the report uses a
margin it should use the county's and say so. From the same page, for the
prose: the ballot asked only whether members should be elected "as provided
in Sec. 2773-F1 of the Code of Virginia", the Commonwealth's Attorney's office
fielded calls from voters asking what it meant, and four of eleven precincts
voted against.

**For County Board**, every year from 1931. This is what the smaller November
electorate did with the candidates it was offered, and it is not coded the
same way as the roster: a candidate is counted under the label the county
prints after their name, not under the party reporting later attached to the
winner. Votes for Dorothy Grotos in 1975 sit in "other" here while her seat
is Republican in `board_party`, deliberately; one figure is the choice on the
ballot, the other who sat. 1931–2021 is the county's candidate history, every
general and special contest in a year summed; 2022 on is the state database,
which names a party on the 2022 general and none after, so from 2023 a
Democratic primary winner is Democratic and everyone else is unrecorded
(Clement, Fierro and Cambridge are in that band). A year is incomplete where a
member the roster seats by election has no vote count: 1942 and 1949. Two
seats are elected in every fourth year from 1951 and a ballot then carries
two votes, so shares are of votes cast; that distorts a party's share only
where it ran fewer candidates than seats, which the county's record shows in
1951 (one independent), 1959 (one Democrat and one Republican against two
ABC) and 2003 (one Republican).


---

## Turnout

`data/clean/turnout.csv` puts four measures side by side, one row per year:
votes cast in the November County Board contests and the seats they filled;
the people that represents; registered voters; the population 18 and over;
and the presidential vote. Each measure has its own source column, because a
row draws on up to four documents at once.

**Votes are not voters.** A Board ballot carries one vote per seat being
filled, so `board_voters` divides the votes by the seats: exactly the number
of people who voted for the Board when one seat was filled, and a lower bound
when more than one was. **Seats are counted from the roster, not read off the
page.** The county prints "Vote for 2" on some two-seat contests and nothing
on others, so the build counts the terms in `board_members.csv` that an
election seated the following January, or a special election seated that
November. That makes 1931, 1935 and 1939 five-seat elections (the whole
Board, before terms were staggered), 1943 and 1960 two (1960 is the regular
seat and Wilt's special), 1947 two (Frisbie, appointed after the election, is
listed with no count), 1952 four (three same-day specials beside the regular
seat) and 1997 two. Since 1951 every two-seat year has been a House of
Delegates year, so the understatement lives in that one line and the caption
says so. Ballots cast would be the right number and no source in hand holds
it.

**Which years are not the county's vote.** The county's own page says its
tallies are complete only from 1971. A year is marked incomplete and not drawn
where a named candidate has no count (1942, 1949, and Frisbie in 1947, whose
page also says its totals are from 8 of 11 precincts) or where the page says
others ran who are not listed (1931). Before 1932 the Board was elected by
district, one seat each, so every voter cast one vote; O'Leary reports the
count for 1907 (756 voters across three districts) and 1915 (876) and "(No
returns.)" for the rest. Both are in the table and not drawn.

**The denominators.** Votes for the Board are the county's candidate history
1931–2021 and the state database from 2022, write-ins included. Registered
voters are the Department of Elections' monthly locality report for October
of each year from 2010 (`varegistration`), dated in the first days of
November, which is as the books stood for the election; nothing earlier is
online. The active list is `registered` and the inactive list is added in
`registered_all`. The population 18 and over is the census: the 1980 and 1990
Summary Tape Files' age tables and the API's tables for 2000–2020, all checked
against the county total on every fetch, and carried between censuses on a
straight line for the figure's share panel (`voting_age_est`, marked
`derived`); after 2020 the 2020 count is carried forward, which overstates
the 2021–25 shares a little. The presidential vote is `voters.csv`'s and is
marked `derived`. Three guards: the Board's voters can never exceed the
registered voters, nor the presidential vote of the same year, and the
registered can never exceed the adults.

The state's historical database gives votes, not voters, and no registration:
its `Total Votes Cast` is the sum of the candidates' votes, and `Total Ballots
Cast` appears only for 2025. The Department's precinct turnout files from
2007 were not used; 2008's lacks the central absentee precinct, and in several
years a precinct's row is repeated once per district it sits in.

**What the series shows.** The Board's vote is drawn as four series by what
else the November ballot carried (the `cycle` column: president, governor,
midterm, delegates), because drawn as one line it is a sawtooth whose teeth
are the ballot and not the Board. In a presidential year about nine in ten of
the county's presidential voters also vote for the Board. As a share of the
county's adults, the presidential-year Board vote rose from about a third in
1980 to 57 per cent in 2024; the House of Delegates years, when the Board tops
the ballot, from a fifth to 30 per cent in 2023; and the midterm and
governor's years sat at a third for decades and have converged on the
presidential-year level since 2017. In November 2024: 196,563 adults (the 2020
count), 164,865 active registered voters, 128,362 who voted for President and
113,209 for the County Board.

**What the denominators do not reach.** Adults before 1980: the 1930–1970
censuses printed the county's population 21 and over (18 and over from 1970)
in the state volumes, none of which is in `data/raw/`; with them the share
panel would reach 1931, with a note at the 1971 change of age. Registration
before 2010 exists in the State Board of Elections' printed annual reports
and nowhere online found. "Eligible" is not one series: citizenship by county
exists only in the ACS from 2005, and before 1966 the poll tax and before 1920
sex decided eligibility, so adults is the denominator that can be held
constant, with the milestones as the caveat.

**Milestones, for the prose.** 1870, the Board is created, elected in May by
district. 1904, local elections move from May to November under the 1902
constitution, whose poll tax and literacy test shrank the electorate until the
1960s. 1920, women vote: O'Leary's presidential returns go from 804 in 1916 to
1,831 in 1920. 1932, the at-large Board of five, staggered from 1940 so that
the Board is on every November ballot. 1966, the poll tax falls (*Harper v.
Virginia Board of Elections*). 1971, the vote at 18. 2020, no-excuse absentee
and early voting.


---

## What rests on an assumption

- The 1938 referendum margin has two counts and the canvass has not been
  found (`referendum-1938-margin`).
- The non-Democratic County Board candidates since 2023 carry no party
  (`voters-2023-labels`).
- The presidential figure stacks three bands, and the pre-1924 nominees are a
  table in the build (`president-figure-form`).
- Turnout's denominators: adults before 1980 (`adults-before-1980`), adults
  after 2020 carried forward (`adults-after-2020`), registration before 2010
  (`registration-before-2010`), and votes per seat standing in for ballots
  cast (`ballots-cast`).

Each is a row in `docs/questions.csv`, with an owner and what would settle it.
