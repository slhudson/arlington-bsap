"""Census rows in the claim files -> transcribed/by_claude/board_census.csv

Moves every row that cites a census record (a citekey census<year><name>)
out of board_demographics.csv and board_residence.csv and into one row per
record in board_census.csv. The rows left behind, newspapers, obituaries
and secondary sources, are untouched, byte for byte. Re-runnable: a record
already in the table is merged with any new rows that cite it, and two
statements that differ stop the script rather than one overwriting the
other. Run by hand, output committed.

    .venv/bin/python code/transcribe/board_census.py

What each column holds is in docs/board.md, "Census records".
"""
import csv
import re
from io import StringIO

from paths import BY_CLAUDE

DEMOGRAPHICS = BY_CLAUDE / "board_demographics.csv"
RESIDENCE = BY_CLAUDE / "board_residence.csv"
OUT = BY_CLAUDE / "board_census.csv"

COLUMNS = ["name", "source", "year", "basis", "checked", "gender", "race", "age",
           "birth_year", "birthplace", "occupation", "place", "quote", "sheet"]

CENSUS = re.compile(r"census(\d{4})[a-z]+")

# The index listing's fields, "Key Value" between " · ".
FIELDS = {
    "gender": re.compile(r"Gender (.+)"),
    "race": re.compile(r"Race (.+)"),
    "age": re.compile(r"Age(?: in \d{4})? (\d+)"),
    "birthplace": re.compile(r"Birth ?[Pp]lace (.+)"),
    "occupation": re.compile(r"Occupation(?: Category)? (.+)"),
}
# A birth date the record prints, as opposed to the index's "abt" estimate.
BIRTH = re.compile(r"(?:Birth Date|Birth Year|Estimated Birth Year) (?!abt|Abt)(?:\w+ )?(\d{4})")

SHEET_AGREES = "read against the sheet, which agrees"
INDEX_ONLY = "the index only"


def lines(path):
    """The header line, and (raw line, parsed row) for each data line, line
    endings as found. No field in these files spans a line."""
    with open(path, newline="") as f:
        raw = f.read().splitlines(keepends=True)
    header = next(csv.reader([raw[0]]))
    return raw[0], [(line, dict(zip(header, next(csv.reader([line]))))) for line in raw[1:]]


def parse(quote):
    """The index listing's fields, as it prints them."""
    items = [i.strip() for i in quote.strip("“”").split(" · ")]
    out = {}
    for field, pattern in FIELDS.items():
        found = [m.group(1) for m in map(pattern.fullmatch, items) if m]
        out[field] = found[0] if found else ""
    born = BIRTH.search(quote)
    out["birth_year"] = born.group(1) if born else ""
    return out


def record(key, demo, resi):
    """One table row from the claim rows that cite one record."""
    name, source = key
    claims = [r for r in demo if r.get("race_words") or r.get("gender_words")]
    silent = [r for r in demo if not (r.get("race_words") or r.get("gender_words")
                                      or r.get("birth_year") or r.get("age"))]
    for r in claims[1:]:
        if (r["basis"], r["quote"]) != (claims[0]["basis"], claims[0]["quote"]):
            raise ValueError(f"{name} {source}: two claim rows state the match differently")
    row = {"name": name, "source": source, "year": CENSUS.match(source).group(1),
           "basis": "", "quote": "", "sheet": "", "place": ""}
    # The match and the index listing come from the trait rows; a residence
    # row alone leaves them to the record already in the table.
    if demo:
        lead = (claims or demo)[0]
        row.update(basis=lead["basis"], quote=lead["quote"], **parse(lead["quote"]))

    checked = [SHEET_AGREES] if SHEET_AGREES in row["basis"] else []
    for r in resi:
        row["place"] = r["place"]
        if r["quote"] != row["quote"]:
            row["sheet"] = r["quote"]
        if r["basis"] != "census listing":
            checked = [r["basis"].removeprefix("census listing; ")]
    checked += [r["basis"].removeprefix("census listing; ") for r in silent]
    row["checked"] = "; ".join(checked) or INDEX_ONLY
    return row


def merge(old, new):
    """A record already in the table, with what new rows say of it. A blank
    cell takes the new value; two values that differ stop the script."""
    out = dict(old)
    for c in COLUMNS:
        if c != "checked" and new.get(c) and old.get(c) and new[c] != old[c]:
            raise ValueError(f"{old['name']} {old['source']}: {c} is {old[c]!r} in the table "
                             f"and {new[c]!r} in the new rows")
        out[c] = old.get(c) or new.get(c, "")
    return out


def main():
    table = {}
    if OUT.exists():
        for r in csv.DictReader(OUT.open()):
            table[(r["name"], r["source"])] = r

    found, keep = {}, {}
    for path in (DEMOGRAPHICS, RESIDENCE):
        header, rows = lines(path)
        keep[path] = [header]
        for line, r in rows:
            if not CENSUS.fullmatch(r["source"]):
                if CENSUS.match(r["source"]):
                    raise ValueError(f"{r['name']}: {r['source']!r} is not a census citekey alone")
                keep[path].append(line)
                continue
            entry = found.setdefault((r["name"], r["source"]), {"demo": [], "resi": []})
            entry["demo" if path == DEMOGRAPHICS else "resi"].append(r)

    for key, rows in found.items():
        new = record(key, rows["demo"], rows["resi"])
        table[key] = merge(table[key], new) if key in table else new
        if not table[key]["basis"]:
            raise ValueError(f"{key[0]} {key[1]}: no row states the match; key the record "
                             f"into {OUT.name} with its basis")

    buf = StringIO()
    w = csv.DictWriter(buf, COLUMNS, quoting=csv.QUOTE_ALL, lineterminator="\n")
    w.writeheader()
    w.writerows({c: r.get(c, "") for c in COLUMNS} for r in table.values())
    OUT.write_text(buf.getvalue())
    for path, kept in keep.items():
        with open(path, "w", newline="") as f:
            f.write("".join(kept))
    print(f"{OUT.name}: {len(table)} records, {len(found)} moved in this run")


if __name__ == "__main__":
    main()
