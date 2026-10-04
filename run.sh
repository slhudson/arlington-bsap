#!/usr/bin/env bash
# Rebuild everything from data/. The only entry point (CLAUDE.md).
#
#   bash run.sh                  build, test, then every figure
#   bash run.sh residents_per    only figures whose names match; the data
#                                stages run only if their inputs changed,
#                                and the tests not at all
#
# Invoke through bash, not ./run.sh: Overleaf strips the executable bit.
set -euo pipefail
cd "$(dirname "$0")"

# A session on a branch belongs in its own worktree (CLAUDE.md); the primary
# checkout stays on main so two sessions cannot build against each other's edits.
if [ "$(git rev-parse --git-dir 2>/dev/null)" = ".git" ] && [ "$(git branch --show-current 2>/dev/null)" != "main" ]; then
  echo "WARNING: this is the primary checkout on branch $(git branch --show-current); work on a branch in a worktree (git worktree add .claude/worktrees/<name> <branch>)"
fi

# The commit guard lives in .githooks/ so it is committed and reviewable, which
# .git/hooks/ is not. Pointing at it is a local setting, so it is set here
# rather than asked of each collaborator, and the executable bit is restored
# because Overleaf strips it (above).
if [ "$(git config core.hooksPath 2>/dev/null)" != ".githooks" ]; then
  git config core.hooksPath .githooks && echo "installed the commit guard (.githooks)"
fi
chmod +x .githooks/* 2>/dev/null || true

PY=.venv/bin/python
[ -x "$PY" ] || { echo "no venv: python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl pyflakes"; exit 1; }

# One build at a time in a checkout. data/built/ is emptied and rewritten in
# place, so a second run deletes the tables the first is reading: it fails in
# the test stage saying a built table is missing, which reads like a bug in the
# clean stage and is not one. The lock makes that collision impossible rather
# than warning about it. A crashed run leaves the directory behind; the owner's
# pid is in it, so a stale lock is recognised and taken over, never waited on.
LOCK=data/built/.run.lock
mkdir -p data/built
if ! mkdir "$LOCK" 2>/dev/null; then
  owner=$(cat "$LOCK/.pid" 2>/dev/null || echo "")
  if [ -n "$owner" ] && kill -0 "$owner" 2>/dev/null; then
    echo "another run.sh is building in this checkout (pid $owner)."
    echo "  data/built/ is shared, so the two runs would corrupt each other."
    echo "  wait for it, or work in a worktree of your own:"
    echo "    git worktree add .claude/worktrees/<name> -b <branch>"
    exit 1
  fi
  echo "took over a lock left by run $owner, which is no longer running"
  rm -rf "$LOCK" && mkdir "$LOCK"
fi
echo $$ > "$LOCK/.pid"
trap 'rm -rf "$LOCK"' EXIT

# Stage 1: data/raw/ and data/transcribed/ -> data/built/. Reshaping only;
# each step is refused if a value its inputs carry is missing from its output.
BUILD=(elections members_claims candidates census ipums registration localities localities_places localities_counties localities_southeastern localities_southeastern_bodies candidates_party elections_nominations candidates_gazette survey_satisfaction survey_rcv survey_satisfaction_by_year survey_rcv_precision)

# Stage 2: data/built/ -> data/clean/. Every decision about what a number
# is. Each step is named for the file it writes, and later steps read what
# earlier ones wrote.
CLEAN=(residents residents_by_district residents_by_district_adults members members_chairs candidates members_residence members_by_year elections_results elections_turnout elections_nominations elections_margins elections_margins_by_year localities localities_southeastern survey_satisfaction survey_rcv survey_satisfaction_by_year survey_rcv_precision)

# Stage 3: data/clean/ -> figures/. Each step is named for the figure it
# writes. Five populations, alphabetical within each; last, the one step that
# writes the numbers the prose cites, paper/body_text_numbers.tex, instead,
# and members_roster writes the roster, paper/members_roster.tex, and the two
# subsets the body prints, paper/members_roster_subsets.tex.
FIGURES=(residents_by_age residents_by_district_race residents_by_district_race_adults residents_by_race residents_per_seat elections_turnout elections_turnout_before_1932 elections_turnout_before_1932_adults elections_turnout_by_district elections_board elections_president members_age candidates members_by_gender members_by_party localities_peers localities_southeastern members_by_race members_race_coverage members_residence_coverage survey_satisfaction_structure survey_satisfaction_by_year survey_satisfaction_sample survey_rcv_support survey_rcv_by_race body_text_numbers members_roster)

echo "lint"
"$PY" -m pyflakes code style || { echo "  pyflakes: fix the above"; exit 1; }
echo "  clean"

# What the data stages depend on. A full run always runs both; a filtered
# run reruns build only if one of its inputs changed since the last run that
# completed the data stages, and clean from the first step whose script
# changed (a change to a module every step imports reruns them all). The
# fingerprints live in data/built/, which is not committed, and are size and
# modification time, not content: a touched file only costs a rebuild.
BUILT_BY=(data/raw data/transcribed code/build code/citekeys.py)
CLEANED_BY=(code/clean code/citekeys.py)
STAMP=data/built/.inputs      # line 1: when the build stage started; then one line per input
fingerprint() {
  find "$@" -type f -not -path '*/__pycache__/*' -print0 | sort -z | xargs -0 stat -f '%N %z %m' | sort -u
}
changed() {                   # inputs under "$@" whose line is not in the stamp, or that left it
  comm -3 <(tail -n +2 "$STAMP" | grep -E "^($(IFS='|'; echo "$*"))" || true) <(fingerprint "$@") \
    | sed 's/^\t//' | cut -d' ' -f1 | sort -u
}
mkdir -p data/built

build=yes; from=0
if [ $# -gt 0 ] && [ -f "$STAMP" ]; then
  if [ -z "$(changed "${BUILT_BY[@]}")" ]; then
    build=no; from=${#CLEAN[@]}
    for f in $(changed "${CLEANED_BY[@]}"); do
      i=0; step=${#CLEAN[@]}
      for s in "${CLEAN[@]}"; do [ "$f" = "code/clean/$s.py" ] && step=$i; i=$((i + 1)); done
      [ "$step" -lt "${#CLEAN[@]}" ] || step=0        # not a step: a module the steps import
      [ "$step" -lt "$from" ] && from=$step
    done
  fi
fi

# Both data stages read `import citekeys` from here; nothing else is on the path.
export PYTHONPATH="$PWD/code"

# code/clean/paths.py refuses a built or clean table older than this. When
# the build stage is skipped, its tables are from the run the stamp records.
if [ "$build" = yes ]; then
  export RUN_STARTED=$(date +%s)
  # data/built/ is not committed, so it is made before anything reads it, and
  # emptied first: a table left by a step that no longer exists would fail the
  # inventory test in any checkout that had built before.
  echo "build"
  rm -f data/built/*.csv
  for s in "${BUILD[@]}"; do
    (cd code/build && ../../"$PY" "$s.py")
  done
else
  export RUN_STARTED=$(head -1 "$STAMP")
  echo "build: skipped, its inputs have not changed"
fi

# The tests prove the guards still fire, under a minute. A filtered run
# is for editing one thing; the full run that gates a commit runs them.
if [ $# -eq 0 ]; then
  echo "tests"
  "$PY" code/tests.py | sed 's/^/  /'
else
  echo "tests: skipped on a filtered run"
fi

if [ "$from" -lt "${#CLEAN[@]}" ]; then
  [ "$from" -eq 0 ] && echo "clean" || echo "clean: from ${CLEAN[$from]}, earlier steps unchanged"
  for s in "${CLEAN[@]:$from}"; do
    (cd code/clean && ../../"$PY" "$s.py")
  done
else
  echo "clean: skipped, no script changed"
fi
{ echo "$RUN_STARTED"; fingerprint "${BUILT_BY[@]}" "${CLEANED_BY[@]}"; } > "$STAMP"

# A figure script reads `import style` and `import charts` from here.
export PYTHONPATH="$PWD/style"

echo "analysis"
selected=("${FIGURES[@]}")
if [ $# -gt 0 ]; then
  selected=()
  for pat in "$@"; do
    for f in "${FIGURES[@]}"; do [[ "$f" == *"$pat"* ]] && selected+=("$f"); done
  done
  [ ${#selected[@]} -gt 0 ] || { echo "  no figure matches: $*"; exit 1; }
fi
for s in "${selected[@]}"; do
  printf '  %-34s' "$s"
  outputs=("figures/pdf/$s.pdf" "figures/png/$s.png")
  case "$s" in
    body_text_numbers) outputs=("paper/$s.tex");;
    members_roster) outputs=("paper/$s.tex" "paper/${s}_subsets.tex");;
  esac
  # Removed first, so a script that writes nothing cannot pass on a previous
  # run's copy.
  rm -f "${outputs[@]}"
  (cd code/analysis && ../../"$PY" "$s.py") >/dev/null
  for out in "${outputs[@]}"; do
    [ -f "$out" ] || {
      echo "FAILED"
      echo "    $s.py did not write $out"
      echo "    A figure script ends in paths.save(fig, profile), which names the"
      echo "    file after the script - check that the call is there."
      exit 1; }
  done
  echo "ok"
done
echo "-> figures/pdf, figures/png ($(ls figures/pdf | wc -l | tr -d ' ') each)"

# Which figures this run changed. A report, never a failure.
if changed=$(git diff --name-only -- figures/ 2>/dev/null) && [ -n "$changed" ]; then
  echo
  echo "figures changed by this run:"
  printf '%s\n' "$changed" | sed 's/^/  /'
  echo "  (commit them, or git checkout -- figures/ to discard)"
fi

# On a full run, figures/ should hold exactly what the steps produce.
if [ $# -eq 0 ]; then
  for kind in pdf png; do
    for f in figures/$kind/*.$kind; do
      stem=$(basename "$f" ".$kind")
      printf '%s\n' "${FIGURES[@]}" | grep -qx "$stem" || {
        echo "WARNING: figures/$kind/$stem.$kind is not produced by any step - stale? delete it."; }
    done
  done
fi

# Scans marked in_git = no in the inventory are fetched on demand and never
# read by the build.
missing=$("$PY" -c '
import csv, pathlib
print(sum(1 for r in csv.DictReader(open("data/contents.csv"))
          if r["in_git"] == "no" and not pathlib.Path(r["path"]).exists()))')
if [ "$missing" -gt 0 ]; then
  echo
  echo "$missing census scans and OCR files are not on disk; the build never reads them."
  echo "  to fetch the scans: .venv/bin/python code/fetch/census_volumes.py; the OCR (a Mac): .venv/bin/python code/transcribe/census.py"
fi

# Overleaf's limits on the files it syncs: 100MB in all, 7MB of editable
# (text) files (CLAUDE.md). These checks never fail the build.
kb=0; text_kb=0
while IFS= read -r -d '' f; do
  [ -f "$f" ] || continue
  size=$(( $(stat -f%z "$f") / 1024 ))
  kb=$(( kb + size ))
  case "$f" in *.pdf|*.png|*.ttf|*.gz) ;; *) text_kb=$(( text_kb + size ));; esac
done < <(git ls-files -z 2>/dev/null) || true
if [ "$kb" -ge 81920 ]; then
  echo
  echo "WARNING: tracked files total $((kb/1024))MB, approaching Overleaf's 100MB ceiling."
  echo "         Time to revisit the one-repo decision - see CLAUDE.md."
fi
if [ "$text_kb" -ge 6144 ]; then
  echo
  echo "WARNING: editable files total $((text_kb/1024))MB; Overleaf stops syncing at 7MB."
  echo "         The large text files are data/raw CSVs and the OCR - see CLAUDE.md."
fi
