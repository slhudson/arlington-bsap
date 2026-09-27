# Candidates

Who ran for the Board and which of them a source says was Black: what each
number in `data/clean/candidates.csv` is, what backs it, what is assumed
where nothing does, and why. Present tense; how a decision was reached is in
the git history. The placeholders in the `source` columns are explained in
`code/citekeys.py`, and what is still open is in `docs/questions.csv`.

## The question this subject exists to answer

Whether a Black candidate ran and lost, or did not run at all, in each
period the report covers. A "no ring" year on the `candidates` figure means
one of two very different things — nobody ran, or somebody ran and the
record of it hasn't been checked — and telling them apart is the whole
point of this subject. Coverage, era by era (27 September 2026):

- **1871–1887**: answered, and closed for good. O'Leary's record names only
  winners before 1907, so a loss cannot appear in it; the absence is the
  record's limit, not a finding.
- **1888–1930**: fully open. No candidate list exists for these 42 years at
  all; nobody has searched the Alexandria Gazette's returns yet
  (`black-losers-1870-1930`).
- **1931**: answered. A complete candidate list survives; three Black
  candidates ran, all lost.
- **1932–1986**: the claim at stake is two historians' sentences, not a
  check of the list (`black-losers-1932-on`). 1932–1950 (19 of the 55 years)
  is now race-matched against the census, and it found one likely
  exception, pending a second check against the sheet ("1932-1950,
  race-matched against the census," below). **1950–1986, 36 years, is
  entirely unstarted.**
- **1987–2025**: the four Black members' own runs are tracked in full.
  Whether any *other* candidate in these 38 years was Black has not been
  checked either — `black-losers-1932-on` runs through 2025, not just to
  1986, and this stretch is as open as 1950–1986 is.

The 1888–1930 gap and the 1950–2025 gap are each larger than what has been
checked so far; a full answer is not close. Each era above is free to
become its own thread — the census-matching approach used for 1932–1950
does not extend past 1950 (contemporaneous newspaper profiles take over;
`black-losers-1932-on` says which), and 1888–1930 is a different kind of
search (the Gazette's returns) from either.

## What rests on an assumption

- A Black candidate who lost is recorded only in 1931 and, after 1987, only
  for the four Black members: before 1931 the election record names winners
  (`black-losers-1870-1930`), and 271 losing candidacies from 1932 through
  2025 have not been matched to a census record or a press description for
  race (`black-losers-1932-on`), so "none ran 1932-1986" is two authors'
  sentences, not a check of the list.
Each is a row in `docs/questions.csv`, with an owner and what would settle it.

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
candidacy. The table holds 26 candidacies by twelve people.

**1871–1887.** Thirteen candidacies, all won, by the five members Hjerpe
highlights in her Table 1 (`hjerpe2021` p.2): Jefferson District elects a
Black member at ten of its eleven elections, every one but 1885's, and
Syphax (1872) and Rowe (1879, 1881) win Arlington District. Hjerpe's table
sets some names against the wrong years, so the year and district of each
are O'Leary's. His record names each district's winner and, before 1907,
nobody who lost, so no loss by a Black candidate can appear in these years:
the absence is the record's, not a finding.

**1888–1930.** Allen resigns in 1888 ("Residence in the district", above).
Hjerpe writes that "no black candidates were recorded as running for the
county board again until after 1930" (p.3), on the same record of winners.
Bestebreurtje (`bestebreurtje2017` p.215) has Black candidates running in
1931 "for the first time since 1903", and names no 1903 candidate or office.
The two agree that none ran from 1904 and differ at most on 1889–1903; the
Alexandria Gazette's returns would settle both (`black-losers-1870-1930`).

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

**1987 on.** Ten candidacies by the four Black members, from the county's
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
is not a candidacy here. The county's and the state's records hold 436
candidacies for the Board from 1932 through 2025, 271 of them losing (a
County Board candidacy is one row of `elections.contests()`, one page
collapsed into another where the county's history prints it twice -
`elections._dedup_board_pages()`; a candidate's outcome where the state's
own record does not say, in a ranked-choice contest, is the top-`seats` by
first choice, for eighteen contests where no source has settled it). None of
the 271 has been matched to a census record or a press description for
race, so 1932-1986 rests on Pratt's and Bestebreurtje's sentence that none
ran, and the years from 1987 hold every run by a Black member and nobody
else's (`black-losers-1932-on`). The check is bounded: the 1930-1950
censuses for the early candidates, and candidate profiles for the rest. It
cannot reach the nomination stage, though: a candidate who lost a
Democratic primary never appeared on the general ballot, and the county's
list records primaries only patchily from 1950, the state's fully from
2007, and a caucus or convention nomination never.

**The figure.** `candidates` draws each candidacy in a regular or
special election as a dot at its year, filled if won and a ring if lost,
with runs in the same year stacked; primaries are in the table and not
drawn. It shows a win at every Jefferson election but one from 1871 to
1887; nothing from 1888 to 1930; three losses at the first at-large election
in 1931; nothing for the next 55 years; and from 1987 wins, the one loss
being Monroe's in the one-seat special. Where a year is empty the sources
say different things, and this section says which: from 1932 to 1986 two
sources state that no Black candidate ran; before 1931 and after 1987 the
records cannot show a loss by anyone but a member.
