# Paper punch list

Small fixes to the report noticed while reading the PDF: a wording, a title, a
table's spacing, a figure's placement. One line per item, in plain words, with
the page or section if you have it. No compiling and no decisions belong here;
a decision that changes a number, a citation or a figure's form is a row in
`docs/questions.csv`.

Cleared in batches: a session takes the whole list, makes each change, builds
the paper, commits, and deletes the lines it cleared. What it cannot settle
stays, with a one-line reason under it.

## Open

- Figure 3 (county by race) legend: consider alphabetical order (Asian & Pacific Islander first), since nothing says why Black comes first. The figures skill says a legend follows stacking order, and docs/figures.md sets the stack with the largest group on top; if the legend goes alphabetical, decide whether the stack does too, and apply the same rule to Figure 4 and the gender figure.
- A map of the three magisterial districts, perhaps on the same page as the Black-share-by-district figure. How to render it: for simplicity, a stylized version drawn with a little GIS coding of our own (district polygons from the traced boundaries over the modern county outline, in the style layer's colors), not a reproduction of the 1900 map. The boundary source and the build are on the tracker (district-map).
- Age: soften the Board half. Be cautious about saying the Board is not representative by age: no one under 18 can serve, so the comparison base is adults (or eligible voters), and age correlates with knowledge and professional skill, so the claim needs a conversation before it is made strongly. If the claim stays, it needs a figure that makes the comparison directly, probably in a different format from the two now in the section. (Decision; tracker row age-board-against-county.)
- Headings and spacing are not yet nailed for skimmability (Sally, 4 October 2026, looking at the data appendix): the part, section, subsection and run-in levels need a deliberate scheme of weight, style and white space above and below so the eye finds the structure at a glance; a typographic pass over the whole document, one scheme applied everywhere, shown before and after.
- A.1 (Board Seats) and A.2 (Election Method) both give the 1930 referendum's at-large vote, 1,689 to 1,149, with the same Rose citation. Keep it in A.2 and have A.1 say the same referendum chose at-large election, with a pointer to A.2.
- Ban "the record" from the draft (Sally, 4 October 2026): it is the project's shorthand for what the sources show, and a resident would not read it that way. Six places: Part A Race and Ethnicity, "Four Forces" ("the record bears on each differently"), and the subsection "What the Record Settles" with its opening sentence; Part C Gender ("the one claim on the record") and Race and Ethnicity ("the question the record cannot test"); and in the Data Appendix, "The repository records each disagreement" (Sources) and "the repository's members table" (Seat-Years), which want the archive delivered to the County instead of the repository. When the six are gone, add a test that fails on the phrase.

## Could not settle
