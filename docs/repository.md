# Repository decisions

The reasoning behind the rules in `CLAUDE.md` about how the repository is
kept. `CLAUDE.md` states each rule and points here; this file says why, and
what happened where a rule came from an incident.

## Why `data/clean/` is committed and `data/built/` is not

**`data/clean/` is committed even though it is generated.** The usual rule is
the opposite, and this repository follows it everywhere else. These are small
CSVs, and committing them means a cleaning decision shows up as a reviewable
diff: a reader can see exactly which numbers moved and by how much. That matters while those are open.
`data/built/` is not committed: it holds no decisions, rebuilds in seconds
from the layers above, and would add 1.6MB to the text Overleaf syncs.
`bash run.sh` makes it before anything reads it.

## Why the style layer sits outside `code/`

The conventions themselves are the Urban Institute's data visualization style
guide, loaded from `style/urban.mplstyle` and cited there. Where this project
departs from Urban, the departure and its reason are in `docs/figures.md`,
which holds the reasoning behind every visual convention; the style layer
states the values.

`style/` sits outside `code/` because most of it cannot be executed: a typeface
and a table of rcParams. `code/` is for things you can run.

## Why `run.sh` never touches the network

Two reasons. Anyone who clones the repository can build it — no account, no API
key, no connection. And an API can change its answer, so a live call could move
a figure between runs with nothing in the repo to explain it; a committed file
is the same evidence standard as a scanned page.

The one exception is twenty-four census scans the build never reads, about
250MB that would push Overleaf past its ceiling. They are marked `in_git = no` in
`data/contents.csv` with their URL and checksum; `code/fetch/census_volumes.py`
fetches them and refuses a byte that differs, and `run.sh` says at the end of
every build if they are missing. A raw file the build reads is always
committed.

## Why one repository, with `paper/` inside it

**One repository, with `paper/` inside it.** Overleaf syncs a whole
repository and cannot be scoped to `paper/` and `figures/`, so it carries the
data too. Its limits are on the files it syncs, not on git history: a
recommended 100MB in all, and a hard 7MB on editable (text) files, past
which GitHub sync stops working. One repository was chosen because pushing
figures across a repository boundary would undercut the case that this setup
is simpler than emailing files. `run.sh` warns at 80MB and at 6MB of text, so
revisiting does not depend on anyone remembering; a gzipped file is counted
against the whole, not against the text, since it is not editable. The scans the build never
reads are already fetched on demand rather than committed, and so is the
OCR of the census volumes (`data/transcribed/by_ocr/`, regenerated on a Mac by
`code/transcribe/census.py`), which took 1.8MB of the text cap. If the cap
trips again, the candidate is the state's 2MB election CSV.

**A job that depends on another waits for its tracker row, not its branch.**
A project is finished when its row leaves `docs/questions.csv` on `main`;
that is what settling a question means here, and it is the only signal a
second session can check. Branches are invisible until pushed and can be
renamed, so a gate on "has that branch merged" passes for the wrong reason.
Push a branch the moment it is created, so that others can see it exists.

## Why one session works on main and two take worktrees

Two sessions sharing one checkout once produced committed figures built
against uncommitted edits, so `figures/` no longer matched `data/clean/`
beside it. Since then a session that is not alone in a checkout takes a
worktree on a branch, and the hook in `.claude/settings.json` says at the
start of a session which case applies. It advises and never blocks, since
collaborators may be new to Git.

**The hook once judged this by counting worktrees, which misses simultaneous
starts.** `git worktree list` only grows once some session has already taken
a worktree; it says nothing about how many sessions are live in the primary
checkout before any of them has. Four sessions once started at once with
none, so all four read "0 other worktrees" and all four worked directly in
the primary checkout, which is the exact case the hook exists to prevent. The
hook now writes its own liveness marker instead: a PID and a timestamp in
`.claude/tmp/session.lock` (machine-local, gitignored), checked with `kill
-0` against whatever PID it finds there, ignoring one it wrote itself or one
past its shift. Two sessions starting in the same second each see the
other's PID as soon as either has written it, which a static count of past
worktrees cannot.

Collaborators each work in their own clone, so they cannot share a checkout;
they meet only at push, and a rejected push means pull, run the build again,
push. The build itself is reproducible: the same sources in a fresh virtualenv
give byte-identical figures, so two people who pull the same commit hold the
same `figures/`.

## Why the paper compiles with lualatex, and the two ways it fails

`paper/arlington-bsap.tex` sets its body text in Lato, the typeface
`style/urban.mplstyle` gives the figures, so the report and the charts inside
it read as one document. Choosing a typeface by name needs `fontspec`, and
`fontspec` runs only under lualatex or xelatex, never under pdflatex. Both
authors and Overleaf therefore have to use the same engine, and the file says
which in its first line:

```
% !TeX program = lualatex
```

That is a magic comment. Overleaf and latexmk both read it and switch engines
on their own, which is why it lives in the file instead of in an Overleaf
project setting only one author can see.

The four Lato faces are committed under `style/fonts/` rather than installed,
so the fonts travel with the repository to Overleaf and to the other author's
machine. All four are declared in the preamble: an undeclared face is
substituted silently, which is the second failure below.

**Compiling with pdflatex stops with a fatal fontspec error**, naming the
engine it wants:

```
Fatal Package fontspec Error: The fontspec package requires either
XeTeX or LuaTeX.
```

This failure is loud and costs nothing. Compile with `latexmk -pdflua
arlington-bsap.tex` from `paper/`, or let an editor read the magic comment.

**A stale `paper/arlington-bsap.fdb_latexmk` silently drops every citation.**
That file is latexmk's record of which tools it ran last time. The paper uses
biblatex with `backend=biber`; if the record holds bibtex from an earlier
build, latexmk keeps calling bibtex, which finds no citations in a biblatex
document and reports errors most editors bury. The PDF still builds, and every
footnote citation and every `\ref` to a figure comes out undefined. It is the
dangerous failure, because a report that is missing its sources looks finished
at a glance.

The cure is to clear latexmk's record once, after any engine change:

```
cd paper && latexmk -C && latexmk -pdflua arlington-bsap.tex
```

On Overleaf the same staleness is cleared by *Recompile from scratch*, under
the Recompile dropdown.

A good build reports no font warnings and no undefined references. If the log
says `Font shape ... undefined, defaults substituted`, a face is missing from
`style/fonts/` or from the `\setmainfont` declaration; if it says citations
are undefined, biber did not run.
