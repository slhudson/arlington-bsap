"""Git merge driver for docs/questions.csv: a three-way merge by row id.

    python3 code/merge_questions.py <base> <ours> <theirs>

Git calls this (.gitattributes names the driver, run.sh and code/merge.sh
register it) with the common ancestor, the current side and the side being
merged. The result goes to <ours>; a nonzero exit means conflicts.

The tracker's unit is the row, and a line-based merge cannot see that. The
union merge this replaces kept both sides of every hunk that differed, so a
row closed on main came back whenever the branch touched a line near it.
Here each row is judged on its own, by its id, against the ancestor:

    one side left it alone     -> the other side's version, including a deletion
    both sides made the same change   -> that change
    both sides changed it differently -> a conflict, both versions written
                                         between markers for a person to choose

An edit on one side against a deletion on the other is such a conflict: the
row was closed on one side and still being worked on the other.

The result is main's rows in main's order, then the rows the branch added in
its order. Rows are compared and written as the bytes in the file, so a row
neither side touched is not reformatted.
"""
import csv
import io
import sys


def rows(text):
    """The file as (header, {id: raw record}, [ids in order]). A record is the
    exact text of one row, quoted newlines and all, so it is compared and
    written back byte for byte."""
    lines = text.splitlines(keepends=True)
    records, current = [], ""
    for line in lines:
        current += line
        if current.count('"') % 2 == 0:       # every quote closed: the record is whole
            records.append(current)
            current = ""
    assert not current, "unterminated quote in the tracker"
    if records and not records[-1].endswith("\n"):
        records[-1] += "\n"
    header, body = records[0], records[1:]
    by_id, order = {}, []
    for rec in body:
        rid = next(csv.reader(io.StringIO(rec)))[0]
        assert rid not in by_id, f"two rows with the id {rid}"
        by_id[rid] = rec
        order.append(rid)
    return header, by_id, order


def merge(base, ours, theirs):
    """The merged text, and the ids left in conflict."""
    _, b, _ = rows(base)
    oh, o, oo = rows(ours)
    th, t, to = rows(theirs)
    assert oh == th, "the two sides have different columns; a person has to merge that"
    out, conflicts = [oh], []
    for rid in oo + [i for i in to if i not in o]:
        base_row, mine, theirs_row = b.get(rid), o.get(rid), t.get(rid)
        if mine == theirs_row:
            pick = mine
        elif mine == base_row:
            pick = theirs_row
        elif theirs_row == base_row:
            pick = mine
        else:
            conflicts.append(rid)
            out.append("<<<<<<< ours\n" + (mine or "") + "=======\n" + (theirs_row or "")
                       + ">>>>>>> theirs\n")
            continue
        if pick is not None:
            out.append(pick)
    return "".join(out), conflicts


def main(base_path, ours_path, theirs_path):
    read = lambda p: open(p, newline="").read()
    text, conflicts = merge(read(base_path), read(ours_path), read(theirs_path))
    with open(ours_path, "w", newline="") as f:
        f.write(text)
    if conflicts:
        print("docs/questions.csv: rows changed on both sides: " + ", ".join(conflicts),
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
