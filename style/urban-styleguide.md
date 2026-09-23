# The Urban Institute style guide, as we hold it

`urban-styleguide.html` is the guide itself, taken from Urban's own repository
at <https://github.com/UrbanInstitute/graphics-styleguide>, commit fetched
23 September 2026. It is the document `urban.mplstyle` implements, kept here
so the conventions can be checked without a connection and so a claim about
what Urban says can be verified rather than remembered.

The repository is 231MB, almost all of it images and Excel add-ins. This is
the text, which is 195KB.

## What it does not contain

**Spacing.** There is no guidance on white space, padding or margins: zero
occurrences of "white space", "whitespace" or "padding", one of "margin" (a
margin of error), and every "spacing" hit is about character spacing in the
tagline or line spacing in Word templates. The numbers live in Urban's R theme,
not in the published guide, so every spacing decision in `urban.mplstyle` is
ours and is marked as such.

## What it says that we do not follow

Departures are listed in `style.py` with their reasons. Two are worth naming
here because they are explicit in the guide rather than merely absent from it:

**Colour for gender.** The guide says: "Urban tries not to use color palettes
that reinforce gender or racial stereotypes (e.g., pink for women and blue for
men)." The gender figure does exactly that, at Sally's direction and before
either of us had this text.

**Legend size.** The guide puts legend text at 9.5pt against 8.5pt for axis
labels and ticks. Here both are 8.5, set in `urban.mplstyle` where the size is: inside these figures a legend entry and a
tick label both name a mark, and the difference read as arbitrary rather than
as hierarchy. The one size that remains distinct is the `(a)`/`(b)` panel
label, which has no counterpart in Urban's table — their title is 12pt and
sits in the Word document beside the image, which is where this repository
puts it too, in the LaTeX caption.

**Capitalisation in legends.** The guide says: "Use sentence-style
capitalization for all text within the figure, including axis titles, data
labels, and legends." Our legend entries are title case, because a legend is a
list of names rather than a sentence. Axis labels and panel titles do follow
the rule.

**A beige for the largest category.** The guide says to avoid colours
associated with skin tones. The sand carrying White is a beige, kept
deliberately: the largest category works as a backdrop the others read
against.
