# Sources

Every `source` cell in `data/clean/` holds a citekey from `paper/sources.bib`
or one of three placeholders: `unsourced` (a claim exists and its evidence is
not yet named), `derived` (computed from another clean table, whose rows carry
the citations) and `assumed` (no claim exists; the build supplied a value from
a standing assumption). `code/build/citekeys.py` says what each admits to, and
`bash run.sh` counts them on every build. What each number rests on is in
`docs/residents.md`, `docs/board.md` and `docs/voters.md`.

---

## Works cited

Every source named on this page has an entry in `paper/sources.bib`, which the
prose and the data share: a `source` cell in `data/clean/` holds the same
citekey a footnote in the report will. `bash run.sh` refuses to build if a
cell names an entry that is not there.

One entry is still marked provisional in its annotation, POP-TWPS0076, for the
reason given under Population and race. Two details were corrected against the
documents while the entries were built: O'Leary's electoral history is dated
March 2010 in its own text (the 2012 once carried was the PDF's creation
date), and the county's compilation is titled *Arlington County Election
Results*; "Candidate History, 1920-Present" was the website's link text.

Sources consulted to settle a question rather than to take numbers from are
cited here rather than saved into `data/`. **Their copies live in the
project's Drive folder**, in `sources/documents`
(<https://drive.google.com/drive/folders/10SGuURB-ldC1AzM3ClsdL_tAiWeFIZB4>),
named for a person reading the folder: author, year, then the title as the
document prints it, `Pratt 1995 - Arlington's At-Large Electoral System.pdf`.
Each entry in `paper/sources.bib` carries a "Filed in Drive as" line, which is
where you check that a cited source is filed. Hjerpe's is a PDF snapshot
rather than the live Google Doc, which belongs to someone outside the project
and can change; cite the snapshot. The ten pieces of reporting cited for
party are not yet filed.

**City of Alexandria.** *A History of the Boundaries of the City of
Alexandria, Virginia: 1749-2024.*
`alexandriava.gov/sites/default/files/2024-06/History of the Boundaries of Alexandria 1749-2024.pdf`
— Alexandria annexed land from Alexandria County in 1915 and again in 1930,
the second including the Town of Potomac.

**Rose, C. B.** "Annexation of a Portion of Arlington County by the City of
Alexandria in 1915." *Arlington Historical Magazine*, 1964.
`arlhist.org/wp-content/uploads/2017/02/1964-4-Annex.pdf`
— The size and effective date of the 1915 annexation: 866 acres, effective
1 April 1915.

**Anderson, Robert Nelson.** "Arlington Adopts the County Manager Form of
Government." *Arlington Historical Magazine*, 1958, 52–67.
— A first-hand account of the 1930 referendum and the 1931 election, by a
founder of the Historical Society.

**Bestebreurtje, Lindsey.** *Built by the People Themselves: African American
Community Development in Arlington, Virginia, from the Civil War through Civil
Rights.* Two documents with one title, entered separately: the 2017 George
Mason University dissertation (`bestebreurtje2017`, from its own title page)
and the 2024 University of South Carolina Press book (`bestebreurtje2024`,
from the publisher's catalogue). A digital exhibit at lindseybestebreurtje.org
is a third. Neither document is in hand; the page cited for the 1930
candidacies of Harris, Morton and Mosley has not been read
(`bestebreurtje-p215` in `docs/questions.csv`).

**Pratt, Sherman W.** "Arlington's At-Large Electoral System: A Study of Its
History, Strengths, and Weaknesses." *Arlington Historical Magazine*, October
1995, 19–35.
— Heard Vollin's testimony and holds his own tape recordings of him. The
source for both Vollin citations, which are two proceedings, not one: the
federal suit, *George Vollin, Jr., et al. v. Mills E. Godwin, et al.*, E.D.
Va., Civil Action No. 173-74-A, in which Vollin testified in 1974
(`vollin1974`); and *Vollin v. Arlington County Electoral Board*, 216 Va. 674,
222 S.E.2d 793, decided 5 March 1976 (`vollinelectoralboard`), a petition to
put district-versus-at-large election to a vote, denied because the county had
already adopted the County Manager Plan. Cases are entered as `@misc` with the
court and docket in `note`, because biblatex-chicago in notes mode silently
drops the legal entry types.

**Hjerpe, Grace.** *A History of Representation on the Arlington County Board,
1870-Present.* Updated 15 July 2021. Google Doc, shared with Sally.
— Names all five Black members of the Reconstruction-era board, with 1880
manuscript census records reproduced as appendices, and tabulates every Board
member by district from 1871 to 1888. Also documents the 1930
change-of-government referendum, the 1974 Vollin case, and that the federal
government began removing residents from Freedman's village in 1888, the year
Tibbett Allen, the last Black member, was removed for "non-residence". Cited
by the page the document prints, which runs one behind the PDF's. Its
footnotes point at `vote.arlingtonva.us`, which now returns a not-found page
rendered as a PDF; the live copies are on `vote.arlingtonva.gov`.

**O'Leary, Frank.** *The Electoral History of That Part of Alexandria County
Now Known as Arlington County, 1870-1920.* Version 2, March 2010. Arlington
County Treasurer. In `data/raw/arlington_county/`.

**Arlington County Office of Voter Registration and Elections.** *Arlington
County Election Results* ("Candidate History, 1920-Present"). Last updated
18 November 2021. In `data/raw/arlington_county/`. The county has since taken
it down; its results page points to the state.

— Between them these cover Board elections for the whole period. Both are
compilations rather than primary records, and both say so: O'Leary compiles
from the Alexandria Gazette with party affiliation "inferred", and the
Electoral Board's preamble notes incomplete early tallies and invites
corrections. They record elections rather than service, and neither carries
race or gender.

**Virginia Department of Elections.** *Historical Elections Database.*
`historical.elections.virginia.gov`. Every County Board contest from 2000 and
Arlington's presidential vote from 1924, saved as the database's own CSV in
`data/raw/va_dept_of_elections/`. Cited by contest id, the database's own key
for a race. Its monthly *Registration Statistics* supply registered voters
from 2010.

**Novack, Norman S.** "Six Decades of Arlington Leadership." *Arlington
Historical Magazine*, 1994.
`arlhist.org/wp-content/uploads/2020/02/1994-6-Decades.pdf`
— A complete roster of County Board members with terms of service to the
month, from the County Manager plan through 1994, with the circumstances of
each mid-term departure. The roster's source for 1932–1994. Carries no race or
gender. In `data/raw/arlington_historical_magazine/`.

**U.S. Census Bureau.** *Population of States and Counties of the United
States: 1790-1990.* Virginia notes, printed p.185.
— Establishes that Alexandria city became independent of the county in 1900
for census purposes, that the county was renamed Arlington in 1920, and that
county figures reflect boundaries as reported at each census. The Virginia
pages are excerpted into `data/raw/us_census_bureau/` because numbers are
taken from them.

**The Sun (Arlington).** 11 November 1938, p.1 (`sun1938referendum`) and 18
November 1938, p.4 (`sun1938womenvoters`), from the Library of Virginia's
Virginia Chronicle. The first is in `data/raw/arlington_sun/` because a number
is taken from it (`referendum-1938-margin` in `docs/questions.csv`).
