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

PY=.venv/bin/python
[ -x "$PY" ] || { echo "no venv: python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl pyflakes"; exit 1; }

# Stage 1: data/raw/ and data/transcribed/ -> data/built/. Reshaping only;
# each step is refused if a value its inputs carry is missing from its output.
BUILD=(elections members_claims candidates census registration localities voters_party)

# Stage 2: data/built/ -> data/clean/. Every decision about what a number
# is. Each step is named for the file it writes, and later steps read what
# earlier ones wrote.
CLEAN=(residents residents_by_district members candidates members_residence members_by_year voters voters_turnout localities)

# Stage 3: data/clean/ -> figures/. Each step is named for the figure it
# writes. Five populations, alphabetical within each; last, the one step that
# writes the numbers the prose cites, paper/body_text_numbers.tex, instead.
FIGURES=(residents_by_age residents_by_race residents_per_seat voters_turnout voters_board voters_president members_age members_age_coverage candidates members_gender members_party localities_density localities_residents members_race members_residence_coverage body_text_numbers)

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
  # data/built/ is not committed, so it is made before anything reads it.
  echo "build"
  for s in "${BUILD[@]}"; do
    (cd code/build && ../../"$PY" "$s.py")
  done
else
  export RUN_STARTED=$(head -1 "$STAMP")
  echo "build: skipped, its inputs have not changed"
fi

# The tests prove the guards still fire, about ten seconds. A filtered run
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
  [ "$s" = body_text_numbers ] && outputs=("paper/$s.tex")
  # Removed first, so a script saving under the wrong name cannot pass on a
  # previous run's copy.
  rm -f "${outputs[@]}"
  (cd code/analysis && ../../"$PY" "$s.py") >/dev/null
  for out in "${outputs[@]}"; do
    [ -f "$out" ] || {
      echo "FAILED"
      echo "    $s.py did not write $out"
      echo "    A script must save under its own name - check its files.save() call."
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
for r in csv.DictReader(open("data/contents.csv")):
    if r["in_git"] == "no" and not pathlib.Path(r["path"]).exists():
        print(r["path"])')
if [ -n "$missing" ]; then
  echo
  echo "not on disk, and not needed to build:"
  printf '%s\n' "$missing" | sed 's/^/  /'
  echo "  scans: .venv/bin/python code/fetch/census_volumes.py"
  echo "  OCR text under data/transcribed/by_ocr/ (a Mac): .venv/bin/python code/transcribe/census.py"
fi

# Overleaf's limits on the files it syncs: 100MB in all, 7MB of editable
# (text) files (CLAUDE.md). These checks never fail the build.
kb=0; text_kb=0
while IFS= read -r -d '' f; do
  [ -f "$f" ] || continue
  size=$(( $(stat -f%z "$f") / 1024 ))
  kb=$(( kb + size ))
  case "$f" in *.pdf|*.png|*.ttf) ;; *) text_kb=$(( text_kb + size ));; esac
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
