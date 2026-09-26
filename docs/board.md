# The Board

Who held each seat and when, and who they were: what each number in
`data/clean/board_members.csv` and `data/clean/board_seats.csv` is, what backs
it, what is assumed where nothing does, and why. Present tense; how a decision
was reached is in the git history. The placeholders in the `source` columns
are explained in `code/citekeys.py`, and what is still open is in
`docs/questions.csv`.


## What rests on an assumption

- 1889–1986 is coded all-White on the "first since Reconstruction" framing,
  and the five Reconstruction-era members rest on Hjerpe's census linking
  (`default-1931-1986`).
- Gender rests on the default (man) for 29 members: 25 seated before 1912, the
  three of 1916–20 (Wibirt, Duncan, Walker) and B. M. Smith (1933). The
  other 90 have a census listing (50) or a pronoun or honorific in the press
  (43; three have both).
  `gender_evidence` in `board_members.csv` says which (`gender-from-names`).
- For 33 members first seated 1932–1966 and 16 first seated 1870–1904,
  race and gender come from 53 census records, each index reading checked
  against the sheet where the row could be found on it; the match
  to the member rests on the name, Arlington and, where the index gives
  one, an occupation, a spouse or a street, and four of that era were found
  in no census (B. M. Smith, H. L. Brown Jr, T. W. Richards, R. L. Lowry).
- Birth years, for 88 of 119 members, rest on the census listings' ages and
  on an age stated in an obituary or a profile, each right to within a
  year, and the age figure draws a year only when all but at most
  one sitting member has one. The figure is not in the paper yet, and it
  starts in 1932.
- 1912–1931 names five terms and no more; the seats for those years are
  assumed, not counted from them.
- From 1907 O'Leary's surnames are not joined to earlier full names
  (`surnames-from-1907`).
- 23 terms from 1932 carry no party, three labels are unresolved, and no
  party is attempted before 1932 (`party-unlabelled`, `party-before-1932`).
- The 1930 candidacies of Harris, Morton and Mosley rest on a page nobody has
  read (`bestebreurtje-p215`).
- Each place carries a precision, from the place's own words by rules in
  `code/clean/board_residence.py`: a house number with a street is an address;
  a street with no number, a street; a neighborhood, civic association or
  named community, a neighborhood; and "North Arlington" or the northernmost
  section, a side; and one of the three magisterial districts of Alexandria
  County, Arlington, Jefferson or Washington, as the 1880–1910 census sheets
  head each page, a district. A place no rule reads stops the build. A house
  number whose street is unread (Ames) counts as a neighborhood.
- Before 1932 the only places are the census sheets' own: 34 of the 41
  members seated 1870–1911 have a record, and for 29 of them the sheet gives
  a magisterial district and nothing finer, since the street column is blank
  outside the towns; Cherrydale, Washington Avenue, Old Glebe Road and
  Saegmuller's Maryland Avenue house in Washington City are the exceptions.
  Two of the 34 are weak matches, Roach and R. Henry Phillips, flagged in
  their rows. Seven have no record in the 1870–1920 indexes under any
  spelling tried (`residence-pre-1932`).
- Every member seated for a magisterial district also has a district claim
  from the office, source `derived`, and 1912–1931, where no roster exists,
  the figure counts the Board's three seats at district precision. Both rest
  on the assumption that a supervisor lived in the district he represented
  (`code/clean/residence_district.py`). Sec. 32 of the 1902 constitution
  requires it from 1903; the 1869 constitution's Art. I sec. 2 makes every
  voter eligible to any office "within the gift of the people" with no
  residence clause, and the 1873 Code has not been read
  (`residence-district`).
- Where members lived is transcribed but not yet coded, and the 1973 Post map
  that places a whole Board at once has not been seen (`mathews1973-map`);
  two of the 37 members first seated 1932–1962 have none
  (`residence-1932-1962`), 10 of the 25 seated 1964–1999 have none
  (`residence-1964-1999`), two rows postdate the member's service
  (`residence-after-service`), and for Thomas two sources name different
  places (`thomas-residence`). Tillema's and Massey's two sources also
  differ, but which each source says is settled; see "Reading an image".
- Thirteen county board sizes rest on search summaries of county web pages,
  not on a document held (`county-seat-counts`); Arlington's five is the
  County Attorney's.

Each is a row in `docs/questions.csv`, with an owner and what would settle it.

---

## Local legal authority

The two Dillon's Rule opinions the paper's local legal authority section
cites, `commonwealthvarlington1977` and `arlingtonvwhite2000`, are both held,
read from CourtListener and filed in Drive under `legal/`.

---

## The roster

`data/clean/board_members.csv` holds one row per person per term: name, term
number, district, when service began and ended (to the month), the months the
term held (`held_from` and `held_to`, counted from year 0, the end exclusive),
how the term began, and a source per row. 222 terms, 1870 through 2026, from three sources
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

**The constitution created the Board; the acts of 1870 stood it up.** The
constitution framed in 1868 and ratified in 1869 divides every county into not
fewer than three townships, has one supervisor elected annually in each, and
provides that "The Supervisors of each township shall constitute the Board of
Supervisors for that county" (art. VII sec. 2, `vaconstitution1868`). The
mechanism is the constitution itself, not an enabling act; prose should say so
rather than "under the post-Civil War constitution". Three acts of the 1869–70
session then made it exist in fact: ch. 39, approved 2 April 1870, has the
governor appoint five commissioners in each county to lay it off into
townships; ch. 76 sec. 14, approved 11 May 1870, has one supervisor chosen in
each township at the May general election; and ch. 188 sec. 2, approved 11
July 1870, repeats the constitutional sentence and gives the board a corporate
name it can sue and be sued by (`vaacts1870`). That order is why the roster
starts at the May 1870 election and not at ratification.

**Townships became magisterial districts in 1875, without a change of unit.**
An amendment to art. VII respecting county organization was ratified on 3
November 1874, and ch. 76 of the 1874–75 session, approved 5 February 1875,
declares the townships as they stood on that date to be the magisterial
districts the amendment directs, keeping their boundaries, names and voting
places; ch. 69, approved 2 February 1875, makes "township" in any earlier
statute read as those districts (`vaacts1875`). The conversion renames units
Alexandria County already had, which is why the roster shows no seat-count
change at that point. The amendment's own text has not been read: both
chapters describe it and date its ratification, and that is what is cited.

**Before 1870 the county court governed, and its justices were elected by
district from 1852.** The 1851 constitution puts a County Court in each
county, "held monthly, by not less than three nor more than five Justices",
with the jurisdiction of the existing county courts, and lays each county off
into districts in which the voters elect four Justices of the Peace for four
years (art. VI secs. 25–27, `vaconstitution1851`). The administrative work is
that court's: the Code of Virginia in force through the period has the county
levy laid by the court of the county, made up annually in May or June "when a
majority of the acting justices of the county is present" (ch. 53 secs. 1 and
3), and the court held "by the justices of the county or corporation, or any
four or more of them" (ch. 157 sec. 1, `vacode1860`). So the 1870 Board is the
county's first elected governing body of this kind, and the elected element
before it reached only the justices who composed the court. Both sources apply
by their terms to every county and name none, so this is Alexandria County's
arrangement by generality, not from a document about this county; nothing held
says the county was treated as an exception.

**The Board's name changed with its form.** Members elected by magisterial
district were supervisors: the county's own returns print "Supervisor Jefferson
District" for the election of 8 November 1927 (arlingtonelections2021 p.4), and
Corbett's 1910 census occupation is "Supervisor, County". Arlington adopted the
County Manager Plan by referendum in 1930 and has operated under it since 1932;
samuel2026 note 8 records that the Plan "appears to be the only county form of
government that does not refer to its Board members as 'supervisors'". The
name, the at-large method and the five seats therefore arrive together, and
prose should not carry one back across 1932 without the others.

**When a term begins depends on the constitution in force.** Under the
magisterial system elections were held in May and the board took office then,
so those terms run May to May. The 1902 constitution moved county and district
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
speaks to four. Their terms close in January 1912, and nothing names who held
those seats next. The note on such a row says the end is the statute's; where
the next listed election seats a successor on the same date the departure is
sourced and carries no note.

**So the roster names almost nobody from 1912 to 1931.** No source in hand
records who served, and the seat counts for those years are an assumption,
stated in `code/clean/board_seats.py` and labelled `assumed`: three seats,
filled, held by white men. `board_seats` states those years itself and
replaces whatever the roster holds for them, so a name added to the roster
moves no seat-year; `code/tests.py` adds a member in 1925 and checks that
the table for 1912–1931 does not change. Two elections inside the stretch are printed in the county's
candidate history under the district headings rather than under "County
Board": November 1923 (Ingram in Arlington, Duncan in Jefferson, Thornburke
in Washington, each the only name listed) and November 1927 (Duncan and
Thornburke, each with the highest vote). They are keyed in
`data/transcribed/by_claude/board_terms.csv`, page 2 and page 4, as five
terms seated the following January, with no end: the county gives neither a
start nor an end, so the January start is the build's rule for a November
winner and each term holds to the end of its first year (1924 and 1928). Ingram and Thornburke appear in no
other source; both are marked "(inc.)" in 1923, so they were elected at one
of the unrecorded elections after 1915, and the Alexandria Gazette and the
Washington Star are where to look for the rest. Duncan is very likely the
Duncan who held Jefferson from 1895 in O'Leary, which would make the gap two
seats wide rather than three; the roster does not join him to "E. Duncan"
(see the surnames row below).

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
above whatever the roster holds for them. Days are not recorded consistently, Novack giving some and the election
dates others, so the month is the unit, and **the handover month belongs to
the incoming member** (Sally, 22 September 2026). An end no source records
holds to the end of the term's first year. Both rules are applied once, in
`held_from` and `held_to` on `board_members.csv`; the seat-years and the
figures of who was sitting on 1 July read those columns rather than the dates.

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

## Census records

A census listing names a person, not a Board member, and gives several
traits at once, so each record matched to a member is one row of
`data/transcribed/by_claude/board_census.csv`, and the build derives each
trait from it rather than each trait being keyed separately. 72 records, for
68 members, from the 1880, 1900, 1910, 1930, 1940 and 1950 schedules. The
columns:

| Column | Holds |
|---|---|
| `name`, `source` | the roster name and the record's citekey, `census<year><surname>` |
| `year` | the census year |
| `basis` | what ties the record to the member, stated once: the name, the place, and an occupation, a spouse or a house number where one agrees; where the index misreads a name, what it reads |
| `checked` | what was read against the image: `read against the sheet, which agrees`, or what the sheet gives where it differs from the index. Every row names the sheet; see "Reading an image" |
| `gender`, `race`, `age`, `birthplace`, `occupation` | as the index prints them: `Male`, `Mulatto`, `39` |
| `birth_year` | a birth year the index prints as a date rather than as its `abt` estimate from the age (the 1900 schedule records a month and year); blank otherwise |
| `place` | the street and house number as read for residence, from the sheet where the sheet was read; blank where no one has read it for that purpose |
| `quote` | the index listing verbatim |
| `sheet` | the sheet's lines verbatim, where they were read |

`code/clean/board_census.py` codes the printed values: `Male` a man,
`Female` a woman, `White` White, and both `Black` and `Mulatto` Black, as
Hjerpe codes Pinn's 1880 record. A printed value it has no code for stops
the build, since a dropped claim would fall silently into the default, and
so does a row whose `checked` names neither the sheet nor the index. The
birth year is the one the index prints as a date, or else the census year
less the age, and the note on it says which. The place joins the claims in
`data/transcribed/by_claude/board_residence.csv` in
`data/clean/board_residence.csv`, one row per claim, none chosen over
another and nothing coded.

The claim files keep words, not categories. `board_demographics.csv` has
`race_words` and `gender_words` (the pronoun, honorific or description as
the source prints it), and `board_party.csv` has `party_words`; the tables
that say what each means are `RACE_WORDS`, `GENDER_WORDS` and `PARTY_WORDS`
in `code/clean/board_members.py`, where a word not listed stops the build.
`board_terms.csv` keeps the election date the county prints; the January
start, the missing end and the election as how the seat was gained are
`code/clean/board_roster_results.py`'s. A press or obituary age is keyed the
same way: `board_demographics.csv` has
`age` and `age_date` (as printed: "25 April 2019", "1960"), and
`birth_year` only where a source prints a birth date or year. The transcriber
never subtracts. `code/clean/board_members.py` takes the year of the date
less the age, refuses an age with no year in its date, and refuses a row that
gives both a birth year and an age.

Three records read on 25 September 2026 are filed and cited but kept out of
the table, since each gives a birth year that disagrees with the member's
other record and the build stops on two sources disagreeing: W. N. Febrey's
1900 and 1920 records (`census1900febrey`, `census1920febrey`, one
household, born 1851 or 1854, against the 1910 record's 1859, a second
William N. Febrey household) and William Duncan's 1910 record
(`census1910duncanwilliam`, 1857 against the 1900 record's August 1854).
Which household is Febrey and which year is Duncan's are open
(`febrey-birth-year`, `duncan-birth-year`); the rows are added when it is
settled. For the members seated 1870–1911 the 1880, 1900 and 1910
sheets name a magisterial district at the head of each page and, outside
the towns, leave the street column blank, so the district is the place
recorded, in the sheet's own words.

Only the census record itself goes in this table. What a newspaper, an
obituary or a secondary source says, Hjerpe's reading of an 1880 record
included, is a separate claim and stays in `board_demographics.csv` or
`board_residence.csv`. `code/transcribe/board_census.py` moves any row that
cites a census record out of those two files and into the table, merging
it with the record's row where there is one, and stops where the two
disagree. A new record is keyed into the table directly, and the build
refuses a row citing a census record in either claim file, so the script
is run when it does.

### Reading an image

**Nothing leaves an image on one reading.** A census record is read against
its own enumeration sheet before any of its fields is used, and its `checked`
column says what the sheet gives. Ancestry's index is a finding aid, the same
standing as the OCR under `data/transcribed/by_ocr/`: it locates the line, it
does not read it. That is a second reading of every record, not a sample,
because there are only 72 of them and the cost of a wrong one is silent.

`code/build/board_claims.py` enforces the half of that rule a machine can
check. A row whose `checked` names neither the sheet nor the index stops the
build, and so does a `place` on a row the sheet was never read against, since
a street is the field the index gets wrong. `code/tests.py` reintroduces both
mistakes.

For a page read through OCR — a newspaper claim in
`board_residence.csv` — the quoted sentence is read off the page image before
the row is written, and any house number in it is read off the image, never
off the OCR. Where rows were entered before this rule, the backlog is cleared
a page at a time, whole pages rather than a sample of rows, since opening the
page is the cost and the rows on it are then free.

A pass over the rows that predate the rule, on 25 September 2026, read the
seven census records that had only ever been indexed, and two newspaper pages
carrying seven of the quoted addresses. It found one wrong value: Detwiler's
1940 sheet gives his birthplace as **Minnesota** where the index reads
Wisconsin, and spells the surname Detwiler, as the Board member does, where
the index reads Detweiler. Birthplace is not a column the build reads, so no
figure moved. Three smaller disagreements stand unresolved or need no fix:
the sheet's own number reads 63A or 67A where the index and the filed image's
name say 62A, and neither reading is firm; the index's street name for
Buchholz, `1`, is a column number and not a street; and Byrne's sheet gives
202 N. Highland St., which the *Daily Sun* of 11 September 1952 prints as
well. The 103 figures keyed from the 1870, 1880 and 1890 volumes and the
whole of the POP-TWPS0076 Arlington block were re-read against the printed
pages and every one agreed.

**Tillema and Massey.** Both have a census row and a *Daily Sun* row of 11
September 1952 that name different streets, and the 1952 page prints exactly
what the rows quote — the disagreement is between the two sources, not in the
transcription. Tillema's 1950 sheet reads **N. Harvard St.**, and Arlington
has a North Harvard Street and no North Howard Street, so the Sun's "1903
North Howard Street" is its misprint. Massey's sheet reads **23rd Rd**, where
the Sun prints "4300 North 23rd Street"; North 23rd Road and North 23rd
Street are both real and both in North Arlington, so this is a different
house, not a different side. Neither changes what the build does: it carries
every claim with its source and chooses none.

## Race, gender and birth year of Board members

Birth years come from the same files as race and gender, one row per
source, and reach `board_members.csv` as `birth_year` with a source and a
note; with no source the year is blank and `unsourced`, since no standing
assumption stands in. A census listing gives an age, and the year is the
census year less the age, so it is right to within a year, except where
the index prints a birth date; an obituary or a profile gives a birth
date, or an age on a date, and the row's basis says which. For members
seated 1960 on the sources are obituaries on legacy.com,
Dignity Memorial and InsideNoVa, candidate profiles in the Connection,
ARLnow and Patch, a Senate of Virginia member page, and the Post's archive
where it shows the paragraph that carries the age. The build refuses a year
that would seat a member under 18 or over 100, and two sources disagreeing
stop it. `election_year` on each elected term is the election that seated
it, a January start following a November election, so a figure can
subtract without re-deriving that rule.

Race and gender come from `data/transcribed/by_claude/board_demographics.csv`,
one row per claim a source makes about a member, in the source's own words
with a citation to the page the document prints, and from the census records
above; and otherwise from a default,
a white man, labelled `assumed`. Each cell of `board_members.csv` says which, and
`gender_evidence` says how a gender is known: `record` (a census listing),
`press` (the pronoun or honorific a paper uses for the member; each such row
of the claim file quotes the sentence and cites the page), both joined with
`; `, or `none` where the default stands. Two sources disagreeing about a person stops the build, and an attributed name
that matches no roster name stops it too, so a near-miss cannot fall silently
into the default. The default is a claim, and this is what stands behind it in
each period:

| Period | Race | Gender |
|---|---|---|
| 1870–1888 | Five Black members named by Hjerpe (2021): Rowe, Syphax, Pinn, Pendleton, Allen. Pinn, Pendleton and Allen each rest on a reproduced 1880 census image; Rowe and Allen on narrative statements in her paper; Syphax on O'Leary, who writes that his photograph shows he was African American. The sentence naming the five as a group sits in her own list of open inquiries, and the file records it as such. O'Leary adds that "a majority of the early office holders" were probably African-American but cannot name them. Nobody on our side has checked the census linking. | Names in O'Leary, but seven members before 1912 appear by initials only (`gender-1870-1912`). |
| 1889–1930 | One collective sentence: the board "became and remained all white for the duration of this system" (Hjerpe 2021, p.4), sourced to the county's election records. No per-person evidence. | Names in O'Leary; initials only before 1912. No source names a first woman member, so "all men before Magruder (1932)" is assumed. |
| 1931–1986 | Nothing per-person from any source. The default rests on Newman (1987) being described as the first Black member since Reconstruction. About 280 person-years. **The weakest stretch.** | Census listing or a press honorific or pronoun for all but B. M. Smith (1933). |
| 1987–present | Per-person: Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), and Tejada as the first Latino member (Hjerpe 2021). The Arlington Historical Society's Newman entry names Newman, Monroe and Dorsey as African American members, and its Center for Local History entry gives Tejada's Latin American heritage; Monroe also rests on the Arlington NAACP president's words at his death, and Dorsey on his own statement (2020). | A press pronoun or honorific for every member. |

None of the three roster sources states anyone's race or gender. Race comes
from Hjerpe and O'Leary; gender comes from a census listing or from the
pronoun or honorific a paper uses for the member, and where neither has been
found the default stands, labelled `assumed`. The
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

## Other localities

`board_peers.csv` sets Arlington's Board beside the governing body of every
Virginia independent city and of fourteen counties: the thirteen largest
other than Arlington, and Rockingham. The figures show those of 100,000
residents or more, eighteen in all, and leave the choice of peer to the
reader: places Arlington's size in `board_peers_residents`, places as dense
in `board_peers_density`.

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
