# Repository decisions

The reasoning behind the rules in `CLAUDE.md` about how the repository is
kept. `CLAUDE.md` states each rule and points here; this file says why, and
what happened where a rule came from an incident.

## Why `data/clean/` is committed and `data/built/` is not

**`data/clean/` is committed even though it is generated.** The usual rule is the
opposite, and we follow it elsewhere. These are small CSVs, and committing them
means a cleaning decision shows up as a reviewable diff — you can see exactly
which numbers moved and by how much. That matters while those are open.
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
