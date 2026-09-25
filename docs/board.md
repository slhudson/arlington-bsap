# The Board

Who held each seat and when, and who they were: what each number in
`data/clean/board_members.csv` and `data/clean/board_seats.csv` is, what backs
it, what is assumed where nothing does, and why. Present tense; how a decision
was reached is in the git history. The placeholders in the `source` columns
are explained in `code/build/citekeys.py`, and what is still open is in
`docs/questions.csv`.


## What rests on an assumption

- 1889–1986 is coded all-White on the "first since Reconstruction" framing,
  and the five Reconstruction-era members rest on Hjerpe's census linking
  (`default-1931-1986`).
- Gender is read from names for most of the roster (`gender-from-names`).
- 1912–1931 has no roster; the 1923 and 1927 names are not entered
  (`roster-1912-1931`).
- The November 1903 winners are seated in January on sec. 112 without the
  Schedule having been read (`schedule-1902`).
- From 1907 O'Leary's surnames are not joined to earlier full names
  (`surnames-from-1907`).
- 23 terms from 1932 carry no party, three labels are unresolved, and no
  party is attempted before 1932 (`party-unlabelled`, `party-before-1932`).
- The 1930 candidacies of Harris, Morton and Mosley rest on a page nobody has
  read (`bestebreurtje-p215`).
- Ten pieces of reporting cited for party are not yet filed in Drive
  (`reporting-unfiled`).

Each is a row in `docs/questions.csv`, with an owner and what would settle it.

---

### The roster

`data/clean/board_members.csv` holds one row per person per term: name, term
number, district, when service began and ended (to the month), how the term
began, and a source per row. 217 terms, 1870 through 2026, from three sources
in sequence: O'Leary's electoral history to 1915, Novack's roster from 1932 to
1994, and election results after that, the county's candidate history to 2021
and the state's elections database from 2022. Nothing covers 1912–1931 except
the two elections named below.

A term is the natural unit: person-years fall out of it, while a term starting
in May or ending in February cannot be recovered from a list of years. A
vacant seat is not a row, since nobody served. `term_number` counts within a
person, so someone appointed to a vacancy who then won twice has three rows
numbered 1, 2, 3; William A. Rowe has eight, including his move from Jefferson
district to Arlington at term 7.

`seated_by` says how each term began: election, special election,
appointment, or unrecorded where O'Leary writes only that someone was
replaced. Three builds select terms by it, so it is a column rather than
something read out of the note.

**When a term begins depends on the constitution in force.** Under the
magisterial system elections were held in May and the board took office then,
so those terms run May to May. The 1902 constitution moved county and district
elections to November and seated their winners on 1 January following (sec.
112, `vaconstitution1902`), so from the November 1903 election a term runs
January to January; the County Manager plan seats members on 1 January too,
so the convention is unbroken from 1904 on. The Schedule of the 1902
constitution, which would say how the first election under it was treated,
is not in the copy held (`vaconstitution1902` stops at sec. 136; the Library
of Virginia has a scan behind a viewer), so whether the November 1903 winners
fell under sec. 112 or a transitional provision is unconfirmed; the build
seats them in January on the reading that the section is the operative rule
and an exception has to be shown (Sally, 24 September 2026). It moves one
handover by two months in a stretch where every member is coded a white man.

The same convention is why the Arlington Historical Society's roster dates
Newman 1987, Monroe 1999, Dorsey 2015 and Spain 2024 where this one seats them
a year later: each won the November general election of the earlier year and
took office that January. Tejada is the control. He won a special election in
March 2003 and is seated in 2003, because a special election seats its winner
when it is held.

**A term ends when the term ends, not when the listings resume.** Sec. 112
makes it four years, so a November win closes four years on. O'Leary lists the
board in 1907 and in 1915 and not in 1911; reading the 1907 winners through to
1915 would put three named men in a seat for eight years on a source that
speaks to four. Their terms close in January 1912, and nothing names who held
those seats next. The note on such a row says the end is the statute's; where
the next listed election seats a successor on the same date the departure is
sourced and carries no note.

**So the roster stops naming people in 1912, and nothing names anyone until
1932.** For 1912–1931 no source in hand records who served, and the seat
counts for those years are an assumption, stated in `code/build/board_seats.py`
and labelled `assumed`: three seats, filled, held by white men. Two elections
inside the stretch are printed in the county's candidate history under the
district headings rather than under "County Board": November 1923 (Ingram in
Arlington, Duncan in Jefferson, Thornburke in Washington) and November 1927
(Duncan and Thornburke). Ingram and Thornburke appear in no other source; both are marked
"(inc.)" in 1923, so they were elected at one of the unrecorded elections
after 1915, and the Alexandria Gazette and the Washington Star are where to
look for the rest. Duncan is very likely the Duncan who held Jefferson from
1895 in O'Leary, which would make the gap two seats wide rather than three.
They are not in the roster: `board_seats` derives its counts from it, so a
roster covering 1923 and 1927 but not the years around them would read the
rest as unfilled, and the two would first have to be decoupled, with the
roster naming who is named and the counts keeping the assumption, which is
already how the 1915 winners are carried.

**Mid-term handovers are terms like any other.** O'Leary records them as
prose beside the elected member ("Replaced by H. Dwight Smith in Dec.;
replaced by Lott W. Crocker in March 1873, replaced by Francis D. Schutt in
April"), and those are parsed into their own rows: the Arlington seat in
1872–73 is four terms. Where a month is given without a year, the year carries
from the previous handover and rolls forward when the month goes backwards.
Francis D. Schutt holds two consecutive terms in 1873, appointed in April and
elected in May; that is two terms, not a duplicate. From 1907 O'Leary gives
surnames only, so "Corbett" from 1907 is a different person in the roster from
"Frederick S. Corbett" before it and starts again at term 1. Two people appear
under both forms, Corbett and Duncan; joining them needs a rule (surname plus
district plus continuity) or a note per case.

**Novack's spans are split at elections.** He lists a person once with their
whole service compressed into a string ("1932-1947" for Elizabeth Magruder),
so a span is cut at each November election the person contested, using the
county's candidate history, and the months come from his parentheticals. He
sometimes dates a span from the election rather than from taking office
(Fisher "1963-1974" won in November 1963 and sat from January 1964), so a span
whose first year is one the person won without having stood the year before
begins the following January. A cut at an election the person stood in and
lost continues however the span began: Frisbie, appointed in November 1947,
stood that month and did not win, and his 1948 term is still the appointment.
A member appointed to a vacancy who then wins the seat at a same-day special
election is seated by it that November and the appointment ends then: Wilt,
appointed in January 1960, won the special for Krupsaw's unexpired term that
November, which Novack's note does not record and the county's does. Where an
appointment is dated and no departure accounts for it, the one member whose
span ends that year undated left in the month of the appointment; more than
one candidate stops the build.

**From 1995 a term is built from election results.** A November win starts a
four-year term the following January. A special election fills the rest of a
term that ended early: the member who left is closed at that month, the winner
serves until the seat's next regular election, and where two members' terms
end in the same year the county's own annotation ("to fill Eisenberg's
unexpired term") says whose seat it was; the build refuses to guess when it is
absent. The five people still serving when Novack published have their last
term closed the same way. A check runs every month from 1995 through 2026:
five members at large, six only in a month a special election changed hands.
The county and state sources both hold the 2021 election, and the build
insists they name the same winner there before using the second.

**Recorded vacancies.** Two in the whole period a roster covers, found by
counting the months each term covers against the seats that existed: the
Washington district seat from the May 1873 election until Samuel Titus was
appointed that December, and March and April 1990 between Milliken's
resignation and Hunter's special election. 1912–1931 is the only stretch not
swept, since there is no roster to sweep.

## Seat-years

`data/clean/board_seats.csv` is one row per year, 1870 through 2026: seats
held by each race, each gender and (from 1932) each party, in seat-years, so
a member who sat for four months of a year counts 4/12. It is computed from
`board_members.csv` for every year but 1912–1931, which are the assumption
above. Days are not recorded consistently, Novack giving some and the election
dates others, so the month is the unit, and **the handover month belongs to
the incoming member** (Sally, 22 September 2026).

The denominator is the months the Board existed that year, which is twelve for
every year but its first. Arlington's Board came into existence at the May
1870 election, so 1870 is scaled by the eight months it existed: it reads
three seats filled, because they were, for as long as there was a Board to
fill them. Divided by twelve it would read two, and a chart of that says the
Board grew from two seats to three, which it did not.

The seats held can never exceed the seats that exist (three magisterial
districts with one supervisor each from 1870; five members elected countywide
from the County Manager plan, adopted at the November 1931 referendum and
seated in January 1932), and fall short only in 1873 and 1990; anything else
stops the build. Race, gender and party are independent splits of the same
seats and must account for the same total in every year, which
`code/tests.py` checks by taking a term out of one split and asserting the
build refuses.

The Board's race coding is one code per person, so it is already a set of
categories that do not overlap. A member coded Hispanic carries no separate
race, so `white` here means white and not Hispanic, which is what the census
basis means from 1980; the two files line up and the figures drawn from them
can be read against each other.

`residents_per_seat` divides population by the seats that exist, not the
seats filled. Where a seat sat empty, each serving member represented more
people than the figure shows. Whether to divide by the filled count instead,
which would make the growth figure depend on the roster, is open.

## Race and gender of Board members

Race and gender come from `data/transcribed/by_claude/board_demographics.csv`,
one row per claim a source makes about a member, in the source's own words
with a citation to the page the document prints; and otherwise from a default,
a white man, labelled `assumed`. Each cell of `board_members.csv` says which.
Two sources disagreeing about a person stops the build, and an attributed name
that matches no roster name stops it too, so a near-miss cannot fall silently
into the default. The default is a claim, and this is what stands behind it in
each period:

| Period | Race | Gender |
|---|---|---|
| 1870–1888 | Five Black members named by Hjerpe (2021): Rowe, Syphax, Pinn, Pendleton, Allen. Pinn, Pendleton and Allen each rest on a reproduced 1880 census image; Rowe and Allen on narrative statements in her paper; Syphax on O'Leary, who writes that his photograph shows he was African American. The sentence naming the five as a group sits in her own list of open inquiries, and the file records it as such. O'Leary adds that "a majority of the early office holders" were probably African-American but cannot name them. Nobody on our side has checked the census linking. | Names in O'Leary. |
| 1889–1930 | One collective sentence: the board "became and remained all white for the duration of this system" (Hjerpe 2021, p.4), sourced to the county's election records. No per-person evidence. | Names in O'Leary. |
| 1931–1986 | Nothing per-person from any source. The default rests on Newman (1987) being described as the first Black member since Reconstruction. About 280 person-years. **The weakest stretch.** | Names and honorifics in Novack (1994). |
| 1987–present | Per-person: Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), and Tejada as the first Latino member (Hjerpe 2021). The Arlington Historical Society keeps a curated entry. | Names in the county candidate history. |

None of the three roster sources states anyone's race or gender. Race comes
from Hjerpe and O'Leary; gender comes from names and honorifics, which is a
weaker attribution than a statement and is labelled as such in the file. The
seat counts for 1870–1888 are therefore Hjerpe's identifications applied to
O'Leary's roster; Alex Keena's earlier year-level counts were a replication
of the same source and are not a second one.

What any source says, in full, is ten members recorded as other than White
and twelve women (Magruder, Cannon, Buchholz, Bozman, Grotos, Whipple, Favola,
Hynes, Garvey, Cristol, Coffey and Cunningham). Everyone else, 109 of 119
people, is recorded as a white man because no source speaks to them. The
verification to ask of County staff, and through them the Historical Society,
is therefore the default rather than the lists: every other member has been
treated as a white man; where is that wrong? That is `default-1931-1986`
in `docs/questions.csv`.

Two things from the record bear on the report's argument. Monroe first stood
in the April 1999 special election for Eisenberg's unexpired seat and lost to
Michael D. Lane by 169 votes, 9,530 to 9,361; he won the two-seat general that
November. Hjerpe argues that the at-large era's members of color all won in
cycles where two seats were up; Monroe is the case where the same candidate
loses the one-seat contest and wins the two-seat one seven months later. And
the *Sun*'s coverage of the November 1938 staggered-terms referendum carries
two contemporaneous claims about women and Board structure: the Arlington
County Woman's Democratic Club opposed the change, holding that staggering
would make it "virtually impossible for a woman to be elected to the board"
(`sun1938referendum`), and a week later the Organised Women Voters of
Arlington County objected to the ballot's wording (`sun1938womenvoters`).
Florence E. Cannon is elected parliamentarian of the Organised Women Voters
in the second notice and sits on the Board from 1948 to 1951.

## Party of Board members

Party has never been printed on the County Board ballot; the county's own
candidate history says so on its first page. So there is no official record
of a member's party, only of whose candidate they were, and that is what is
coded, per term rather than per person, because a label changes between
elections (Bozman ran as ABC's candidate five times and as a Democrat once).
Three sources, in order:

1. The county's candidate history, which prints a label in parentheses after
   a name from 1931, `(D)`, `(R)`, `(ABC)`, `(I)`, though not on every winner
   and rarely before 1950.
2. The state's elections database, which records party from 2007 and is the
   only source from 2022. Where its general-election row carries no party
   (2023 on), a win in that year's Democratic primary stands in.
3. Reporting, in `data/transcribed/by_claude/board_party.csv`, one quoted and
   cited claim per row, used only where the county prints `(I)` or nothing.

Where the county and the state both name a party they must agree, and a cited
claim that contradicts a party the county prints stops the build. A label the
build has not been told what to record stops it too: `elections.LABELS` in
`code/build/` maps every label a County Board candidate has carried, and a
winner under a label only losers have carried is a decision, not a default.

**The rule for reporting** (Sally, 23 September 2026): the party or coalition
whose candidate the source says the member was, and a party's open
endorsement makes someone its candidate whatever label they ran under. Dugan
in 1946 and Vihstadt in 2014 are coded Republican with "ran as an independent"
in the note. A source saying only that someone *leaned* a party's way
(Tillema, 1952) is not an endorsement and stays independent. ABC's endorsement
counts as ABC; where a source names both ABC and a party, the party (Fisher,
1967). ABC is its own band rather than folded into Democratic, because the
county recorded it and an ABC-majority Board from 1957 to 1966 is a finding.

| Period | Source | What it gives |
|---|---|---|
| 1932–1950 | County candidate history, where it prints a label | 9 of 32 terms. The rest are `unsourced` except where McCaffrey (2026a) names the 1949–52 independents and the 1952 appointees. |
| 1951–1966 | County candidate history | Every winner but Blevins (1956) and the two `(Convention)` nominees of 1955. `(ABC)` appears from 1957. |
| 1967–1983 | County prints `(I)` on most winners; reporting names the party | Fisher, Munsey, Purdy and Wholey as Democrats; Bozman as ABC's candidate; Grotos, Frankland and Detwiler as Republicans. Ricks stays `(I)`. |
| 1984–2006 | County candidate history | Every winner labelled. Bozman `(I)` through 1989, `(D)` in 1993. |
| 2007–2021 | County and state, checked against each other | Agree on every winner. |
| 2022– | State database | Party on the 2022 general; from 2023, the Democratic primary win. |

The reporting file has 26 rows, each a sentence in the source's own words
with its citation, keyed on the name and the term's start year: pieces by
Scott McCaffrey for the Sun Gazette and ARLnow (2009–2026), the Library of
Virginia's biography of Joseph Fisher, Joseph Wholey's obituary and an ARLnow
report of the 2020 special election. What it yields for 1932–2026 is 146
terms: 76 Democratic, 18 Republican, 15 ABC, 12 independent, 25 not recorded.
The built table reproduces three compositions reported independently, three
Republicans in 1970 and again in 1979 and three independents in 1952, none of
which was used to build it.

**Not attempted before 1932.** O'Leary's own summary of the magisterial era
is that "with few exceptions, party affiliation has to be inferred", and
nothing held names a party per person; the figure starts at 1932 with a gap
before it. It is recoverable: local elections of the period were run on party
tickets and the Alexandria Gazette printed them, so an RA with O'Leary's dates
could key a ticket per winner into the reporting file.

**What is not labelled.** 23 terms have no label anywhere, 1932–1960 almost
entirely: the first two Boards (1932–39), DeLashmutt 1942–45, Campbell
1943–46, Lloyd 1945–47, Chew and Cannon 1948–51, Frisbie 1947–52, Blevins
1957–60, and four appointees. Where to look is the Northern Virginia Sun and
Arlington Daily on Virginia Chronicle, and for the 1950s Franklin Felt's 1961
dissertation on ABC (Michigan State, d.lib.msu.edu/etd/39978). Three labels
are recorded but not resolved: `(Convention)` on Kaul and Krupsaw in 1955,
whose convention the source does not name (they are `(ABC)` in 1959); `(IM)`
on Buchholz in 1954, coded independent, though if it is the Arlington
Independent Movement, the conservative counterpart to ABC, it may deserve its
own band; and Ricks (1968–71) and Brunner (1984–87), who stay independent on
the county's label although the Washington Post's 1983 preview reportedly
calls Brunner a Republican. Each finding is a row in the reporting file: the
sentence, the citation.

`board_seats.csv` carries the split as `dem`, `abc`, `rep`, `ind` and
`unrecorded`, seat-years from 1932, empty before. "Not recorded" is a band
rather than a gap because the seats existed and were held; what is missing is
the label.
