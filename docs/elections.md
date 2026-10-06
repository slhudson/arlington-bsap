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
- The county's presidential total for 1920 is O'Leary's, since no state
  return has been found (`state-returns-1920`), and the Almanack that
  prints the others before 1924 cannot be tested against the Secretary's
  own return with anything held online; only a visit to the Library of
  Virginia would settle it (`almanack-against-secretary`).
- Turnout's denominators: adults after 2020 carried forward
  (`adults-after-2020`), and the county's men of voting age before 1910
  counted at three censuses until the 1870, 1890 and 1900 volumes are keyed
  in (`adults-1870-1900`). The modern figure's two-seat years are gaps until
  ballots cast are found (`ballots-cast`), and the settled forms of the
  figures are not yet built (`turnout-figures-rebuild`).

- The nominating stage is recorded for at least one winner in 20 of the 89 Board election years since
  1931 (`nominations-1931-1978`, `nominations-1979-2011`,
  `nominations-2012-2025`), and before 1931 for 1885 alone
  (`nominations-pre-1931`); every other year reads "no record" in
  `elections_margins_by_year.csv`, which is a gap and not a finding.
- The nominating margin of the 2023 and 2024 ranked-choice primaries waits on
  the final-round counts (`margins-ranked-choice-rounds`).

Each is a row in `docs/questions.csv`, with whose court it waits in and what would settle it.

---

## Election Method (A.2)

The paper's Election Method section opens with the general mechanics of
single-winner districts, multi-winner block elections and ranked choice, in
the Charlottesville series' language and sources, then turns to Arlington in
four subsections: districts, 1870-1930; at large, 1930 to the present;
staggered terms, 1938 to the present; and ranked choice, 2020 to the present.
The turnout figure sits under staggered terms, as the electorate each seat
is filled by ("Turnout", below), and districts, 1870-1930, owes one sentence
on the electorate its last 28 years ran on, pointing at the same figure.
The nominating stage is not a subsection of its own: whether the report makes
a nominating-stage argument at all is parked (`nominations-1931-1978` and
three further rows, `docs/questions.csv`), and until that is decided the
nominating material stays in the timelines and in "How the Board's candidates
were nominated," below.

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
caption has to. 1872 is the county electoral board's own certified return,
printed in the *Alexandria Gazette*; 1876–1916 is the Commonwealth's return
for the county as the *Warrock-Richardson Almanack* prints the official vote;
and 1924 and 1928 are the Secretary of the Commonwealth's reports. All are
keyed in `data/transcribed/by_claude/elections_results_state.csv` and read by
the build as they stand: the clean step sums each year's tickets into the
bands (a Funder and a Readjuster column for Hancock in 1880 are one Democratic
vote; a dotted ticket is 0; where the Almanack prints only the highest
candidates, 1904, 1908, 1912 and 1916, the other band is what it prints). For
1928 the Secretary's 26 minor-party votes are kept and the year's note says
the state database's locality rows leave them out. 1920 is O'Leary's
compilation of the *Alexandria Gazette*, the only count held, marked as his
in the row's note and drawn as an open marker; the build takes nothing from
him in a year with a state return, and refuses a year that is in neither.
Every year in the return is complete, 1896, 1904 and 1908 included
(see "The state's return, read against O'Leary's"). Party in 1920 is
the nominee's, named in the build, since O'Leary prints it for 1912 only; a name
the build does not know stops it rather than falling into "other". 1932–2024
is the state database's locality rows, which carry party on every candidate; its
Arlington rows for this office begin in 1924. The county's own candidate
history prints the same returns from 1920 and is read as a check: it agrees
with the state within five per cent in every year but 1980, where the
county's Carter figure is 25,003 against the state's 26,502 and the state's
canvass is kept. The "other" band is small except in 1912, 1968, 1980 and
1992; whether a two-line figure of the Democratic and Republican shares would
read better than three stacked bands has not been tried.

**The state's return, read against O'Leary's.** The Commonwealth's county
returns for President are keyed in `data/transcribed/by_claude/elections_results_state.csv`,
one row per ticket, each read off the page image. For 1872 no Commonwealth
canvass by county has been found, but the county electoral board's own
certified return is printed in the *Alexandria Gazette* of 7 November 1872
(`alexandriagazette1872official`), the "Alexandria County Official" table, one
row per magisterial township (Arlington, Jefferson, Washington); the rows keyed
are the three townships' Grant and Greeley columns summed. Before 1924 no
Secretary of the Commonwealth's report prints a county canvass: the reports
held in HathiTrust for 1904 to 1921 are rosters of officers and boards. What
prints the official vote by county from 1876 is the *Warrock-Richardson
Almanack*, a Richmond annual that heads its tables "The Official Vote of
Virginia" and says of the 1892 and 1896 votes that they are "taken from the
official returns for this Almanack" (`warrock1868`, `warrock1892`,
`warrock1900`, `warrock1911`); from 1924 the Secretary's own report prints
them (`vasecretary1924`, `vasecretary1928`). The Almanack's tables keep
Alexandria County and Alexandria city in separate rows, and the county's is
the row keyed. 1920 has no state return in anything held. Where the Almanack
prints only the highest candidates (1904, 1908, 1912, 1916) the minor
tickets' votes are not recorded.

| Year | State's return | O'Leary | The two |
|---|---|---|---|
| 1872 | 126 D, 464 R (the county's own return) | 125 D, 455 R | close but not exact |
| 1876 | 237 D, 587 R | 237 D, 587 R | agree |
| 1880 | 262 D (Funder) and 2 D (Readjuster), 489 R | 262 D, 459 R | Garfield 489 against 459 |
| 1884 | 264 D, 509 R | 264 D, 508 R | one vote |
| 1888 | 255 D, 462 R | 407 D, 314 R | the county's winner changes |
| 1892 | 340 D, 499 R, 1 Prohibition | 338 D, 426 R | Harrison 499 against 426 |
| 1896 | 322 D, 713 R, 4 other | 78 D, 259 R, marked incomplete | state's total 1,039 against 337 |
| 1900 | 413 D, 421 R, 2 Prohibition | 418 D, 408 R | the county's winner changes |
| 1904 | 157 D, 99 R | 157 D, 99 R | agree |
| 1908 | 354 D, 165 R | 345 D, 165 R | Bryan 354 against 345 |
| 1912 | 346 D, 86 R, 153 Progressive | 246 D, 86 R, 153 Progressive | Wilson 346 against 246 |
| 1916 | 515 D, 412 R (two highest only) | 445 D, 351 R, 8 other | Wilson 515 against 445 |
| 1920 | none found | 835 D, 996 R | O'Leary only |
| 1924 | 1,209 D, 1,307 R, 405 Progressive | the build already reads the state | agree |
| 1928 | 1,444 D, 4,274 R, 26 other | the build reads 1,444 D, 4,274 R, 0 other | the 26 minor-party votes |

The build takes the state's return wherever one is keyed and O'Leary's
only for 1920; for 1892 and 1900 it then takes the Gazette's own
district sum over the Almanack's, below. O'Leary compiled his from the *Alexandria Gazette*
and states that party is inferred and the record ragged; the state's figures
are printed from the official returns, and in 1888 and 1900 the two disagree
on which party carried the county. For 1908 the state's Bryan figure is the one
doubtful digit: the type is damaged in every printing seen and reads 354,
which would make O'Leary's 345 a transposition. In 1912 the Almanack prints
346 for Wilson on two pages while O'Leary's 485 total rests on 246, and the
state's 346 gives 585. The Almanack is a compilation and not the Secretary's
own return, and the two are held side by side for no election: the Secretary's
reports print county returns from 1924 and the Almanack volumes held end with
the 1920 edition.

**Why they cannot be tested against each other.** No Almanack edition printed
after the 1920 one is held anywhere found: the bound volumes on HathiTrust and
the Internet Archive run 1868-1891, 1892-1898, 1899, 1900-1910 and 1911-1920,
and the serial's own catalog record (the annual ran 1878-<1935>) carries no
further digitized volume from any contributing library, so no Almanack edition
printed after the November 1924 or 1928 elections exists to set against the
Secretary's reports for those years. Before 1924 the gap runs the other way:
the Secretary's own reports carry no county table, as `vasecretary1924`'s
annotation already records for the volumes searched (1905, 1908/09, 1909,
1912/13, 1913, 1917, 1920/21), confirmed again by a second library's copy of
the 1904/05 report, which does not mention Roosevelt, the losing 1904
candidate. Nothing found in the General Assembly's journals or documents on
HathiTrust prints a county-by-county presidential canvass either. The Almanack
and the Secretary are therefore untestable against each other with anything
held online; only the Library of Virginia's own county abstracts of votes,
filed with the pre-1946 records of the Secretary of the Commonwealth, would
settle it (`almanack-against-secretary`).

The Secretary's 1928 report prints 26 votes for three minor tickets that the
state database's locality rows, which the build reads for 1928, leave out; the
database's total of 5,718 is therefore 26 short of the Secretary's 5,744.

**The Gazette's own district returns settle four of the nine, and the build
now reads two of those over the Almanack.** The
*Alexandria Gazette* printed Arlington, Jefferson and Washington districts'
own presidential vote, not just the county total, after the 1876, 1892,
1896 and 1900 elections, and the Jefferson district alone after 1920; 1872
printed Jefferson and Arlington townships but no Washington, which does not
appear to have existed as a district yet. Summed, the Gazette's own figures
tie to O'Leary's exactly for 1876 (237 D, 587 R), 1892 (338 D, 426 R) and
1900 (418 D, 408 R), and the 1920 county total (835 D, 996 R) matches him
too: O'Leary compiled from these same reports, and for those years his
figure is the Gazette's own canvass, independent of the Almanack's
compilation, read off the page image and not taken on O'Leary's word; for
1892 and 1900, `code/clean/gazette_vs_almanack.py` now reads it in place of
the Almanack's, pending a spot-check of the page reads
(`gazette-vs-almanack-1892-1900`, questions.csv). The 1896 Washington district prints only
McKinley's 25-vote majority, not raw totals, which is why O'Leary's total
for that year is marked incomplete; the Jefferson and Washington districts'
sum (McKinley 553, Bryan 228) cannot be checked against the state's 713 and
322 without it. For 1872 the two townships sum to 77 D, 327 R, well short of
O'Leary's 125 D, 455 R; nothing in the issues checked explains the gap, and
with no state return either, the two stand unreconciled. 1920's Arlington and
Washington districts were not found in the issues read page by page, and a
full-text search of the Gazette on Virginia Chronicle from 6 to 30 November
1920 for "Arlington district", "Washington district" and "Jefferson district
Harding" turns up nothing either; by subtraction from the county total they
sum to 695 D, 857 R. 1880, 1884, 1888, 1908, 1912 and 1916 print no district
breakdown in the Gazette issues read page by page, only a city total and,
from 1888 on, a single county line inside a multi-county congressional-
district roundup; a full-text search of the Gazette on Virginia Chronicle
extending each year's window to four weeks after the election, for
"Arlington district", "Washington district" and "Jefferson district", finds
no further table in any of the six years either (5 October 2026). 1904
prints only the county total too, but it agrees with the state and O'Leary
already. The full-text search is a weaker check than reading the page image
-- the OCR on these scans is poor -- so a later page-by-page read of the
same weeks is not foreclosed if the question matters enough to redo it.

**1896, 1904 and 1908 are complete in the state's return.** The state prints
322, 713 and four others for 1896 where O'Leary has no Washington-district
figure and no total; its 1,039 replaces his 337. For 1904 it prints the same
157 and 99 as O'Leary, so nothing in the state's return is missing from his:
the fall from 836 votes in 1900 to 256 in 1904 is the county's, and follows
the poll tax and literacy test the 1902 constitution put in place. For 1908 it
prints 354 and 165, nine more Democratic votes than his 345. The
tables print a whole row for the county in each year and carry no note of a
precinct missing; whether every precinct was counted is not something a table
can show.

**The 1930 referendum campaign** is in Anderson 1958, a first-hand account by
the chairman of the committee that ran it (`anderson1958` pp. 57-64). The
Arlington County Civic Federation resolved on 6 May 1930 to study a change of
government; its committee joined with the Chamber of Commerce's and the Bar
Association's in July, reported on 2 September for the County Manager form,
and on 16 September the Federation adopted the report with election of the
Board at large; a petition of 1,027 voters brought the circuit court's order
for an election on 4 November. Against it were the Voters' Service Club,
announced on 4 October under the county's zoning officer as executive
secretary, the county weekly *Chronicle* with a half-page editorial on 17
October headed "Dangerous Plan to Fasten on the County", its editor Crandal
Mackey, the attorney Clarence Ahalt, J. C. Pepper, and on 2 November the
Sheriff; the Board of Supervisors made no statement. For it, beside the
committee's sixteen-page pamphlet delivered to 6,000 homes on 23-25 October,
were Delegate Hugh Reid from 28 October, Senator Frank Ball in a radio
broadcast on 31 October with Alexandria's city manager and the school
superintendent, and the Commissioner of Revenue on 3 November. Anderson's
footnote declines to set out the arguments on either side, and neither the
*Chronicle*'s 17 October 1930 editorial nor the Federation's pamphlet is held
in Virginia Chronicle or anywhere else searched. He also prints the three
questions' totals as 2,067 to 1,031 for a change, 1,908 to 485 for the Manager
form and 1,659 to 1,179 for election at large; Rose 1976 prints 1,936 to 428
and 1,689 to 1,149 for the second and third. The precinct table in the
*Evening Star* of 5 November 1930 (`eveningstar19301105b1`) settles it: its
totals tie to Rose's exactly on all three questions, and the paper cites
Rose's.

The *Star* of 26 October 1930 (`eveningstar19301026b2`) carries what the
Chronicle and the Federation's pamphlet are not held to supply: Robert H.
Forman of the Voters' Service Club opposed the manager plan on cost, not on
election at large as such; Capt. Crandal Mackey and Clarence R. Ahalt called
abolishing the magisterial districts for at-large election "a direct
departure from representative government"; and, for the change, John A.
Petty of the Livingstone Heights Civic League called it the step that made
"Arlington County a single unit" and gave "every voter the right to cast his
ballot for or against each of the members of the county board." Anderson
1958 dates Forman's statement to 23 October; the Star printed it on the 26th.

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
give sixteen district margins (1893-1901, 1907, 1915, 1919), each read off the page image, and the
highest count is checked against the roster. The nominating stage is keyed for 1885 only, where the Gazette names
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

**One figure, 1872 to the present, and what it argues.** Election Method's
claim is that what separates the three methods is how many seats one ballot
fills and who counts as the electorate for each, and turnout is the evidence
for the second half. `elections_turnout` is one panel, votes per 100
residents of voting age: the presidential vote as one grey line from 1872,
which is the thread, who could vote, from four men in five in 1880 to one in
eleven in 1904, the dip at 1920 when women double the denominator, the climb
from the 1940s and the plateau above 60 percent since 2008. The Board's vote
sits on it in one colour family: squares for the five district-era
elections every district's count survives (the county recorded the Board's
vote in five of 29, two of them O'Leary's alone, which is a table and not a
line), and from 1935 three shades by what led the ballot, so the Board reads
as one family against the presidential line and the trend in each cycle is
still visible. A two-seat year is a gap, because it records votes and not
voters, and that takes every House of Delegates year from 1943
(`ballots-cast`). The figure goes in Election Method under Staggered Terms,
because that is what it shows about the method: one seat on every November
ballot means each seat is chosen by whoever turned out for that year's top
of the ticket, about half the county's adults in a presidential year and a
quarter to a third in a governor's, two members of one Board with
electorates of different size. Race keeps its electorate paragraph and
points at the figure's left third for the collapse after 1894 and 1902,
which is a fact about the electorate and not about districts: a poll tax
shrinks an at-large electorate the same way. The denominator is every
resident of voting age, non-citizens and the disfranchised included, the
one denominator that can be held constant across the period, and the
caption says so. The all-residents version, the pre-1932 adults figure and
the by-district figure are retired: the first two are the left third of this
one, and the third's one finding, that Jefferson fell steepest, is a
sentence in the prose with its own built numbers (Sally, 6 October 2026;
`turnout-figures-rebuild`).

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
district, one seat each, so every voter cast one vote; the Gazette prints the
count for 1907 (756 voters across three districts, issue of 6 November) and 1915 (876, 3
November) in every district, read off the page image, and O'Leary reports "(No
returns.)" for the rest. O'Leary's own counts for the two years agree with the
Gazette's on all sixteen candidates; they differ only in spelling (Hagen for
Hagan, Wibirt for Wilbert, the initials W.M., J.W. and E.J. for W. N.
Febrey, G. W. Donaldson and C. J. Costello), and nothing in the table rests on him.
Both are in the table and not drawn.

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

**The rates the prose cites are the figures' own.** The turnout figure
and the prose take their pre-1932 denominators from `code/analysis/elections.py`:
the presidential vote per 100 residents of voting age, and a district's Board
contest per 100 men of voting age the nearest census counted there, which
the Race section cites for Jefferson though no figure draws it.
`code/analysis/body_text_numbers.py` reads the same module and writes each rate
as a command (`\turnoutNineteenFour`, `\boardTurnoutJeffersonNineteenOne`), and
the Race section's electorate paragraph cites the commands rather than numbers
typed from the figure, so a change of denominator reaches the prose in the same
build. `code/tests.py` works the rates out again without the module and refuses
a command that disagrees.

**What the series shows.** The Board's vote is drawn by what else the
November ballot carried (the `cycle` column: president, governor, midterm,
delegates), because drawn as one line it is a sawtooth whose teeth are the
ballot and not the Board. In a presidential year most of the county's
presidential voters also vote for the Board.

As a share of the county's adults, the cycles move differently:

- **presidential years** rose from the 1940s to 1968, fell back by 1980, and
  reach a majority of adults in 2024;
- **House of Delegates years**, when the Board tops the ballot, run below the
  other cycles; from 1943 every one is a two-seat year and is not drawn;
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
1960s. 1920, women vote: the presidential vote goes from 927 in 1916 to
1,831 in 1920. 1932, the at-large Board of five, staggered from 1940 so that
the Board is on every November ballot. 1966, the poll tax falls (*Harper v.
Virginia Board of Elections*). 1971, the vote at 18. 2020, no-excuse absentee
and early voting.
