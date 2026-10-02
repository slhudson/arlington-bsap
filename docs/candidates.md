# Candidates

This write-up covers who ran for the Board and which of them a source says was
Black: what each number in `data/clean/candidates.csv` is, what backs it, and
what is assumed where nothing does. How a decision was reached is in the git
history rather than here. `code/citekeys.py` explains the placeholders in the
`source` columns, and `docs/questions.csv` holds what is still open.

## The question this subject exists to answer

This subject exists to establish whether a Black candidate ran and lost, or did
not run at all, in each period the report covers. A "no ring" year on the
`candidates` figure means one of two very different things: nobody ran, or
somebody ran and the record of it has not been checked. Telling those apart is
the whole point. Coverage runs era by era:

- **1871–1887**: thirteen wins by five members, and one loss the Gazette
  names: W. A. Rowe, who won Arlington District in 1879 and 1881, was the
  "regular republican nominee" beaten in 1885 by a "citizens' candidate"
  (`alexandriagazette18850529p3`, read on the page image), and Dr. Tucker, whose
  race is not known, the "regular republican candidate" beaten in Jefferson
  District the same day. O'Leary names only winners, so the other losses are
  the Gazette's to supply, and it supplies few: the 1870s returns come
  township by township, and the weeks after the 1871, 1877 and 1883 elections
  return no issue from Chronicling America. Open.
- **1888–1930**: the Gazette's returns for 1891 to 1901 and 1919 name those who
  lost a supervisor's race (Rowe and Tucker, above, lost in 1885); 1889 and
  1903 give winners only, and 1911's table of names by district is of county
  offices and holds no contest for supervisor. Two things in them bear on the claim that no Black candidate
  ran in these years. The Gazette calls the Washington District supervisor of
  1889 "W. Wilson (colored)" and of 1891 "Wilson, colored"
  (`alexandriagazette18890525p3`, `alexandriagazette18910529p3`, both read on
  the page image). O'Leary's Walter G. Willson held that district in the same
  years and is carried as White on the default (`docs/members.md`, "What rests
  on an assumption"), so a Black supervisor of 1889–93 may be missing from the
  table below. And no one the Gazette names as a loser is marked "(colored)",
  which does not clear them, because it does not mark Rowe, who is Black, in
  1885: those who sat on the Board are carried in `members.csv`, Rowe among
  them; five of the rest are White by the 1900 and 1920 censuses and ten have no
  matching record ("1870–1919, the Alexandria Gazette's returns", below;
  `candidate-analysis`).
- **1931**: answered. A complete candidate list survives; three Black
  candidates ran, all lost.
- **1932–1986**: the claim at stake is two historians' sentences, not a
  check of the list (`candidate-analysis`). 1932–1950
  is race-matched against the census, and that check finds no Black
  candidacy: the one index reading that would have been an exception is the
  index's own error, which the sheet corrects ("1932-1950, race-matched
  against the census," below). 1951–1986 is read for the press: the Sun on
  Virginia Chronicle for 1951 to 1978, the first 25 pages of each year's
  search, and the 1950 census for the candidates of 1950 to 1956, and nothing
  read names a Black candidate; the press says nothing of any candidate's race
  ("1950-2025, press and the 1950 census," below).
- **1987–2025**: the four Black members' own runs are tracked in full. Of the
  other candidates who lost, the press states a race for two (Dromgoole,
  Latino; Fierro, Hispanic) and is silent on the rest.

## Who the general-election list leaves out

The county's candidate history and the state's database print who stood at a
general or special election. They cannot print someone who lost a nomination
and never reached the ballot, and a party's nomination contest, where the party holds one, is a stage
the candidate list never sees.

**How a candidate reached the ballot.** Virginia law gives the method of a
party's nomination for a county office to the party's own county authorities
(`vacode24`, section 24.2-509), so the method is the local party's, and it
changes.

- *To 1902.* A party names a "regular" nominee, and a "citizens'" or
  independent candidate stands against it (`alexandriagazette18850529p3`);
  the Republicans meet in conventions, one in August 1881 at Alexandria's
  Colored Odd Fellows' Hall to choose delegates to the state convention
  (`alexandriagazette1881split`). No report read names who lost a nomination.
- *1902–1930.* The Board's elections move to November from 1903. The state
  holds its first primary, a senatorial one, in 1905, and a law of 1912 codifies
  the primary and lets the party restrict it to whites
  (`encyclopediavirginia2020democraticparty`). What an Arlington party did for
  the Board in these years is not in a source held.
- *1931.* Fifty-one candidates file for the first at-large election, and the
  papers label one of them with a party ("The 1931 election was non-partisan",
  `docs/members.md`, "Party").
- *1932–1950.* The county's history prints a Democratic primary in 1939 under
  "Running Before Primary" (`arlingtonelections2021`, p. 11) and a Democratic
  primary in 1952; the Daily Sun reports six candidates seeking a Town
  Meeting's "nonpartisan" nomination for three Board vacancies in September
  1952, the seats left by a ruling that federal employees cannot hold county
  office (`tds19520924p1`).
- *1953–1990.* Arlingtonians for a Better County names its candidate at a
  nominating convention at which a candidate may be nominated from the floor on
  25 signatures: three filed in 1961, a fourth by petition, and Lowry was named
  (`nvs19610529p1`, `nvs19610531p1`); Wadlow had lost the same nomination in
  1960. The county prints "(Convention)" only for the two ABC nominees of
  1955. Democrats and Republicans nominate by a method the sources read here do
  not name.
- *1993–2017.* The Democratic committee runs its own contest, a primary in
  March 1993 with four candidates (`washingtonpost1993cliffhanger`, whose
  first two paragraphs are all that could be read) and, by 2012, a caucus, with
  instant-runoff counting in 2017 (`arlnow2012garvey`, `arlnow2014howze`,
  `insidenova2017gutshall`).
- *2018 on.* In January 2018 the committee votes unanimously to use a primary
  (`arlnow2018primary`); in 2020 a special election's nominee is chosen by a
  vote of the party's committees (`arlnow2020karantonis`); the state's own
  ranked-choice primaries follow in 2023 and 2024.

**What record of the losers there is.**

| Years | General election | Nomination stage |
|---|---|---|
| 1870–1930 | O'Leary, winners; the Gazette, returns that name losers in some years | convention; no record held |
| 1931 | the county's list of 51 (`anderson1958`) | none |
| 1932–1950 | the county's history; the Sun (1935–51) and the Evening Star | the Sun for the Democratic primary and Town Meeting |
| 1951–1978 | the county's history; the Daily Sun and Northern Virginia Sun | the same papers report ABC's conventions (1960 and 1961 read), and the Star to 1963 |
| 1979–2000 | the county's history; the Post's archive, paywalled | the Post; nothing online from the Sun Gazette |
| 2001–2025 | the county's history to 2021, the state's database from 2007; ARLnow, InsideNova, the Connection | the press, caucus by caucus; the state's database from 2007 for primaries it runs |

**How many the list misses.** The sources cannot say, and the number is not
small. The nomination contests read for this write-up hold candidacies that
never reached a general ballot: Meijer at the Town Meeting of 1952; Wadlow in 1960; Wadlow, Hutchins and Hackman in 1961; three
losers of the Democratic primary of 1993, whom the part of the report that
could be read does not name; Bondi, Sims, Klingler and Fallon in 2012; Thomas
and Fallon in 2014; Klingler, Patil and Fallon in 2017; Kanninen, Choun and
Merlene in 2020 (`candidates_press.csv`). Those contests are a handful of
the nomination contests since 1932: ABC named a candidate at
a convention in 1955, 1960 and 1961 at least. The misses are therefore many more
than these, and cannot be counted without reading each contest's report.

**Whether the later phases are worth doing.**

- *1870–1915.* Yes, and begun: the Gazette names losers in the years above, and
  it has already changed what is known of 1885 and 1889–91. What remains is the
  1870s and 1881 townships and a check of Willson's race against a census record.
- *1916–1930.* No. Chronicling America's Gazette runs to 1921, so 1919 is
  read and 1923 and 1927 are not; the county's candidate history for those
  years, not the Gazette, is the route, and it names winners.
- *1932–1950.* Done for the general election. A nomination-stage search of the
  Sun is worth doing only if a Black candidate for the nomination is suspected,
  and nothing suggests one.
- *1951–1986.* For race, no: the Sun pages read name no Black candidate and state no
  candidate's race, so a longer search of the same papers would find a Black
  candidate only if the paper happened to describe one as such. For gender, only if the
  candidate analysis is taken up: an honorific or the census gives a
  gender for some of the people in these years who never sat on the Board,
  and the ABC conventions would add the filers who never reached a ballot.
- *1987–2025.* Enough for race. The gap is 1987–2000, where the Post's archive
  is behind a library login that was not available.

## What rests on an assumption

- A Black candidate who lost is recorded only in 1931 and, after 1987, only
  for the four Black members: before 1931 the Gazette's returns name some
  losers and mark none "(colored)" (`candidate-analysis`), and the people
  with a losing candidacy from 1932 through 2025 are coded for race and gender
  in part, from the Board's record, the census and the press, with no Black
  candidate among them but the members Monroe and Spain, whose losses the
  figure already draws (`candidate-analysis`), so "none ran 1932-1986" rests
  on two authors' sentences and on this check, and not on a candidate list.
- Who lost a nomination is not in any list held, so a Black candidate who
  sought a nomination and lost cannot be excluded for any year.

Those rows are in `docs/questions.csv`, with whose court each waits in and what
would settle it.

---

## Black candidacies

`data/clean/candidates.csv` holds one row per candidacy a source says
was a Black candidate's for the Board, joined to the election it was in, and
one row per period in which a source says no Black candidate ran. The claims
are keyed in `data/transcribed/by_claude/candidates.csv`, one row per
source, in the source's words, with the name as the election record prints
it; a race is never read off a name or a neighborhood. A candidacy is matched
on surname, year and kind of election (regular, special or primary): before
1931 to the term the roster holds for that election, in 1931 to the county's
contest and its list of candidates, and from 1932 to the county's candidate
history through 2021 and the state's database after. Each row carries the
seats, the candidate's votes, the fewest votes that won a seat, whether the
candidate won (for a primary, the nomination) and the party the record
prints. A candidacy that matches no election stops the build, and so do a
Black member's election with no candidacy, a candidacy inside a period a
source says none ran, and a name the 1931 list marks "(Col)" with no
candidacy.

**1871–1887.** Every candidacy won, by the five members Hjerpe
highlights in her Table 1 (`hjerpe2021` p.2): Jefferson District elects a
Black member at every election but 1885's, and
Syphax (1872) and Rowe (1879, 1881) win Arlington District. Hjerpe's table
sets some names against the wrong years, so the year and district of each
are O'Leary's. His record names each district's winner and, before 1907,
nobody who lost, so a loss by a Black candidate cannot appear in it; the
Gazette names one, Rowe's in Arlington District in 1885 ("1870-1919, the
Alexandria Gazette's returns", below), which this table does not hold.

**1888–1930.** Allen resigns in 1888 (`docs/members.md`, "Residence in the
district").
Hjerpe writes that "no black candidates were recorded as running for the
county board again until after 1930" (p.3), on the same record of winners.
Bestebreurtje (`bestebreurtje2017` p.215) has Black candidates running in
1931 "for the first time since 1903", and names no 1903 candidate or office.
The two agree that none ran from 1904 and differ at most on 1889–1903. The
Alexandria Gazette's returns name losers in these years and a "colored"
Washington District supervisor in 1889 and 1891 ("1870-1919", below); the
1903 Bestebreurtje names has no candidate behind it there
(`candidate-analysis`).

**1931.** The county's list of the 51 candidates for the first at-large
election, 3 November 1931, which its candidate history points to rather
than prints and Anderson reprints (`anderson1958` p.67), marks three
"(Col)": Mrs. Mary B. Harris of Nauck Station, Dr. E. T. Morton and C. H.
Moseley of Halls Hill. It is keyed in full in
`data/transcribed/by_claude/arlington_historical_magazine/anderson_candidates_1931.csv`.
None of the five elected is marked. The county prints the top six with their
votes and "others not mentioned": the fifth seat went to Kelly with 1,456
and McShea ran sixth with 1,177, so each of the three had fewer than 1,177.
Bestebreurtje names the same three, spelling Moseley "Mosley". George
Vollin, Jr. of Queen City ran for sheriff and lost (Bestebreurtje p.215;
Pratt p.22); a sheriff's race is not a Board candidacy and is not in the
table. Pratt's four are the three and Vollin, and ARLnow's "four for the
Board" (Lyon's Legacy V) is the count that is off. Hjerpe dates the four to 1930,
the year of the referendum, citing Bestebreurtje p.215, which says November
1931, and the county's list is of the 1931 ballot.

**1932–1986.** No Black candidate for the Board, as two sources state it.
Pratt: after 1931 "only one other Black candidate ever bothered to file for
office" until Newman, and his note 7 names him, Arthur W. Walls, defeated for
the House of Delegates in 1969 (`pratt1995` pp.22–23, 35). Bestebreurtje:
"It would be fifty years before another African American candidate ran for
office in Arlington" (pp.217–218). The county's history names every
candidate in these years and gives no race, so the negative is the two
sources'. For why, Pratt reports the 1974 testimony of Vollin and Harrison
Douglas: that after 1931 Black Arlingtonians thought running at large an
exercise in futility.

**1987 on.** The candidacies of the four Black members, from the county's
and the state's records. Newman wins in 1987 and 1991. Monroe loses the April
1999 special election, the one-seat contest, to Lane by 169 votes and wins
the two-seat general that November ("Race, gender and birth year of Board
members", above). Dorsey wins the June 2015 primary and the generals of 2015
and 2019. Spain loses the Democratic primary of June 2023 and wins the
primary and the general of 2024; both primaries were ranked-choice, the
state's file carries first choices and flags more winners than seats, so the
outcome of each is the press's (`arlnow2023coffeyprimary`,
`arlnow2024spain`). Dorsey also sought the Democratic nomination in 2002,
at a party caucus rather than on a public ballot (`connection2002`), so it
is not a candidacy here. The county's and the state's records hold the
candidacies for the Board from 1932 through 2025, most of them losing (a
County Board candidacy is one row of `elections.contests()`, one page
collapsed into another where the county's history prints it twice -
`elections._dedup_board_pages()`; a candidate's outcome where the state's
own record does not say, in a ranked-choice contest, is the top-`seats` by
first choice, for the contests where no source has settled it). Counting
person rows from the county's history through 2021 and the state's database
after, with the outcome `code/clean/candidates.py` computes, does not
reproduce the 271 above, so the coding below is of the people those rows name,
not of that count. The years from 1987 hold every run by a Black member and
nobody else's (`candidate-analysis`; "1950-2025, press and the 1950
census", below). The check cannot reach the nomination stage: a candidate who
lost a party contest never appeared on the general ballot ("Who the
general-election list leaves out", above).

**1932-1950, race-matched against the census.** Of the losing candidacies
in this span, the people have been checked against the
1930-1950 census on Ancestry, each row logged in
`data/transcribed/by_claude/candidates_census.csv` in the shape of
`members_census.csv`, whether found or not. Some also
served on the Board and already had a census record in
`members_census.csv`; that record is reused here rather than re-searched.
The others are newly matched, each tied by `unique` - the only person of
that name in Arlington in the census year searched - since no second source
was in hand to try `occupation`, `household` or `address`. Some were
searched and not found under the name the election record gives.

One of the new matches, **William C. Ayres**, who lost County Board
races in 1941 and 1943, is the one that would be a Black losing candidacy
inside the 1932-1986 span the two sources' sentence covers, and only on the
index: Ancestry transcribes his 1940 census as Negro (Black) where the sheet
reads W (White) for Ayres, his wife and his mother-in-law alike, and
Ancestry's own index carries White as an unfollowed bracketed alternate. The
index is wrong, `census1940ayres` records White, and none
of the new matches is a Black candidacy.

Two oddities in the county's own history bear on this slice. Five names the
county's history prints only in a narrative block dated 1935, with no
matching results-table row, are the same four people as four already-served
members (Magruder, B. M. Smith, Lyman Kelley and Edmund Campbell) plus one
non-candidacy (an appointment, "Judge McCarthy appointed" - not a person
running, and not a row in `candidates_census.csv`); this confirms the
mistagging is real rather than five new candidates. And the likely OCR
duplicate "Dr. Victor Myers" / "Dr. Victoria Meyers" (1939) could not be
resolved either way: neither spelling turns up an Arlington match in the
1940 census index.

The source citekeys for the new matches (`census1940windridge`,
`census1940ayres`, `census1940carretta`, `census1950divine`,
`census1950gaines`, `census1950wimberly`, `census1950smith`,
`census1950clair`, `census1950potter`, `census1950bach`,
`census1940gordon`, `census1940donaldson`) are entries in
`paper/sources.bib`, each filed in Drive with its sheet image
(`code/sources/ancestry.py`, which takes a `--file` naming a census-shaped table
other than `members_census.csv`). Only `census1940ayres`'s sheet has been read for
verification; the others carry the index's transcription unread
against the image, the same open state `census-match-quality` describes for
`members_census.csv`. A clean-stage script to read this table into a figure
is still unwritten.

**1870–1919, the Alexandria Gazette's returns.** `data/transcribed/by_claude/candidates_gazette.csv`
holds what the Gazette prints of each Board election it reports with losers named,
one row per candidate: the district, the votes and outcome as printed, a race word
where the paper puts one beside the name, the page, and the sentence. It covers
1885, 1889, 1891, 1893, 1895, 1897, 1899, 1901 and 1919; 1887, 1889 and 1903 print
winners only, and so does the 1881 report, which names Rowe, Pinn and Costello.
O'Leary prints the losers of 1907 and 1915 and the Gazette agrees with him,
so they are not repeated; the table of names by district that the Gazette of 8
November 1911 prints (`alexandriagazette19111108p2`, read on the page image) is of
the county offices voted for on 7 November, clerk, commonwealth's attorney, sheriff
and commissioner of revenue, and the issues of 8 to 11 November print no contest
for supervisor; 1919 is an election
O'Leary does not list at all. 1871, 1877 and 1883 return no issue for the weeks
after them. The Gazette's issues after 1921 are not on Chronicling America.

Four things in it are findings.

- **Rowe lost in 1885.** William A. Rowe, who won Arlington District in 1879 and
  1881, was "the regular republican nominee" beaten by George W. Veitch, "the
  citizens' candidate"; in Jefferson District Richard W. Johnston beat "Dr.
  Tucker, the regular republican candidate"
  (`alexandriagazette18850529p3`). Rowe is Black on Hjerpe's
  word, so a Black candidate lost in 1885, which the Black-candidacies table
  below does not hold because its build can place only a candidacy that won
  before 1931. Tucker's race is not known.
- **"Wilson (colored)", 1889 and 1891.** The Gazette's list of the officers elected on
  23 May 1889 reads "Washington District--W. Wilson (colored), Supervisor"
  (`alexandriagazette18890525p3`), the day after a telegraphed note that
  Alexandria County elected "F. S. Corbett and [blank] Green, (colored)" supervisors,
  a name that differs. On 29 May 1891 "In Washington district, Wilson, colored,
  beat Mr. Phillips, present incumbent, for supervisor, by 36 majority"
  (`alexandriagazette18910529p3`). O'Leary has Walter G. Willson for the district in
  1889 and 1891 and names no Phillips in 1891; `docs/members.md` carries him as
  White on the default (the row `willson-race` in `docs/questions.csv`).
- **Who lost, 1893–1901.** 1893: Birch (130) to Clarke (172) in Arlington; J.
  Costello (52) and G. W. Donaldson (19) to R. H. Phillips (151) in Washington.
  1895: Birch, Hayes (101) and Clark (41) to Corbett (158) in Arlington; Palmer to
  Grunwell in Washington; Hume (119) to William Duncan (162) in Jefferson, in a report
  that says "a large majority of the voters colored, especially in Jefferson
  district". 1897: a tie between Corbett and Torreyson in Arlington, drawn for
  Torreyson. 1899: Birch, Werks and Hines to Corbett (209); Harrison and Donaldson
  to Saegmuller; Graham (138) to Rust (233). 1901: Corbett (74) to Darby (400) in
  Arlington; Saegmuller (110) to Costello (132); Rust (180) to Duncan (281): "All of
  the present Supervisors were defeated."
- **1919.** C. N. Ahalt (241) beat W. H. Payne (204) in Washington; Thomas J. DeLashmutt
  (411) beat F. C. Hall (191), J. R. Robinson (110) and Richard E. Babcock (34) in
  Arlington; Edward Duncan (169) beat Jacob Corl (133), K. Roberts (12) and Charles A. Travers
  in Jefferson.

None of these figures is read against the page image except the three passages above, and the OCR
misreads digits: a figure the report's own arithmetic contradicts (1899, Washington) says so in
the row's note. Of those who lost, Rowe, Phillips, Birch, Clark, Hume, Corbett, Saegmuller, Rust and Costello sat on
the Board and are carried in `members.csv`. Of the other fifteen, five are matched to a
census sheet by the initials or name and the district they stood in, and each is a White man: G. W.
Donaldson (1893, Washington), a carpenter in 1900 (`census1900donaldson`); Richard E. Babcock, a
patent attorney in Arlington (`census1920babcock`), W. H. Payne, a carpenter in Washington
(`census1920payne`), Jacob Corl, a railroad engineer in Jefferson (`census1920corl`) and Charles A.
Travers, a railroad engineer in Jefferson (`census1920travers`), all of 1919 and read in the 1920
census. The other ten, Tucker, Hayes, Palmer, Harrison, Werks, Hines, Graham, F. C. Hall, J. R.
Robinson and K. Roberts, have no record that agrees with the name and the district
(`candidates_census.csv` says what each search found); a name no household bears is not a
Black candidate, and the sheets say nothing of the ten. 1903's winners are Rust, Douglass and Febrey, and the Gazette marks no candidate for the office
"colored" in that year or in 1907, so Bestebreurtje's "for the first time since 1903" (p. 215), whose
sentence carries no note, has no candidate behind it in the Gazette; the one 1903 election he
names elsewhere is the Good Citizen League's nomination of Crandal Mackey for Commonwealth's
Attorney (p. 143).

**1950-2025, press and the 1950 census.** `data/transcribed/by_claude/candidates_press.csv` holds one row
per candidate whom a press source says something about, and a row with `source` `unsourced` and the search
for each the press search found nothing on. Gender is taken from a title, an honorific or a pronoun the
source uses of the person and race from a word the source or the person uses; neither is taken from a
name, a photograph or a place. 1951–1978 is read from the Daily Sun and the Northern Virginia Sun on
Virginia Chronicle, the first 25 pages of the search for "County Board candidate" in April to November of
each year; 1979–1986 is not read, because the Sun on Virginia Chronicle ends in 1978. 1987–2025 is read
from ARLnow, InsideNova, Metro Weekly, Patch, the Connection and the campaigns' own pages. The press
states a race for two candidates, Dromgoole (Latino) and Fierro (Hispanic, in his own words); no Black
candidate is named in these years. A search of the same Sun pages for "Negro", "colored" or "Black" beside "candidate" was read for 1958 to 1963 and names no Arlington candidate; its hits for the other years were not read.
Of the people with a losing candidacy from 1932 through 2025, those who sat on the Board have the race and
gender `members.csv` carries, others are matched to the 1930–1950 census or have a press source, most of
the rest were searched and nothing found, and three, Henry P. Ames, Allen H. Harrison and Charles W.
Rinker, were not reached. Of those with a gender, the women are Elsie L.
Gordon (1939), Elizabeth B. Magruder (1935), Florence Cannon (1947), Leone B. Buchholz (1952), Martha
Gammon (1952), Irene C. Rock (1963), Dorothy Grotos (1974), Barbara Favola (1995), Audrey Clement (2011),
Susan Cunningham (2020), Natalie Roy (2023), Madison Granger (2024) and Tenley Peterson (2024); the
rest are men. Two women who sought a nomination and lost it, Yvonne Hutchins and Mary Cook Hackman (ABC, 1961),
are rows in the press file and not in these counts, which are of the general-election list. The
1950 index matches Cooper, Booker, DeMik and Kimel, all White men, on the name alone or the name and an
occupation; Rowzee, Wright, Bayless, Parli, Bell and Pomponio carry two or more records under the name, or
a different spelling, and are left unmatched; Pearson, Bechtel, Gammon, Leggett and Tuthill have none in
Arlington. Cooper and Kimel are the Board members whose 1950 records `members_census.csv` already
files; Booker (`census1950booker`) and DeMik (`census1950demik`) are filed with their sheets. Whether the report analyzes
candidates at all, women among them, is Sally's to decide (`candidate-analysis`); these are its data.

**The figure.** `candidates` draws each candidacy in a regular or
special election as a dot at its year, filled if won and a ring if lost,
with runs in the same year stacked; primaries are in the table and not
drawn. It shows a win at every Jefferson election but 1885's from 1871 to
1887; nothing from 1888 to 1930; three losses at the first at-large election
in 1931; nothing from 1932 to 1986; and from 1987 wins, the one loss
being Monroe's in the one-seat special. Where a year is empty the sources
say different things, and this section says which: from 1932 to 1986 two
sources state that no Black candidate ran; before 1931 and after 1987 the
records cannot show a loss by anyone but a member.
