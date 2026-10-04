# The 2025 post-election survey of voters

SurveyUSA interviewed 584 Arlington voters between 6 and 13 November 2025,
after the first County Board general election run by ranked choice voting,
and FairVote, the Ranked Choice Voting Resource Center and Ranked Choice
Virginia reported the results to the County Board in February 2026
(`rcva2026evaluation`). This project reads one table from it:
`data/raw/rcva/survey_rcv_by_group.csv`, thirty-three rows giving support for
ranked choice voting, awareness that it would be used, and understanding of
how ballots are counted, each cut by the respondents' gender, age, race and
ethnicity, education, homeownership, contact method and how they voted.

## Why a table and not the respondents

The respondent file is not in this repository and will not be. Four hundred
and seventy-seven of its 585 rows are unique on zip code, exact age, gender,
education and homeownership taken together, and it also carries interview
timestamps to the minute, free-text comments running past a thousand
characters, and a record number keying each respondent to a recording of
their voice. This repository is meant to go public.

The table is therefore a source rather than something this project derives.
It was prepared by the survey's own researchers in a private repository of
their own, which holds the respondent file, the code that tabulates it and a
replication of every number the February report printed; `rcva2026subgroups`
names it.
`data/raw/` is where a file arrives from outside already made, and this one
does: the fact that one researcher worked on both studies is a fact about
staffing, not a path between them.

## What the shares mean

Each share is weighted with SurveyUSA's own weight, built to match
Arlington's 2025 electorate on age, gender and race; the targets behind it are
not in the copy we hold. Every share carries the unweighted number of
respondents in its category and the unweighted number who answered that way,
so a share resting on thirty-seven people cannot be read as one resting on
four hundred.

The preparers marked each cell `ok`, `caution` or `suppressed`.
`code/clean/survey_rcv.py` keeps a `caution` cell and flags it `thin`, rather
than dropping it. Twenty of the 132 cells are thin, and they are not evenly
spread: of the seven race and ethnicity categories only White and Black are
unflagged. Hispanic respondents number 37, and two of their three measures
are marked. Those are precisely the cells the community-input analysis'
claim about Latino voters turns on, so dropping them would answer the
question by removing the evidence. A `suppressed` cell has no share to carry
and is blank.

Race and ethnicity are the respondent's own yes or no answers and overlap: a
respondent who gave two is in both rows, so those rows do not sum to the
total and no figure may stack them.

## What rests on an assumption

- That a `caution` cell is worth showing beside an `ok` one, marked. The
  alternative is to show nothing where the source hedged, which would leave
  the figure silent on every group but White and Black.
- That the vendor's weight is the right one for every cut. It was built to
  match the electorate on age, gender and race, so a share by homeownership
  or education is weighted on characteristics that are not the cut being
  shown.
