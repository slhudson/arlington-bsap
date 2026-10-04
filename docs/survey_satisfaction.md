# The Resident Satisfaction Survey

Arlington County hired Zilo International Group to run its 2026 Resident
Satisfaction Survey, fielded in February and March 2026, and Zilo collected
1,613 completed questionnaires by mail, online, telephone and about twenty
days of in-person outreach at libraries, community centres, human services
sites and farmers markets, promoted through civic, nonprofit, educational,
business and faith-based partners. The County shared both the published
report and the response-level file with the project team. Both sit in
`data/raw/arlington_county/` and are cited as `zilo2026` and `zilo2026data`.

The report's part on community input rests on this survey for what residents
say about the Board and about how the County decides things. Question 4 asks
five statements on a five-point agreement scale, of which two bear directly:
whether the respondent is familiar with Arlington's form of government and
Board structure, and whether that structure is right for this community.
Question 3 supplies two more on a satisfaction scale, transparency of the
County's decision-making process and opportunities for public engagement, and
question 1 supplies the effectiveness of the County's communication with the
public. `data/clean/survey_satisfaction.csv` carries those eight items, one row
per respondent, beside the demographics the report cuts them by.

## What a blank means

The workbook records three different refusals and distinguishes none of them.
A respondent can leave an item blank, can choose "Don't Know" where the
satisfaction scales offer it, or can choose "Prefer not to answer" where the
demographic questions offer it. `code/clean/survey_satisfaction.py` keeps all
three apart: an explicit refusal becomes `declined`, "Don't Know" stays as the
instrument prints it, and a blank stays blank.

Income is the exception that shows why this matters. That question offers no
refusal, so a resident unwilling to state a household income has nowhere to
say so and leaves it empty, and 302 of 1,613 do — twice the rate of any other
demographic. The blanks on income are not the same quantity as the blanks on
race, and reading them as one would understate how many residents decline.

Zilo's own percentages take non-blank responses as the denominator, and the
trend charts drop "Don't Know" as well, so that a satisfaction share rests on
the same base in every cycle. This repository follows that convention where it
reproduces a published figure, which is how the toplines here match the report
exactly: 71.0 per cent familiar with the structure, 43.2 agreeing it is right
for the community, 49.5 trusting elected officials, 35.5 satisfied with
transparency.

## Race

The instrument puts race to the respondent as eight boxes, any number of which
may be checked, and 84 respondents check more than one. The census asks race
and Hispanic origin as two questions and publishes them crossed, and
`data/clean/residents.csv` carries that crossing, so the two tables can only be
set side by side if the survey is cut the same way (`docs/residents.md`).
`code/clean/survey_satisfaction.py` therefore reads Hispanic of any race first,
then among the rest White, Black, and Asian or Pacific Islander alone, and
puts everyone else — a respondent naming two races, American Indian or Alaska
Native, or "Other" — together. The 173 respondents who check "Prefer not to
respond" are `declined` and the 178 who check nothing are blank, and neither
is counted into a race.

## What the earlier waves can and cannot settle

The report compares 2026 against 2022 and 2018 for questions 1, 3, 12, 16, 17,
18 and 20, and for nothing else. Question 4 carries no earlier wave, so the two
items that speak most directly to the Board's structure — whether residents are
familiar with it and whether they think it is right for this community — have
no trend. They are new in 2026: the County's review of its form of government
began within the year before the survey was fielded, and the five statements
were written for this instrument. The 2026 reading of them stands alone, and
nothing in the report licenses a sentence about residents' views of the Board's
structure moving.

What does have a trend is transparency, and it falls from 42 per cent
satisfied in 2018 and 42 in 2022 to 36 in 2026. Those values exist only as a
bar chart on page 83 of the report, printed as an image whose numbers no
software can read, so a person read them off the chart and keyed them into
`data/transcribed/by_claude/survey_satisfaction_by_year.csv` with the page. Eleven
of question 3's twelve items appear there; the County's efforts to improve
equity is on the instrument and not on the chart.

## How far the sample departs from the county

Of 1,613 respondents, 1,262 name a race. Against the county's 2020 census
composition, those 1,262 are 70.7 per cent White where the county is 58.5, and
9.4 per cent Hispanic where the county is 15.7. Black and Asian or Pacific
Islander residents are short by two and three points. The sample's White
majority is twelve points larger than the county's, and the gap is widest for
Hispanic residents, who are a little over half as present in the survey as
they are in Arlington.

Every figure and table built from this file reports subgroup shares as
fielded. Nothing in the repository weights a response to the county's
composition on race or any other characteristic; the departure above is the
correction a reader gets, not one the data gets.

Zilo states that the dataset "achieves a 95% confidence level with a margin of
error of approximately ±2.4%". That is the figure a simple random sample of
1,613 would carry, and the sample Zilo describes is a voluntary one recruited
partly through partner organisations, so this repository does not repeat the
margin of error and does not treat subgroup differences as significant or not
on the strength of it.

The comparison stops at race. `data/clean/residents.csv` holds the county's
race and age by census year and nothing on tenure, income or gender, and the
survey asks for the ages of a respondent's household rather than the
respondent's own, so neither age nor the three economic characteristics can be
set against the county from what the repository holds.

## What rests on an assumption

- That the values the report's trend chart prints are the published
  values. This repository has no microdata for the earlier waves, so the chart
  is read as printed, including the 2018 values for the County's efforts to
  embrace diversity and the overall inclusiveness of the community, which equal
  their 2026 values.
- That a respondent who leaves race, income and gender blank or declined has
  declined to give demographics, which is the definition
  `demographics_declined` applies to 147 respondents. A respondent who
  simply stopped answering before reaching those questions is counted the
  same way.
