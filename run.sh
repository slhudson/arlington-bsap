#!/usr/bin/env bash
# Rebuild everything from data/. The only entry point (CLAUDE.md).
#
#   bash run.sh                  build, then every figure
#   bash run.sh residents_per    build, then only figures whose names match
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
BUILD=(elections board_claims board_candidacies census registration board_peers voters_party)

# Stage 2: data/built/ -> data/clean/. Every decision about what a number
# is. Each step is named for the file it writes, and later steps read what
# earlier ones wrote.
CLEAN=(residents board_members board_candidacies board_residence board_seats voters turnout board_peers)

# Stage 3: data/clean/ -> figures/. Each step is named for the figure it
# writes. Three subjects, alphabetical within each.
FIGURES=(residents_by_age residents_by_race residents_per_seat turnout voters_board voters_president board_age board_age_coverage board_candidacies board_gender board_party board_peers_density board_peers_residents board_race board_residence_coverage)

echo "lint"
"$PY" -m pyflakes code style || { echo "  pyflakes: fix the above"; exit 1; }
echo "  clean"

# code/clean/paths.py refuses a built or clean table older than this.
export RUN_STARTED=$(date +%s)

# Both data stages read `import citekeys` from here; nothing else is on the path.
export PYTHONPATH="$PWD/code"

# data/built/ is not committed, so it is made before anything reads it.
echo "build"
for s in "${BUILD[@]}"; do
  (cd code/build && ../../"$PY" "$s.py")
done

# The tests prove the guards still fire. About five seconds.
echo "tests"
"$PY" code/tests.py | sed 's/^/  /'

echo "clean"
for s in "${CLEAN[@]}"; do
  (cd code/clean && ../../"$PY" "$s.py")
done

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
  # Removed first, so a script saving under the wrong name cannot pass on a
  # previous run's copy.
  rm -f "figures/pdf/$s.pdf" "figures/png/$s.png"
  (cd code/analysis && ../../"$PY" "$s.py") >/dev/null
  for kind in pdf png; do
    [ -f "figures/$kind/$s.$kind" ] || {
      echo "FAILED"
      echo "    $s.py did not write figures/$kind/$s.$kind"
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
