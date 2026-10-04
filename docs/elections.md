# Elections

This write-up covers who voted, for whom, and how many: what each number in
`data/clean/elections_results.csv` and `data/clean/elections_turnout.csv` is,
what backs it, and what is assumed where nothing does. How a decision was
reached is in the git history rather than here. `code/citekeys.py` explains the
placeholders in the `source` columns, and `docs/questions.csv` holds what is
still open.


## What rests on an assumption

- The 1938 referendum margin has two counts and the canvass has not been
  found (`referendum-1938-canvass`).
- The presidential figure stacks three bands, and the pre-1924 nominees are a
  table in the build (`president-figure-form`).
- Turnout's denominators: adults after 2020 carried forward
  (`adults-after-2020`), registration before 2010
  (`registration-before-2010`), and votes per seat standing in for ballots
  cast (`ballots-cast`).

- The nominating stage is recorded for at least one winner in 20 of the 89 Board election years since
  1931 (`nominations-1931-1978`, `nominations-1979-2011`,
  `nominations-2012-2025`), and before 1931 for 1885 alone
  (`nominations-pre-1931`); every other year reads "no record" in
  `elections_margins_by_year.csv`, which is a gap and not a finding.
- The nominating margin of the 2023 and 2024 ranked-choice primaries waits on
  the final-round counts (`margins-ranked-choice-rounds`), and the district
  margins before 1931 rest on the Gazette's OCR text (`margins-gazette-ocr`).

Each is a row in `docs/questions.csv`, with whose court it waits in and what would settle it.

---

## Results

`data/clean/elections_results.csv` is Arlington's vote by party for two offices, one row
per election and office.

**For President**, every fourth year from 1872. Virginia has no party
registration, so nothing counts residents by party; the presidential vote is
the standard proxy and the one measure that arrives as a dataset. It counts
voters, not residents, and before 1966 the electorate was the one the 1902
constitution allowed, poll tax and literacy test, and before 1920 it was men.
The comparison the figures invite is therefore the Board against the people
who were allowed to vote, which the file name and axis label say so that no
caption has to. 1872–1920 is O'Leary's compilation of the Alexandria Gazette,
transcribed verbatim and parsed in `code/clean/elections_results.py`. Party before 1924
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

**What staggering meant in practice** is in the Historical Society's 1967
compilation, not the ballot: "beginning with the County Board elected in 1939
to take office in 1940, one member of the Board has been elected in each
year and in the fourth year, two members are elected" (`arlhist1967officials`
p.37). So 1938 left term length alone - four years, unchanged since the Plan
took effect in 1932 - and changed only the cadence, from the whole five-member
Board at once every four years to one seat most years and two in the fourth.
That is the baseline the 1952 c. 591 referendum, never petitioned onto a
ballot (`vaacts1958c207`), would have replaced with elections
in groups every two years instead of annually.

**For County Board**, every year from 1931. This is what the smaller November
electorate did with the candidates it was offered, and it is not coded the
same way as the roster: a candidate is counted under the label the county
prints after their name, not under the party reporting later attached to the
winner. Votes for Dorothy Grotos in 1975 sit in "other" here while her seat
is Republican in `members_by_party`, deliberately; one figure is the choice on the
ballot, the other who sat. 1931–2021 is the county's candidate history, every
general and special contest in a year summed; 2022 on is the state database,
which names a party on the 2022 general and none after, so from 2023 a
Democratic primary winner is Democratic. Every other general-election
candidate since 2023 is read from a press or campaign source, quoted in
`data/transcribed/by_claude/candidates_party.csv` and decoded in
`code/clean/elections_results.py`'s `CANDIDATE_PARTY_WORDS`: Fierro (2023, 2024) and
Cambridge (2025) are Republican, named by the county Republican committee;
Clement (2023–2025), Granger (2024, running under the Forward Party's
banner) and De Castro Pretelt and Olmack (2025) are independent, so in
"other". A year is incomplete on the
same rule turnout uses, below: 1931, 1942, 1947 and 1949. Two
seats are elected in every fourth year from 1951 and a ballot then carries
two votes, so shares are of votes cast; that distorts a party's share only
where it ran fewer candidates than seats, which the county's record shows in
1951 (one independent), 1959 (one Democrat and one Republican against two
ABC) and 2003 (one Republican).


---

## How the Board's candidates were nominated

`data/clean/elections_nominations.csv` has one row per candidate per nominating
contest. A party's or coalition's method is its own and changes
(`docs/candidates.md`, "Who the general-election list leaves out"); the file
records the methods the sources name and no others: Democratic primary,
Democratic caucus, Democratic committees' vote, ABC convention, Republican
committee, Republican mass meeting, and for 1885 the Gazette's "regular"
nomination. A row is **derived** where the county's candidate history (to
2021) or the state's database (from 2022) prints the primary with its counts,
and **keyed** where a newspaper reports a convention, caucus, committee vote
or primary, with a quoted sentence in
`data/transcribed/by_claude/elections_nominations.csv`.

A primary candidate won the nomination if they are on that year's regular
general ballot. The state's own winner flag is not used: for a ranked-choice
primary it marks every candidate who was not eliminated in the first count.
The 2023 and 2024 counts are first choices (`votes_kind`), and in 2023 the
candidate with the most first choices did not win.

`contested` is yes where a source names a losing candidate, no where it says
the nominee was unopposed, and blank where it says neither: the county prints
some primaries as one name, and a convention report can omit the losers.

What the covered years show about method, from the rows:

| Years | Party | Method |
|---|---|---|
| 1942, 1944 | Democratic | primary: unopposed in 1942; Lloyd 1,212, Usilton 754, Beard 116 in 1944 |
| 1944, 1963 | Republican | county committee (1944); mass meeting, then committee when the nominee withdrew (1963) |
| 1955 | ABC | convention, five seeking two nominations, 39 votes between second and third |
| 1950, 1952, 1962 | Democratic | primaries the county prints without counts |
| 1995, 1997, 2003 | Democratic | state-run primaries |
| 2002, 2003 (March special) | Democratic | caucus |
| 2012, 2014, 2017 | Democratic | caucus, with ranked ballots in 2014 and 2017 |
| 2015, 2016, 2018, 2021 | Democratic | state-run primaries |
| 2019, 2020 (regular seat) | Democratic | primary not held, the incumbents unopposed |
| 2020 (special) | Democratic | a ranked-choice vote of about 250 committee members |
| 2023-2025 | Democratic | state-run primaries, ranked-choice counting |

## How close the contests were

`data/clean/elections_margins.csv` has one row per contest, general and
nominating. The margin is the fewest votes that won a seat minus the most votes
that lost one, so with two seats it is the second-place candidate against the
third; as a share it is of the votes cast in the contest, write-ins included,
which counts each two-seat ballot twice. A source that prints only
percentages (the 2014 caucus) gives the difference in points. The seats are the
county's except where it prints "Vote for 1" on a larger contest (`SEATS` in
`code/clean/elections_margins.py`), and every winner the votes name must be a
member the roster seated that year or the build stops.

A margin is not computed where the returns are incomplete (1931, 1935, 1947,
1949, and 1942, whose names carry no counts), where no named candidate stood
against the winner (1996, 2005), where the page prints no counts for a
nominating contest, and for a ranked-choice contest whose counts are first
choices. Each such row stays in the file with its reason.

The general margin is computed for 83 of the 89 years since 1931. Its share of
votes cast, by era:

| Years | Contests computed | Median share | Range |
|---|---|---|---|
| 1931-1950 | 9 | 10.0% | 0.7-57.2% |
| 1951-1970 | 21 | 4.6% | 0.2-21.8% |
| 1971-1990 | 21 | 11.1% | 0.5-68.6% |
| 1991-2010 | 23 | 23.5% | 0.9-53.1% |
| 2011-2025 | 18 | 31.2% | 5.7-49.6% |

`contested_other` in `elections_margins_by_year.csv` is yes where any named
candidate carries a label other than the county's Democratic or ABC (the
county's label, as in "For County Board" above, and not the member's party in
`members_by_party`), no where every candidate is Democratic or ABC, and unknown
where a candidate has no label and no other candidate has a non-Democratic,
non-ABC one.

Before 1931 each district's seat is its own contest. The Gazette's counts
give ten district margins (1893-1901, 1919) from OCR text; O'Leary prints the
counts for 1907 and 1915, and the highest count there is checked against the
roster. The nominating stage is keyed for 1885 only, where the Gazette names
the "regular republican" nominee and a "citizens'" candidate against them in
Arlington District; the other years and districts are gaps.

---

## Turnout

`data/clean/elections_turnout.csv` puts four measures side by side, one row per
year: the votes cast in the November County Board contests, the registered
voters, the population 18 and over, and the presidential vote. It also carries
the seats those Board votes filled and the number of people the votes
represent. Each of the four measures has its own source column, because a row
draws on up to four documents at once.

**Votes are not voters.** A Board ballot carries one vote per seat being
filled, so `board_voters` divides the votes by the seats: exactly the number
of people who voted for the Board when one seat was filled, and a lower bound
when more than one was. **Seats are counted from the roster, not read off the
page.** The county prints "Vote for 2" on some two-seat contests and nothing
on others, so the build counts the terms in `members.csv` that an
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
tallies are complete only from 1971. One rule, in `code/clean/elections.py`,
decides for `elections_results.csv` and `elections_turnout.csv` alike. A year is marked incomplete and not drawn
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
`registered_all`. The adults are the census's count of the people old enough
to vote: 21 and over through 1970 (`voting_age_21`) and 18 and over from 1971,
when the Twenty-sixth Amendment took effect (`voting_age`). 1930 to 1970 are
the census volumes' county tables, keyed in and tied out as
`docs/residents.md` describes; 1970 prints both ages. 1980 and 1990 are the
Summary Tape Files' age tables and 2000–2020 the API's tables, all checked
against the county total on every fetch. `voting_age_est` carries them between
censuses on a straight line for the figure's share panel, marked `derived`:
the 21-and-over counts through the November 1970 election, and from 1971 the
18-and-over counts from 1970's 132,720; after 2020 the 2020 count is carried
forward, which overstates the 2021–25 shares a little. The change of age adds
the people aged 18 to 20 to the 1970 denominator, and no series on the
share panel steps at 1971. The presidential vote is `elections_results.csv`'s and is
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
are the ballot and not the Board. In a presidential year most of
the county's presidential voters also vote for the Board.

As a share of the county's adults, the four series move differently:

- **presidential years** rose from the 1940s to 1968, fell back by 1980, and
  reach a majority of adults in 2024;
- **House of Delegates years**, when the Board tops the ballot, run below the
  other cycles and rise in 2023;
- **midterm and governor's years** sat well below presidential years for
  decades and have converged on them since 2017.

November 2024 gives the whole picture at one date: 196,563 adults (the 2020
count), 164,865 active registered voters, 128,362 who voted for President and
113,209 for the County Board.

**What the denominators do not reach.** Registration
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
