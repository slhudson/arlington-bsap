---
name: prose
description: Write or edit the report's prose and the write-ups in this repository's voice. Use whenever text in paper/ or docs/ is being drafted, rewritten or reviewed, including a figure's caption and a tracker row's sentence.
---

# Prose

The report is read by a county board, by the people it is about, and by
collaborators who will check it. Write so that a reader who knows the subject
but not this project understands a sentence the first time.

## The sample

The voice is Sally's, and it is published. Two samples, and the second is
the closer one:

    https://www.rankedchoiceva.org/news        the Charlottesville series
    "Final Report - Arlington RCV Evaluation"  Drive; to the County Board

The five-part Charlottesville series traces an electoral system through its
own records: same state, same subject as this report. The RCV evaluation is a
formal report to the Arlington County Board — the same body that will read
this one — and it is the model for register, for how a method is explained
and for how a limitation is stated.

Read a sample before a long rewrite, not a summary of one. Everything below
is drawn from them, and where a rule here and the sample disagree, the sample
is right.

Three books stand behind it, and none of them is a word count.

    Strunk, The Elements of Style (1918)    what to cut and what to prefer
    Orwell, Politics and the English        the escape hatch, below
      Language (1946)
    Williams, Style: Lessons in Clarity     why a sentence reads badly
      and Grace

Strunk says prefer the active voice, write with nouns and verbs, omit needless
words. Williams says why those work: make the characters of a sentence its
subjects and their actions its verbs, put information the reader already has
before information that is new, and end on what you want to land. Orwell says
the rest of it can go: "Break any of these rules sooner than say anything
outright barbarous."

That last line governs the others. Nothing here is a limit to be counted.

## What the voice does

**Somebody is doing something in every sentence.** The NAACP launches a
campaign, the commission delivers a proposal, the Department of Justice forces
two cities to abandon block voting, Virginia Carrington testifies. Named
actors, active verbs. This is the strongest single feature of the sample and
the one to reach for first when a passage will not come right.

The actor is never the authors: this report avoids *we*. Nor is it the work
itself — "the study", "the figures", "this analysis" as a grammatical subject
is the construction that makes a passage dense, and swapping in *we* is not
the cure. The actor is the thing in the world that acted. Not "the figures
assume a member served to the end of his term" but "the minute books record
no resignation, so a term runs to its end." Not "this study's outside sources
are exhausted" but "the census closes for seventy-two years and the
directories stop being published." A source, a court, a Board, a statute, a
census sheet: something did something, and naming it removes the passive and
the abstraction together.

**No number arrives bare.** It comes with what it bought or cost, in the same
sentence: "the only Black candidate that cycle, James Hicks, lost by 175
votes, leaving Charlottesville with an all-white council after eight years of
breakthrough leadership." A figure with no consequence attached is half a
sentence.

**Paragraphs land.** They end on the stake, not on the last fact to hand:
"In winner-take-all elections, the losing team has little incentive to play
the game at all." "The failed referendum would haunt election reform efforts
in Charlottesville for decades."

**Sentences are long and freely subordinated.** A main clause with two or
three modifiers hanging off it is normal here, and dashed asides are frequent.
Nothing in this file asks for short sentences.

**Sources speak in their own words.** Where a document says the thing better
than a paraphrase would, quote it and build the passage around the quote.

**A method is taught by working one case.** Not described in the abstract:
"To illustrate the weighting procedure, consider the representation of Latino
voters in the survey sample. CNN found that Latinos were 5% of all Virginia
voters in 2025, while the US Census estimates that Latinos were 9% of
Virginia residents, so Latinos voted at lower rates than other ethnic
groups." Pick the instance that shows the mechanism and walk it through. This
is how `docs/` should explain how a number is built.

**A limitation is named where it bites, then sized.** Not deferred to a notes
section and not hedged into mush. State it, say how much it matters, stop:
"The remaining differences are within the margin of error for the given
sample size, though early in-person voters may remain slightly
over-represented in the weighted survey results." Say too what a number does
not license: "The first two reasons do not necessarily imply that voters are
confused about RCV."

**A concession opens the sentence that answers it.** "Though weighting is an
important methodological consideration, in practice weighting has little
impact on the substantive results in this sample." Though, still, meanwhile:
the reader is walked through a qualified finding rather than left to balance
it.

## How a sentence goes wrong here

These are the failures this project's prose actually makes. Each is a shape
to recognise, not a rule to tally.

**The subject is buried.** "What places a member of those years is his census
sheet" — the reader meets a clause before meeting a thing. Ask who is doing
what, and start there: "A member's home is known only as closely as his census
sheet names it."

**A noun stands where a verb belongs.** "The application of the assumption" is
two words away from "the figures assume". Prefer the verb; the sentence
shortens itself.

**An aside changes the subject.** Dashes are fine, and the sample is full of
them, but what sits between them has to be about what the sentence is about.
The fault in the pre-1932 residence passage was not its dash; it was that the
dash held two clauses of election law inside a sentence about census sheets.
Keep the aside on topic, or give the other topic its own sentence.

**A negative about what the project does not know.** "Who was sitting is not
the open question" makes the reader hold a negative to reach a fact. A
negative about the world is different, and often the finding itself: "not a
single first-time candidate was elected from the Clark precinct." Keep those.
What goes is the negative that reports the state of our own knowledge instead
of stating it.

**The tense narrates the project.** "This is no longer the question it was"
only parses for someone who knows what it was. State the position: "The
minute books name all three seats in every year from 1870." The subject's own
chronology is the story and belongs in the prose; the project's progress
through it is in git (CLAUDE.md, *Questions and decisions*).

**Hedges stacked.** "It may perhaps be that some of these are possibly
incomplete" says less than "Two cells are missing." Where something is
genuinely uncertain, name the uncertainty once and move on.

**A list pretending to be a sentence.** Three clauses joined by semicolons
usually want to be three sentences, or a list the reader can see.

## Reading it back

Read the passage aloud. Where you stumble, the reader stops. That test finds
more than any checklist, and it is the one to run before saying a passage is
done.

Then ask of each paragraph: what does it want the reader to know? If the
answer takes two clauses, the paragraph is doing two jobs.

## What the voice is not

Not conversational. The report is formal, and a formal register is not the
same as a dense one — "the county court issued a rule against him" is both
plain and exact.

Not simplified. Keep the technical words the subject needs: magisterial
district, seat-year, enumeration sheet, citekey. A reader of this report knows
them, and a synonym for a term of art costs precision. What goes is the
decoration around them.

Not shorter at the cost of the record. Every number in the prose is checked
against `data/clean/` by `code/analysis/body_text_numbers.py` and
`code/tests.py`. If a rewrite would drop a figure, a citekey or a
qualification that carries a fact, restate the fact in fewer words instead.

## Where each kind of text lives

`paper/` is the report, and it carries the voice in full: actors, chronology,
paragraphs that land. It syncs to Overleaf, so keep the LaTeX valid, leave
section structure and labels alone unless that is the task, and do not reflow
a section to make an edit look tidy.

`docs/` is one write-up per subject, in the present tense: what each number
is, what backs it, what is assumed where nothing does, and why. The register
is more neutral than the report's — no argument, no narrative drive — but
every section still has a point, and says it. A write-up is not a catalogue
of facts in the order they were discovered. Each ends with what still rests
on an assumption.

`docs/questions.csv` is the tracker. A row is written for someone who has not
read this conversation: the question in a sentence, and what would settle it.
A recorded negative — a paper searched, a name not found — belongs in the row
and is never trimmed for brevity.

A figure's caption says what the picture shows and what a reader must know to
read it. Not how it was built.

## Corrections this project has made

Kept here so the voice accumulates rather than being re-derived. Add to it
when an author rewrites a passage, with what they said.

**27 September 2026, the sample.** The first draft of this file described a
voice it had inferred from Claude's own prose and presented it back as
Sally's: "I have no idea where you're getting the idea that you have a
writing sample for me." She then gave the real one — the RCVa news archive,
and the Charlottesville series in particular. Two of the rules here had been
inventions, and the sample contradicts both: it uses dashes to carry second
clauses constantly, and it uses negatives to state findings. Both rules were
rewritten to the narrower fault they came from. What the sample does and this
file had missed — named actors, numbers with their consequence attached,
paragraphs that land on the stake — is now the first section.

**27 September 2026, the Board report.** Offered as "a longer report for the
same audience": the RCV evaluation prepared for the Arlington County Board.
It settles the register question for `paper/`, and it adds three habits the
Charlottesville essays show less plainly — a method taught by working one
case, a limitation named where it bites and then sized, and a concession that
opens the sentence answering it.

**27 September 2026, no first person.** The Board report uses *we* freely for
the project's own choices, and the paper was offered the same construction:
"avoid we." So the fix for an impersonal, dense sentence is not first person
but a real-world actor — the source or the institution that acted. See the
first entry under *What the voice does*.

**27 September 2026, the register of `docs/`.** Asked whether the write-ups
should carry the narrative voice or stay flat reference prose: "i think docs
can be more neutral but in general should have a point." Hence neutral
register in `docs/`, but no section that merely lists.

**27 September 2026, `paper/arlington-bsap.tex`, pre-1932 residence.** A
rewrite that stated the position rather than the history was still unreadable:
"It may read as a statement. It's terrible writing. Like, incredibly hard to
digest." The faults were a cleft sentence, an aside that changed the subject,
and a negative about what the project does not know. The statutory detail moved
to `docs/members.md`, which carries it in full.

Its replacement did not settle it either, and a later pass was told to
calibrate against that replacement rather than to fix it: "Why would you leave
unchanged the paragraph that bothered me enough to start this entire
exercise?" A passage offered as a reference point is not exempt from the pass.
Three sentences in it still reported the state of the project's knowledge
instead of naming something that acted — "is known only as closely as", "who
sat is known" — it closed on a tautology, and its one count arrived with
nothing to say what the count cost. The census, the law and the minute books
are now the subjects, and the count carries its consequence: the county had
only three districts to name.

**27 September 2026, on hard rules.** Numeric limits were offered and
declined: "I don't like the idea of like numeric hard rules for writing style.
Like some some rules are meant to be broken." Hence Orwell's last rule above,
and no counts anywhere in this file.
