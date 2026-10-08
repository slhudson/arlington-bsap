# The Board

This write-up covers who held each seat and when, and who they were: what each
number in `data/clean/members.csv` and `data/clean/members_by_year.csv` is,
what backs it, and what is assumed where nothing does. How a decision was
reached is in the git history rather than here. `code/citekeys.py` explains the
placeholders in the `source` columns, and `docs/questions.csv` holds what is
still open.

## What rests on an assumption

**Race, 1889–1986.** Walter G. Willson (1889–92) is Black on the Gazette's
word. Every other seat is coded White on the "first since Reconstruction"
framing. The five Reconstruction-era members rest on Hjerpe's census linking
(`member-demographics-lists`). From the 1962 seating on, no census is open, so
the members seated since rest on the default unless a source names them: 40 of
126 members rest on it, 34 of them seated in 1962 or later.
`members_race_coverage` draws the seat-years that rest on it. Those 34 are
living people in Arlington, so most could be confirmed by asking.
The other six, Smith, Crocker, Robinson, Phillips, Brown and Richards, were
seated before 1962; the press names each without a racial label, which is weak
evidence at most; the searches are rows of `members_negatives.csv` (below).

**Gender.** William H. Robinson and Walter G. Willson rest on the default,
man, both searched without result (`members_negatives.csv`, below).
Every other member has a census listing or a pronoun or honorific in the
press, and `gender_evidence` in `members.csv` says which each rests on.

**Race and gender from the census.** For the members first seated 1932–1966
and 1870–1904, race and gender come from census records. Each index reading
was checked against the sheet, where the row could be found on it. The match to
the member rests on the name, on the district he sat for or on Arlington, and,
where the record gives one, on an occupation, a household or a street. No
census holds Casto, H. L. Brown Jr, Fisher, Lowry or T. W. Richards of the
later era, or H. Dwight Smith, Crocker, Schutt, Robinson or Willson of the
earlier. R. Henry Phillips's only census household is his father's, so his
birth year rests on an obituary and a railroad notice, not a census (below).

**Birth years.** Birth years are held for most members, and they rest
on the ages in census listings and on an age stated in an obituary or a
profile. Each is right to within a year. The age figure draws a year only where
every sitting member either has a birth year or is one of the two the figure
names, and it runs from 1910 to the present, the first census whose ages the
residents figures can set beside the Board's. Four members before 1910 have no
birth year: H. Dwight Smith, Lott W. Crocker, William H. Robinson and Walter G.
Willson, each found in no census under any spelling tried and in no Gazette
item that gives an age (above); they sit outside the figure. The two it names
are Susan Cunningham and Tannia Talento, recent enough that a stated age
should be findable. Naming them rather than allowing a count of unknowns is
what makes the gap a known quantity: a member who arrives without a birth year
and is not among them stops the build. Every other member seated in 1900-2026
has a birth year. The figure compares the Board to the county's adults, 18
and over, rather than to a voting-age cutoff (21 before the Twenty-sixth
Amendment in 1971, 18 after): a cutoff labelled "voting-age eligible" would
overclaim, since neither sex (women couldn't vote in 1910 or the January 1920
census) nor disenfranchisement (poll taxes and other Jim Crow mechanisms
through the mid-1960s) is modelled by age alone. Sally shelved the
voting-eligibility comparison for the flat adult one on 5 October 2026 and
confirmed the figure on 6 October. The paper's Age subsection states the
county's own age shares and does not set them against Virginia's: the
comparison the section makes is Board against county, and a statewide share
answers a question it does not ask (Sally, 6 October 2026).

**1912–1931 rests on no assumption.** `arlhist1967officials`, the Historical
Society's own compilation from the Board's minute books, names all three
magisterial seats — Arlington, Jefferson and Washington — for all twenty years.
It states the one vacancy, in the Washington seat in early 1920, rather than
leaving it silent. `members_by_year.py` reads the roster for those years like
any other (below, "The article and the other sources, 1870 to 1931").

**1870–1911 rests on O'Leary's electoral history and the same article
together.** The article settles names, the July–June term year, and
terms O'Leary does not record (below, "The article and the other sources, 1870
to 1931"). The statute behind the July
seating is `vaacts1870` ch. 76 sec. 4, below ("When the Board's year ran").
Two seats that the article gives to a different man are settled, and the roster
follows the article in both.

**Party.** Terms from 1932 that no source labels carry no party, and some
labels are unresolved. No party is attempted before 1932 (`party-unlabelled`, `party-before-1932`).

**Every place carries a precision**, read from the place's own words by rules
in `code/clean/members_residence.py`:

- a house number with a street is an address;
- a street with no number is a street;
- a neighborhood, civic association or named community is a neighborhood;
- "North Arlington" or the northernmost section is a side;
- one of Alexandria County's three magisterial districts — Arlington,
  Jefferson or Washington, as the 1880–1910 census sheets head each page — is
  a district.

A place no rule reads stops the build. A house number whose street is unread
(Ames) counts as a neighborhood.

**Before 1932 the only places are the census sheets' own.** Most members
seated 1870–1911 have a record. For nearly all of those the sheet gives a
magisterial district and nothing finer, because the street column is blank
outside the towns; Cherrydale, Washington Avenue, Old Glebe Road and
Saegmuller's Maryland Avenue house in Washington City are the exceptions.
Roach is a weak match, flagged in his row. The 1870–1920 indexes hold no record
for the remaining members under any spelling tried, R. Henry Phillips among
them — the one household read against him is his father's
(`residence-pre-1932`). The Gazette places two of them without a census:
Willson on six acres by Ballston and Smith on the Arlington township's party
committee (`gazette1894wilson`, `gazette1874smith`).

**The seat itself places nobody before 1932.** No instrument required a
supervisor to live in the district he represented before 1903, so a member
seated for a magisterial district has no claim from the office, and every place
comes from a record (below, "Residence in the district").

**Modern residence is transcribed but not yet coded.** The 1973 Post map that
places a whole Board at once has not been seen (`mathews1973-map`). Some
of the members first seated 1932–1962 have no place (`residence-1932-1962`), and
so do some of those seated 1964–1999 (`residence-1964-1999`). Two rows postdate
the member's service (`residence-after-service`). For Thomas, two sources name
different places (`thomas-residence`). Tillema's and Massey's sources also
differ, but what each source says is settled, and the census record's bib
entry says why.

Each of these is a row in `docs/questions.csv`, naming whose court it waits in
and what would settle it.

---
## Residence in the district

No instrument required a supervisor to live in the district he represented
until sec. 32 of the 1902 constitution, from 1903, so the seat places nobody
before then and every place comes from a record. The reading of each
constitution, act and Code behind that is in its entry in `paper/bib/sources.bib`
(`vaconstitution1869`, `vaacts1875`, `vacode1873`, `vacode1887`,
`vaconstitution1902`), and the departures it bears on, Schutt's, Rowe's and
Tibbett Allen's, are in `arlhist1967officials` and the Gazette entries; why
Allen left is `allen-1888`.

## The roster

`data/clean/members.csv` holds one row per person per term: name, term
number, district, when service began and ended (to the month), the months the
term held (`held_from` and `held_to`, counted from year 0, the end exclusive),
how the term began, and a source per row. The terms run from 1870 and come from
four sources in sequence: O'Leary's electoral history to 1915, the Historical Society's
article for 1870–1931, Novack's roster from 1932 to
1994, and election results after that, the county's candidate history to 2021
and the state's elections database from 2022.

A term is the natural unit: person-years fall out of it, while a term starting
in May or ending in February cannot be recovered from a list of years. A
vacant seat is not a row, since nobody served. `term_number` counts within a
person, so someone appointed to a vacancy who then won twice has three rows
numbered 1, 2, 3; William A. Rowe's rows run longer, and include his move from
Jefferson district to Arlington.

`seated_by` says how each term began: election, special election, appointment,
or unrecorded where O'Leary writes only that someone was replaced. Three builds
select terms by it, so it is a column, not something read out of the note.

### What the county's roll adds

**Novack records service and election returns record contests**, and the
county's roll records service too, so the roll dates the departures and
arrivals no contest shows, Tannia Talento's appointment of 15 July 2023 among
them, and is a second witness to Novack for 1932 to 1994.
`code/clean/members_roster_roll.py` reads it: `check_against_novack` holds the
two to each other, `OVERRULED` holds the one disagreement a third source decides: the roll
dates Massey's appointment later than Novack and the *Daily Sun* do
(`dailysun1952appointees`). A disagreement with no third source stops the
build.

**A month belongs to whoever held the seat for any part of it.** Where a gap
covers a whole month the seat was empty, and these months since 1932 were:
March and April 1990, October 1997, March 1999, February 2003, January and
February 2012, March 2014, and May and June 2020. Each is a seat Arlington left
unfilled while a special election was called, the Board sitting with four
members. `members_roster_roll.EMPTY` names the departure and the arrival that
bracket each, and `check_seats` holds the roster to them: an undeclared gap
stops the build, and so does filling a declared one. No one was appointed to
any of those months; Talento's is the only appointment to the Board since 1975
(`arlnow2014zimmerman`).

**A resignation inside a month the member still holds is no vacancy.** Ellen
Bozman resigned the rest of her first term on 2 December 1977 (`sun1977bozman`);
she held part of December, so the month stays hers and the year reads five
seats.

### When a term runs

**When a term begins depends on the constitution in force.** Under the
magisterial system elections were held in May and the winners took office on
1 July following, so those terms run July to June. The 1902
constitution moved county and district
elections to November and seated their winners on 1 January following (sec.
112, `vaconstitution1902`), so from the November 1903 election a term runs
January to January; the County Manager plan seats members on 1 January too,
so the convention is unbroken from 1904 on. The Schedule of the 1902
constitution governs the first election held under it, and confirms this: its
sec. 10 holds the first election of county and district officers "under this
Constitution" on the Tuesday after the first Monday in November 1903, terms
"to begin on the first day of January, next after their election" - the same
rule sec. 112 states for every later election. Sec. 10's second paragraph
names "supervisors of the several counties" among the offices whose sitting
holders are continued only "until January the first, nineteen hundred and
four", so the incoming November 1903 winners are seated then and not before.
The November 1903 handover therefore falls in January 1904 like every other,
in a stretch where every member is coded a white man.

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
speaks to four. Their terms close in January 1912, where the Historical
Society's article picks the seats up. The note on such a row says the end is the statute's; where
the next listed election seats a successor on the same date the departure is
sourced and carries no note.

**The Board's year ran 1 July to 30 June through 1901.** Elected in November,
start in January; elected in May, start in July. Being elected is not taking
office, and the two halves rest on different things:
`members_roster_oleary.seated()` carries the November half on
`vaconstitution1902` sec. 112, and the May half on ch. 76 sec. 4 of the 1870
acts: the term of "all corporation and township officers chosen at a general
election ... shall commence on the first day of July next thereafter," and
sec. 14 of the same chapter makes a supervisor a township officer, chosen at
the May general election (`vaacts1870`). Every term block
the article prints for 1870–1901 runs 1 July to 30 June. Its own footnote at
1901 corroborates the arithmetic. The 1902 constitution moved the Board to
four-year calendar terms, and "the extra six months of this Board covered the
transition period" — a term running 1 July 1901 to 31 December 1903, which is
thirty months on a July–June year and thirty-two on a May one. `BOARD_FROM`
moves with it: the Board elected in May 1870 first sat on 1 July, so the three
seats are empty for six months of 1870, not four.

The article prints "township" through the block ending 30 June 1874 and
"district" from 1 July 1874 on, four months before the amendment was ratified.
The roster says districts throughout, and that is correct, not a
simplification: ch. 76 sec. 1 of the 1874–75 acts, approved 5 February 1875,
declares the townships as they stood on 3 November 1874 to be the magisterial
districts, keeping their boundaries, names and voting places, and ch. 69 sec. 1
directs that "township" in any earlier statute be read as the district
(`vaacts1875`). Same lines, same three names. The townships began with the 1869
constitution and did not predate 1870, so nothing is carried back across a
boundary change that never happened.

### The law behind the Board

Part A begins with Alexandria County and the 1869 constitution and goes no
further back. The earlier governments of the land are filed and cited should
the prose want them: usstat1790residence, usstat1801organic,
usstat1801supplementary, arlingtonva2011markers, nps2025rooseveltisland.

How the constitutions, acts, the County Code and the Board's own papers made
the Board and divide its work with the Manager is the report's, in Part A, and
each source's reading is in its entry's `annotation` in `paper/bib/sources.bib`.
The non-interference bar vaacts1952c443 wrote and vaacts1962c623 carried
unchanged is softened by 1982 c. 108 (vaacts1982c108): the bar on directing or
requesting an appointment, or taking any part in one, narrows to a bar on
dictating one outright; a sentence lets the Board discuss appointments and
removals with the Manager; and the misdemeanor and the forfeiture of office
are struck. Every change between the 1952 text and today's sec. 15.2-703 is
this act's, not the 1997 recodification's. 1993 c. 731 (vaacts1993c731), the
other act `law-library-access` tracked, touches a different section - sec.
15.1-676's election and vacancy machinery, not the bar - and its history
belongs with Election Method once that section is drafted. What is not held
is tracked: `county-code-board-manager` for the County's papers, and
`county-manager-statutes-other-states` for whether Arlington was the first
county to adopt the plan by vote.

### The article and the other sources, 1870 to 1931

`arlhist1967officials`, the Historical Society's compilation from the Board's
minute books, names all three seats for 1912 to 1931 save the one vacancy it
states, and for 1870 to 1911 corrects and adds to O'Leary's elections. How it
is read, and every name it settles, term it adds, vacancy it states and seat it
gives to another man, is in `code/clean/members_roster_arlhist.py` (`NAMES`,
`ADDED`, `VACATED`, `SEATED`, `READING_NOTES`), and each row of `members.csv`
it changes carries a note saying what settled it. Three rulings stand behind
those entries:

- the article dates a term from the first record of a man sitting, not from
  the instrument that named him: Hume was appointed on 2 October 1888 and is
  first shown present on 13 November, the date the roster uses;
- the roster records who held a seat, not who held title to it, so where an
  election return and the minute books disagree about who sat, the minute
  books answer: Torreyson holds the Arlington seat to 11 October 1897 and
  Corbett from then, Boyd never holds the Jefferson seat of 1870, and the
  Washington seat of 1897-99 is Saegmuller's (Sally);
- O'Leary is an electoral history, naming a departure only where his prose
  happens to, so where the article names a supervisor he does not, he is
  silent rather than contradicting (Sally).

**Where these readings bear on the central figure.** Some of them shorten a
Black member's recorded service:

- the added terms close Pinn's, Pendleton's and Allen's mid-term, where
  O'Leary's elections would run them out;
- the July term year moves a start off May in each year a Black member's
  service begins, 1871, 1872, 1879 and 1887;
- Rowe's resignation stands the Jefferson seat empty from April to June 1879. Reading
O'Leary's elections alone would give every one of those months to a sitting
member. `members_by_race` counts what the roster holds, and no count of it is
kept here.

`members_roster.check_district_seats` holds the reading in place: each of the
three districts has exactly one member in every month from 1870 to 1931, save
the six months before the Board sat and three recorded vacancies: Washington
from July to November 1873, Jefferson from April to June 1879, after Rowe's
resignation, and Washington in January 1920, after Clarence R. Ahalt, elected
to it, moved from the district before the term began. A gap anywhere else
stops the build, and so does filling one of these.

## Seat-years

`data/clean/members_by_year.csv` is one row per year from 1870: seats
held by each race, each gender, (from 1932) each party, what the member's race rests on
(a census sheet, a published or press account, or the default), and the most exact place any source gives, in seat-years, so a
member who sat for four months of a year counts 4/12. Every year is computed
from `members.csv`. Days are not recorded consistently — Novack gives some and
the election dates others — so the month is the unit, and **the handover month
belongs to the incoming member** (Sally). An end no source
records holds to the end of the term's first year. Both rules are applied once,
in `held_from` and `held_to` on `members.csv`; the seat-years and the figures
of who was sitting on 1 July read those columns, not the dates. Prorating within a
month would be more exact and would make a seat-year a fraction of a month,
which nothing else here counts below.

The denominator is the months the Board existed that year, which is twelve for
every year but its first. Arlington's Board came into existence at the May
1870 election, so 1870 is scaled by the eight months it existed: it reads
three seats filled, because they were, for as long as there was a Board to
fill them. Divided by twelve it would read two, and a chart of that says the
Board grew from two seats to three, which it did not.

The seats held can never exceed the seats that exist: three magisterial
districts with one supervisor each from 1870, and five members elected
countywide from the County Manager plan, which the referendum of 4 November 1930
adopted and which seated its first Board in January 1932. The seats held fall
short only in 1873 and 1990. Anything else stops the build. Race, gender and party are independent splits of the same
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

## The chair

`data/clean/members_chairs.csv` holds the chair of every year from 1932 and the
vice-chair from 1967, read off the county's roll (`arlingtonva2026members`), and
is kept out of `members.csv`, where every row is a term. The Board elects both
at its first meeting of the year, and nothing in law ties the chair to a seat's
election year (`vacode2020chairelection`); since 1990 the custom is succession,
each vice-chair the next year's chair (`arlnow2026chair`).

**A figure of chair-years by race and gender is not built.** Because the chair
follows the vice-chair, who follows the order of the Board, it would repeat the
seat-years figures with a year's delay. The first Black chair, Newman in 1991,
and the first woman to chair in the roll, Magruder in 1938, are a sentence of
prose.

## Where members lived

`data/clean/members_residence.csv` holds one row per claim about a member's
home: the place as the source names it, how exactly (`precision`: a street
address, a street name, a neighborhood, a side of the County or a
magisterial district), the year the source gives, and the source. Nothing is
coded North or South and no claim is chosen over another; the coverage
figure takes each member's most exact dated place in each year.

**How much is known, for the members first seated from 1932 on.** A member
is counted under the most exact kind of place any source gives him, and dated
by the best-dated row of that kind: during service if the row's year falls
inside a term, otherwise by the distance to the nearest term's ends. Every
census read moves these numbers, so the count is not kept by hand:
`test_the_residence_coverage_table_in_the_write_up_is_current` in
`code/tests.py` recomputes it from the clean tables on every build and fails
with both sets of figures when the table below stops matching.

| Most exact place held | Dated during service | Within 5 years of it | 6 or more years from it | Undated | Members |
|---|---|---|---|---|---|
| Street address | 14 | 19 | 8 | 0 | 41 |
| Street name | 2 | 0 | 1 | 0 | 3 |
| Neighborhood | 10 | 1 | 4 | 2 | 17 |
| Side of the County | 1 | 1 | 0 | 0 | 2 |
| Nothing | | | | | 13 |

So most members have a place of some kind and many a street address, but
only a minority are placed by a source dated to their service. The
sources found online give a place at the time of writing, an obituary's
address is where the person died, and a candidate profile's is where they
lived when they ran; County records may give an address at taking office
(`residence-county-records`). Whether a place dated after service should
count, and within what window, is `residence-after-service`; the coverage
figure counts any dated place, since it shows the state of the evidence,
and the window matters to the neighborhood analysis, which is not yet built.

## Census records

Each census record matched to a member is one row of
`data/transcribed/by_claude/members_census.csv`, holding records from the
1870, 1880, 1900, 1910, 1920, 1930, 1940 and 1950 schedules. What each column
holds, what counts as a match and how the printed values are coded is in the
docstring of `code/clean/members_census.py`; how the claim files keep words
rather than categories is in `code/clean/members.py`. Which rows have not
yet been read for a tie is `census-match-quality`.

One record is filed and cited but kept out of the table, because its birth
year disagrees with the member's other record and the build stops on two
sources disagreeing: William Duncan's 1910 (`census1910duncanwilliam`), which
waits on `duncan-birth-year`.

### Reading an image

How a record or a page is read off its image is in the `sources` skill,
"Reading an image".

### What has been searched for the members who keep a default

Every search that came back empty is a row of
`data/transcribed/by_claude/members_negatives.csv`: the member, the field
sought, the collection searched, the span, how, and what came back.
`code/tests.py` refuses a member first seated before 1962 whose race, gender or
birth year rests on the default with no row there. What a missing racial label
is worth depends on the paper's habit, which the report's Data Appendix sets out
under Race and Ethnicity: it is no confirmation of White.

## Race, gender and birth year of Board members

Birth years come from the same files as race and gender, one row per source,
and reach `members.csv` as `birth_year` with a source and a note. With no
source the year is blank and `unsourced`, because no standing assumption stands
in.

Two kinds of source give a year. A census listing gives an age, and the year is
the census year less the age, so it is right to within a year — except where
the index prints a birth date. An obituary or a profile gives a birth date, or
an age on a date, and the row's basis says which.

`birth_year_precision` in `members.csv` records which case a row is, `exact` or
`within a year`; most are within a year. The age figures draw both the
same way, as a stroke assuming a mid-year birthday, because the half-year is
below what a stroke can show (Sally). What the report
does with such distinctions is the data appendix's to explain
(`data-appendix`). For members
seated 1960 on the sources are obituaries on legacy.com,
Dignity Memorial and InsideNoVa, candidate profiles in the Connection,
ARLnow and Patch, a Senate of Virginia member page, and the Post's archive
where it shows the paragraph that carries the age. The build refuses a year
that would seat a member under 18 or over 100, and two sources disagreeing
stop it. `election_year` on each elected term is the election that seated
it, a January start following a November election, so a figure can
subtract without re-deriving that rule.

Race and gender come from `data/transcribed/by_claude/members_demographics.csv`,
one row per claim a source makes about a member, in the source's own words
with a citation to the page the document prints, and from the census records
above; and otherwise from a default,
a white man, labelled `assumed`. Each cell of `members.csv` says which, and
`gender_evidence` says how a gender is known: `record` (a census listing),
`press` (the pronoun or honorific a paper uses for the member; each such row
of the claim file quotes the sentence and cites the page), both joined with
`; `, or `none` where the default stands. Two sources disagreeing about a person stops the build, and an attributed name
that matches no roster name stops it too, so a near-miss cannot fall silently
into the default. The default is a claim, and this is what stands behind it in
each period:

| Period | Race | Gender |
|---|---|---|
| 1870–1888 | Five Black members named by Hjerpe (2021): Rowe, Syphax, Pinn, Pendleton, Allen. Pinn, Pendleton and Allen each rest on a reproduced 1880 census image; Rowe and Allen on narrative statements in her paper; Syphax on O'Leary, who writes that his photograph shows he was African American. The sentence naming the five as a group sits in her own list of open inquiries, and the file records it as such. O'Leary adds that "a majority of the early office holders" were probably African-American but cannot name them. The census linking is unchecked. | Names in O'Leary; two before 1912, Robinson and Willson, still rest on the default (above, "What rests on an assumption"). |
| 1889–1930 | Willson (1889–92) is Black on the Gazette's word, three notices that read "colored" (above). For every other member, one collective sentence: the board "became and remained all white for the duration of this system" (Hjerpe 2021, p.4), sourced to the county's election records, which the Gazette contradicts for 1889 and 1891. No per-person evidence. | Names in O'Leary; initials only before 1912. No source names a first woman member, so "all men before Magruder (1932)" is assumed. |
| 1931–1986 | Nothing per-person from any source, except that the county's list of the November 1931 candidates marks three of its 51 names "(Col)" and none of the five elected (`docs/candidates.md`, "Black candidacies"). The default rests on Newman (1987) being described as the first Black member since Reconstruction. **The weakest stretch.** | Census listing or a press honorific or pronoun for all but B. M. Smith (1933). |
| 1987–present | Per-person: Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), and Tejada as the first Latino member (Hjerpe 2021). The Arlington Historical Society's Newman entry names Newman, Monroe and Dorsey as African American members, and its Center for Local History entry gives Tejada's Latin American heritage; Monroe also rests on the Arlington NAACP president's words at his death, and Dorsey on his own statement (2020). | A press pronoun or honorific for every member. |

In November 1931 three Black candidates ran for the Board and all lost; who
they were, and every other Black candidacy, is in `docs/candidates.md` under
"Black candidacies".

No roster source states anyone's race or gender. Race comes
from Hjerpe and O'Leary; gender comes from a census listing or from the
pronoun or honorific a paper uses for the member, and where neither has been
found the default stands, labelled `assumed`. The
seat counts for 1870–1888 are therefore Hjerpe's identifications applied to
O'Leary's roster; Alex Keena's year-level counts are a replication
of the same source and not a second one.

What any source says, in full, is that Rowe, Syphax, Pinn, Pendleton, Allen,
Newman, Monroe, Dorsey, Spain, Tejada and Talento are recorded as other than
White and that Magruder, Cannon, Buchholz, Bozman, Grotos, Whipple, Favola,
Hynes, Garvey, Cristol, Talento, Coffey and Cunningham are women. Every other member is recorded
as a white man because no source speaks to them. The verification to ask of
County staff, and through them the Historical Society, is therefore the
default, not the lists: every other member has been treated as a white man;
where is that wrong? That is `member-demographics-lists` in `docs/questions.csv`.

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

### The voting-rights era

One secondary source, the Congressional Research Service's history of the Act
(`crs2023votingrightsact`), covers all four items the race timeline may name.

- The Voting Rights Act is signed on 6 August 1965 (P.L. 89-110) and prohibits
  discrimination in registration and voting on the basis of race, color or
  language-minority status (Table 2, p. 5; Summary); its Section 5 requires
  federal review of voting changes before they take effect in certain
  jurisdictions (Table 1, p. 3).
- Section 4(b) covers six states entirely when the Act is enacted in 1965,
  Virginia among them (p. 14).
- *City of Mobile v. Bolden* (22 April 1980) reads Section 2 to require proof
  of discriminatory intent, and Congress amends the Act in 1982 in response
  (Table 2, p. 5; p. 21).
- *Thornburg v. Gingles* (30 June 1986) sets the standard for vote-dilution
  claims under Section 2, which the report ties to the 1982 amendment's
  attention to at-large elections (Table 2, p. 5; p. 22).

Arlington is covered by Section 5 from the start, and the Justice Department's
published records name it in submissions but in no objection.

- **Coverage.** Virginia is covered in its entirety under the 1965 formula,
  coverage dating from 1 November 1964, so the state and all its political
  subdivisions need preclearance for voting changes
  (`doj2023section4bailouts`; `doj2023section5covered`, the Virginia row).
  Neither page names a locality as covered. Arlington is not among the
  Virginia jurisdictions listed as bailed out, the first being the City of
  Fairfax on 21 October 1997 (`doj2023section4bailouts`, the bailout list).
- **Submissions naming Arlington.** The Division's periodic notices of
  preclearance activity list each submission by state, county and subject.
  Twelve notices between 19 February 1999 and 6 July 2001 carry a line for
  Arlington County, one submission each: two vacancy special-election
  procedures (February 1999, July 2000), voter registration hours or
  locations (May 1999, October 2000), four changed polling places (July to
  November 1999), a bond election (September and October 2000), a voting
  machine (June 2001) and a precinct realignment (July 2001). The notices
  record receipt and requests only and state no outcome, and they do not say
  whether the vacancy procedures concerned Board seats. They are cited
  nowhere: the changes are administrative and none concerns how the Board
  is chosen, so no source entry is kept for them; the notices are at
  justice.gov/crt under "Notice of Preclearance Activity".
- **Objections naming Arlington.** None. The Division's list of Virginia
  objection letters runs from 26 June 1970 to 21 October 2003, 33 entries
  for the State of Virginia and named cities and counties, and does not name
  Arlington (`doj2015section5virginiaobjections`).
- **Statewide records covering Arlington without naming it.** The objections
  to the State's own changes - Senate and House multi-member districts
  (7 May 1971), redistricting (1981, 1982 and 1991) and a prohibition on
  candidates assisting voters (3 August 1984) - apply to every Virginia
  locality including Arlington
  (`doj2015section5virginiaobjections`, entries for the State of Virginia);
  they are the State's changes and the list does not say what they meant for
  Arlington.

No submission or objection on election method is found. The Board's at-large
election dates from November 1931, before the Act, and no record found in
the notices or the objection list shows the method itself, or any change to
it, going before the Justice Department. The 479 notices held run from April 1998 to August 2008, as published
at the two addresses the Division uses for them; submissions before April 1998 or after August 2008 are not in
anything held, and the Division's own list of changes by type and year is
national and names no locality. Whether Arlington submitted anything between
1965 and 1998, and what became of the twelve submissions, rests on
the County's own record of its submissions; no published Division record
found gives an outcome for a submission it did not object to. Neither *City of Mobile v. Bolden* nor *Thornburg v. Gingles* is tied to
Arlington by any source held.

## Party of Board members

Party has never been printed on the County Board ballot; the county's own
candidate history says so on its first page. So there is no official record of
a member's party, only of whose candidate they were, and that is what is coded,
per term, not per person, because a label changes between elections (Bozman ran
as ABC's candidate five times and as a Democrat once). Three sources, in order:

1. The county's candidate history, which prints a label in parentheses after
   a name from 1931, `(D)`, `(R)`, `(ABC)`, `(I)`, though not on every winner
   and rarely before 1950.
2. The state's elections database, which records party from 2007 and is the
   only source from 2022. Where its general-election row carries no party
   (2023 on), a win in that year's Democratic primary stands in.
3. Reporting, in `data/transcribed/by_claude/members_party.csv`, one quoted and
   cited claim per row, used only where the county prints `(I)` or nothing.

Where the county and the state both name a party they must agree, and a cited
claim that contradicts a party the county prints stops the build. A label the
build has not been told what to record stops it too: `elections.LABELS` in
`code/build/` maps every label a County Board candidate has carried, and a
winner under a label only losers have carried is a decision, not a default.

**The rule for reporting** (Sally): the party or coalition
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
| 1932–1950 | County candidate history, where it prints a label | The county's label where it prints one, newspaper reporting for 1933 and 1942–49, McCaffrey (2026a) for the 1949–52 independents and the 1952 appointees; the rest are `unsourced`. |
| 1951–1966 | County candidate history | Every winner but Blevins (1956) and the two `(Convention)` nominees of 1955. `(ABC)` appears from 1957. |
| 1967–1983 | County prints `(I)` on most winners; reporting names the party | Fisher, Munsey, Purdy and Wholey as Democrats; Bozman as ABC's candidate; Grotos, Frankland and Detwiler as Republicans. Ricks stays `(I)`. |
| 1984–2006 | County candidate history | Every winner labelled. Bozman `(I)` through 1989, `(D)` in 1993. |
| 2007–2021 | County and state, checked against each other | Agree on every winner. |
| 2022– | State database | Party on the 2022 general; from 2023, the Democratic primary win. |

The reporting file holds a sentence in the source's own words for each
claim, with its citation, keyed on the name and the term's start year: pieces by
Scott McCaffrey for the Sun Gazette and ARLnow (2009–2026), the Library of
Virginia's biography of Joseph Fisher, Joseph Wholey's obituary and an ARLnow
report of the 2020 special election. The built table reproduces three compositions reported independently, three
Republicans in 1970 and again in 1979 and three independents in 1952, none of
which was used to build it.

**Not attempted before 1932.** O'Leary's own summary of the magisterial era
is that "with few exceptions, party affiliation has to be inferred", and
nothing held names a party per person; the figure starts at 1932 with a gap
before it. It is recoverable from the Alexandria Gazette (Chronicling
America, sn85025007), which prints the result of each May election. Tried:
1895 (Grunwell, Corbett and Duncan were elected on "the entire republican
ticket", 24 May 1895, p. 3) and 1871 (Deeble on "the whole Conservative
ticket", 26 May 1871, p. 3; Smith and Rowe unlabelled). 1872–73 were read
and print no party beside the supervisors; 1874–75 were fetched and not read. Paused, and no row is keyed for
any of these: the County has not said it wants these data used.

**What is not labelled.** These terms have no label anywhere: the four 1932
winners (Magruder, Fellows, Gall, Kelley), B. M. Smith 1933, McShea 1934,
the four 1936 winners (Magruder, Chew, Yeatman, McShea), Wilt 1960 and
Richards 1975. Read and settled from the Sun, Daily Sun, Northern Virginia
Sun and Evening Star: DeLashmutt 1942, Campbell 1943, Lloyd 1945, Cuppett,
Frisbie (three terms), Chew and Cannon 1948, Garnett 1933, Krupsaw, Kaul,
Blevins, Ricks and Buchholz 1955. `(Convention)` on Kaul and Krupsaw in 1955
is ABC's nominating meeting (Daily Sun, 25 May 1955). `(IM)` on Buchholz in
1954 is the Arlington Independent Movement, whose nominee the Evening Star
calls her; AIM candidates (Buchholz, Blevins) are coded independent, so
whether AIM is a band of its own is open. Ricks was backed by ABC and the
Democratic party and is coded Democratic, as Fisher is.

The 1931 election was non-partisan in what the papers print: the Washington
Times of 4–5 November 1931 labels Gosnell alone ("Republican nominee"), the
Evening Star of 5 November prints no party, and on 2 January 1936 the Sun
calls Ames "the only Republican" on the Board. That leaves the other 1932 and
1936 winners without a printed party. Not found: Smith 1933, McShea 1934
(Evening Star searches by name returned no article) and Wilt 1960 (the
Northern Virginia Sun's OCR for January 1960 is too poor to search). Brunner
(1984–87) stays on the county's `(I)`; the 1983 Post preview is not read.

`members_by_year.csv` carries the split as `dem`, `abc`, `rep`, `ind` and
`unrecorded`, seat-years from 1932, empty before. "Not recorded" is a band
rather than a gap because the seats existed and were held; what is missing is
the label.
