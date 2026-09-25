# Setup

For anyone joining the repository. Paste everything below the line into a
new Claude conversation; it tells Claude what the project is and how to help
get set up.

---

## The project

Arlington County's Board Structure and Performance study: a historical and
descriptive-representation analysis of the County Board, 1870 to the present.
The work product is a paper with figures. The figures are drawn from data
that the repository assembles from primary sources — census volumes, the
county's election records, a published roster of Board members — and every
number in them either traces back to the page it came from or says plainly
that it is an assumption.

## The tools

Four things, each doing one job:

- **Git and GitHub** keep the repository. It is private, on GitHub, and
  everyone works from their own copy on their own machine, pushing changes
  back when they are done.
- **Python** does the computing. The scripts need four packages — pandas,
  matplotlib, openpyxl and pyflakes — which live in a virtual environment inside the
  repository folder so nothing has to be installed system-wide.
- **Claude** works with the repository two ways. **Claude Code** is Claude in
  the terminal: it reads and edits the files directly, runs the build, and
  pushes changes back. A **Claude Project** can instead sync the repository
  from GitHub and answer questions about it — where a number came from, what
  is still open — without being able to change anything. Either needs a paid
  Claude plan; the $20-a-month one is enough.
- **Overleaf** is where the paper is written. It is linked to the GitHub
  repository, so the figures the scripts produce appear in the paper without
  being uploaded by hand.

## The repository

Everything is built by one command, `bash run.sh`, from files that are
committed in the repository. Data flows downward through four folders of
code, each writing one folder of data:

- `code/fetch/` downloads a published source and saves it, unchanged, into
  `data/raw/`. It is run only when a new source is needed; the downloaded
  file is committed, so nobody else needs to fetch it again.
- `code/transcribe/` reads the scanned documents in `data/raw/` into tables in
  `data/transcribed/`. Also run only when something new needs reading, and
  its output is committed.
- `code/build/` turns the raw and transcribed files into the clean tables in
  `data/clean/`. This is where every decision about what a number *is* gets
  made — what a blank means, which of two conflicting figures to trust.
- `code/analysis/` draws the figures from `data/clean/` into `figures/`. One
  script per figure. These scripts decide how a number is shown, and they
  cannot see anything above `data/clean/`, so a figure can never quietly
  change a value.

`run.sh` runs the last two every time; the first two only run when someone
asks for them. Alongside those: `paper/` holds the LaTeX source that Overleaf
syncs, and `docs/` holds the open questions, the record of what backs every
number, and the reasoning behind each figure.

Two rules to know before touching anything. `data/raw/` holds the sources as
published and is never edited — a defect in one is corrected in
`code/build/`, where the correction is visible. And `README.md` is the front
door — it has a table of which script
writes which file — while `CLAUDE.md` holds the working rules.

## What a working setup looks like

1. **Access to the GitHub repository and the Overleaf project.** Both are
   private, so someone already on them has to send the invitations — the
   repository's owner, or any collaborator with access. Nothing else can
   start until the GitHub one is accepted.

   *To read the data and the documentation without changing them, that plus
   a Claude Project is the whole setup.* Attach the repository in the
   Project's knowledge, with its files rather than under settings or
   connectors, using a GitHub personal access token with read access. Sync
   `code/`, `docs/`, `paper/`, `data/clean/` and `data/contents.csv`, and
   leave out `data/raw/` and `data/transcribed/` — the figures read only
   `data/clean/` for the same reason, that the layers above hold scans and
   OCR that misreads digits by design. The steps below are for changing
   things.

2. **Git installed**, and signed in to GitHub.
3. **Claude Code installed and working.**
4. **Python with pandas, matplotlib, openpyxl and pyflakes**, in a virtual environment
   at `.venv` inside the repository folder:

       python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl pyflakes

5. **A successful build.** `bash run.sh` from the repository folder should
   print the tests, a build step, eight figures, and a line about
   `figures/pdf` and `figures/png`. That is the test that everything works.
   Invoke it through `bash`, not `./run.sh`; `run.sh` says why at the top.
6. **The Overleaf project open and synced.** In Overleaf, the GitHub link
   is under the **Integrations** tab in the icon rail down the left of the
   editor, not under the Menu; pull from GitHub before a writing session and
   push when done, so the paper and the repository stay the same thing.

## How to help

**Start by working out what they want to do, because that decides what needs
setting up.** Ask it that way round rather than asking which tool they want.

If they mean to read — check where a figure's numbers came from, see which
questions are still open, follow how a total was derived, talk through the
methods — then a Claude Project synced from GitHub is the whole setup, and
nothing has to be installed. Stop after step 1.

If they mean to change anything — correct a number, edit a figure, add a
source, rebuild the outputs — that is Claude Code, and the rest of the steps
apply.

The two are not exclusive and the first is far cheaper, so someone who is
not sure can start with the Project and add Claude Code when they first hit
something they want to change.

Either way the invitations come first, since nothing works without them. If
they do not have both, say exactly what to ask for and whom to ask — an
invitation to the `slhudson/arlington-bsap` repository on GitHub and to the
`arlington-bsap` project on Overleaf, both to the email address they will
use, from the repository's owner or any existing collaborator.

For the Claude Code path, any of the tools may be new or may already be in
place; ask rather than assume, in either direction. Where something is new,
the setup is part of the job: installing Git and signing in to GitHub,
installing Claude Code and signing in to it, creating the Python environment
(which happens inside Claude Code once it is running), cloning the
repository, and connecting to the Overleaf project. Ask what operating
system they are on and go one step at a time: say what to type, what they
should see if it worked, and what to do if they see something else, and wait
for them to confirm before the next step. If a step needs something only the
repository's owner can do, say so plainly and say what to send them, rather
than working around it.

Once `bash run.sh` works, the setup is done. For orientation, a good first
thing to do is to open Claude Code inside the repository folder and ask it
to walk through `README.md` and `CLAUDE.md`; then change something small in
one figure — `code/analysis/` has one script per figure, named for the figure it
produces, and `style/` holds the colours, fonts and chart types they share —
and rebuild, to see the loop work end to end.

## Reaching the archives

What each archive needs from this machine, learned in September 2026. None
of it is in `run.sh`; these are the on-demand routes behind `data/raw/` and
the Drive folder, and they change, so check before relying on one.

- **Library of Congress, Chronicling America** (the Washington Evening Star
  to 1963, which prints candidates' home streets in the week before an
  election). A JSON API:
  `https://www.loc.gov/collections/chronicling-america/?q=Surname+Arlington&dates=1955-09-01/1955-12-31&fa=partof_title:evening+star+%28washington%2C+d.c.%29+1854-1972&fo=json&c=10&at=results,pagination`;
  each result's resource JSON (`&fo=json&at=resource`) names a
  `fulltext_file` (the OCR text) and a `pdf` (the page). It rate-limits
  after about 55 fetches (a 503, or a Cloudflare page on every route from
  the machine, browsers included); a few minutes clears it, and about 220
  fetches across three pauses is a day's budget. One request every few
  seconds, one worker.
- **Virginia Chronicle** (Library of Virginia; the Sun 1935–51, the
  Arlington Daily 1943–48, the Northern Virginia Sun 1957–78). Cloudflare's
  human check blocks curl and the built-in browser; it passes in Sally's own
  Chrome, after which Claude in Chrome can search (`?a=q&txq=Surname&puq=NVS`
  with a date range) and read pages. A page's text needs no login:
  `?a=d&d=<page id>&f=XML`. The page PDF needs the site's free login, which
  Sally has and enters on request; it then opens in Chrome's viewer and the
  download icon saves it as `<page>.pdf`, though Chrome has refused that
  click from a second tab, in which case Sally saves each page herself
  (Cmd+S) at about a page a minute; plan for that. A downloaded PDF's text
  layer differs from the `f=XML` OCR, so identify a page by the id in the
  tab's URL, not by matching text. Title codes for `puq`: TSU the Sun
  (1935–51), TAD the Arlington Daily (1943–48), TDS the Daily Sun
  (1951–56), ALCR the Arlington County Record (1932–33), ANG the
  News-Gazette (1936), NVS the Northern Virginia Sun (1957–78). Addresses sit on the election-week
  jump page, not where the surname is densest: search the surname, then scan
  every hit page's full text for "lives at", "home is at", "resides at" or
  "of <number> North/South"; the Sun's 1947 candidate series and the Daily's
  appointment stories put the street in the first sentence. The OCR
  misreads house numbers (3111 for 3411); read each number off the page
  image before writing a row.
- **Ancestry** (the 1880–1950 censuses with street and house number, race,
  gender, age, occupation). Needs Sally signed in in Chrome. Search by URL:
  `https://www.ancestry.com/search/collections/62308/?name=First_Last&residence=_arlington-arlington-virginia-usa_22922`
  (62308 is 1950, 2442 is 1940, 2441 is 1930). On a record page the
  record's own sheet is the imageviewer link whose `pid` is the record id;
  the first imageviewer link can still be the previously viewed sheet for a
  few seconds. The sheet downloads from the viewer's Save button, "Save to
  your computer", into `~/Downloads` as `<image id>.jpg`. Hill's Arlington
  County directories are not in Ancestry's city-directory collection; its
  Alexandria volumes cover the 1930s and 1940s only.
- **ProQuest** (the Post 1877–2001, including the 11 November 1973
  residence map): a UVA or public-library login; neither was available.
- **washingtonpost.com**: refuses curl and the built-in browser; in Chrome
  the archive pages show two paragraphs once a few have been read. The
  older `wp-dyn` pages (about 2005–2010) read in full.
- **Claude in Chrome's JavaScript tool** refuses to return any output that
  contains `?`, `&` or `=`; strip them before returning. A worktree has no
  `.venv`; a symlink to the primary checkout's works, and pymupdf there
  renders page clips (`pdftoppm` is not installed).
- ARLnow, InsideNoVa, Connection Newspapers, Arlington Magazine, the county
  site and legacy.com fetch with curl and a browser user agent, and print to
  PDF with headless Chrome from the saved HTML with its scripts removed.
  Dignity Memorial and some funeral homes sit behind Cloudflare.
