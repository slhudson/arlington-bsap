#!/usr/bin/env bash
# Rebuild everything from raw/. The only entry point: no figure is produced by
# hand, and nothing in data/ or figures/ is edited after the fact.
#
#   bash run.sh                  build, then every figure
#   bash run.sh residents_per    build, then only figures whose names match
#
# Invoke through bash, not ./run.sh - Overleaf does not preserve Unix file
# permissions, so a push from Overleaf strips the executable bit.
#
# Steps are listed explicitly rather than globbed, so reading this file tells
# you exactly what runs and in what order. Adding a figure means adding a line.
set -euo pipefail
cd "$(dirname "$0")"

PY=.venv/bin/python
[ -x "$PY" ] || { echo "no venv: python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl"; exit 1; }

# Stage 1: raw/ -> data/. Every decision about what a number IS happens here.
# Each step is named for the file it writes: residents.py -> data/residents.csv
BUILD=(residents board_seats board_members)

# Stage 2: data/ -> figures/. Presentation only; analysis cannot reach raw/.
# Each step is named for the figure it writes: board_seats.py -> board_seats.pdf/.png
FIGURES=(residents_by_race residents_by_race_share residents_by_race_log
         residents_per_seat board_seats)

echo "build"
for s in "${BUILD[@]}"; do
  (cd build && ../"$PY" "$s.py")
done

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
  # Remove the expected outputs FIRST. Checking only that they exist afterwards
  # is not enough: a previous run's copy would still be sitting there, so a
  # script saving under the wrong name would pass while leaving a stale figure.
  rm -f "figures/pdf/$s.pdf" "figures/png/$s.png"
  (cd analysis && ../"$PY" "$s.py") >/dev/null
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

# On a full run, figures/ should contain exactly what the steps produce and
# nothing else. Renaming a figure otherwise leaves the old one behind, and it
# keeps compiling into the paper long after its script is gone.
if [ $# -eq 0 ]; then
  for kind in pdf png; do
    for f in figures/$kind/*.$kind; do
      stem=$(basename "$f" ".$kind")
      printf '%s\n' "${FIGURES[@]}" | grep -qx "$stem" || {
        echo "WARNING: figures/$kind/$stem.$kind is not produced by any step - stale? delete it."; }
    done
  done
fi

# Overleaf syncs the WHOLE repo and recommends staying under 100MB. We chose a
# single repo on that basis, so the choice needs a tripwire rather than a note
# someone has to remember. See docs/questions.md Q6.
#
# This check must never be able to fail the build, so it tolerates tracked
# files missing from disk and falls back to 0 rather than aborting.
kb=0
while IFS= read -r -d '' f; do
  [ -f "$f" ] && kb=$(( kb + $(stat -f%z "$f") / 1024 ))
done < <(git ls-files -z 2>/dev/null) || true
if [ "$kb" -ge 81920 ]; then
  echo
  echo "WARNING: tracked files total $((kb/1024))MB, approaching Overleaf's 100MB ceiling."
  echo "         Time to revisit the one-repo decision - see docs/questions.md Q6."
fi
