"""Every quotation in a legal source's annotation is in the copy we hold.

    .venv/bin/python code/sources/quotations.py

Rose 1976 p. 176 put "continuous, contiguous, and homogeneous community" in
the Supreme Court of Appeals' mouth. The phrase reached a proposal, the
paper and a slide the County was sent, and nothing here would have caught
it: the opinion had been filed in Drive all along and no one compared the
two. This does.

Only the entries archive.kind() files under legal/ are checked. Those copies
are reporter scans and statute volumes that carry a text layer, so a
quotation either appears in one or does not. Elsewhere in the bib the filed
copies are census sheets and newspaper pages whose OCR is too poor to hold a
quotation to.

Not every quotation in an annotation is the copy's own words. Some are
recorded negatives, words the reader searched for and did not find, which the
write-ups keep; some are another entry's; and some sit on a page whose scan
the OCR did not reach, read by eye instead. Prose cannot be read for the
difference, so each is declared in DECLARED with its reason. Anything else
missing stops the build.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive

# A quotation shorter than this is a term of art, not a passage, and matching
# it proves nothing.
SHORTEST = 4

# The quotations a filed copy is not expected to yield, and why. The key is
# the citekey and each quotation is given as the annotation writes it. A
# quotation belongs here only with a reason a reader can check; the point of
# the file is lost if it becomes a place to put whatever failed.
DECLARED = {
    "bennettvgarrett1922": {
        "a continuous, contiguous, and homogeneous community":
            "the misattribution this check exists to catch; rose1976 p. 176 "
            "put it in the court's mouth and the opinion does not contain it",
    },
    "winchestervredmond1896": {
        "directly quoted what we know as Dillon's Rule":
            "schragger2022's words about this case, not the case's own",
    },
    "vacode1873": {
        "resident of the township": "a recorded negative: searched for and not found",
        "reside in the township": "a recorded negative: found only of the assessor",
    },
    "vacode1887": {
        "resident of the district": "a recorded negative: searched for and not found",
        "of the road district": "a recorded negative: searched for and not found",
        "reside in the district": "a recorded negative: found only of a medical examiner",
    },
    "vaconstitution1869": {
        "the county, city or town in which he shall offer to vote":
            "on printed p. 9 of the excerpt, whose scan carries no OCR; only "
            "pp. 28-29 came through, and Art. III sec. 1 was read by eye",
        "passed April 17, 1868":
            "on the title page of the excerpt, which carries no OCR either",
    },
}

# A copy whose annotation says so carries no text to search.
NO_TEXT = re.compile(r"carries no text layer|scan carries no text")


def quotations(annotation, filenames=()):
    """The passages an annotation quotes, as it writes them."""
    a = " ".join(annotation.split())
    # A filed name is written the way archive.py reads it, so the comparison is
    # against that reading: an annotation that types a space after a folder
    # still names a copy and is not quoting the document.
    return [q for q in re.findall(r'"([^"]{8,})"', a)
            if len(q.split()) >= SHORTEST and archive.tidy_name(q) not in filenames]


def comparable(s):
    """A string reduced to what OCR cannot get wrong - letters and digits -
    so that a quotation and a scan can be compared at all. Not the same job
    as archive.plain(), which renders a bib value for a reader."""
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"[-‐-―]\s*", "", s)          # line-break hyphenation
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def contains(text, quote):
    """Is the quote in the text, allowing for what a scan does to a line?

    An ellipsis or a bracket marks the reader's own omission, so the
    fragments either side must appear in order. Within a fragment the scan
    may interpolate a marginal note or drop a letter, so a bounded number of
    stray characters is allowed - few enough that the rest still has to match
    in order, which a wrong quotation cannot do.
    """
    at = 0
    for part in re.split(r"\.\s*\.\s*\.|…|\[[^\]]*\]", quote):
        part = comparable(part)
        if not part:
            continue
        at = _find(text, part, at)
        if at < 0:
            return False
    return True


def _find(text, part, start):
    """Where part ends in text at or after start, or -1. See contains()."""
    budget = max(6, len(part) // 5)
    anchor = part[:min(4, len(part))]
    i = text.find(anchor, start)
    while i >= 0:
        j, k, left = i + len(anchor), len(anchor), budget
        while k < len(part) and j < len(text):
            if text[j] == part[k]:
                k += 1
            elif left:
                left -= 1
            else:
                break
            j += 1
        if k == len(part):
            return j
        i = text.find(anchor, i + 1)
    return -1


def text_of(path):
    """A filed copy's text, in reading order. Reporter scans are laid out in
    columns and come back shuffled without the sort."""
    import pymupdf
    return comparable(" ".join(p.get_text(sort=True) for p in pymupdf.open(path)))


def unsupported(bib, documents=None):
    """Every (citekey, quotation) a legal entry attributes to a copy that does
    not contain it and does not declare in DECLARED, and how many quotations
    were read. A check that silently reads nothing is worse than none, so the
    count is returned and main() refuses a run that checked too few."""
    documents = documents or archive.DOCUMENTS
    out, read = [], 0
    for e in archive.entries(bib):
        annotation = e.get("annotation", "")
        if archive.kind(e) != "legal" or NO_TEXT.search(annotation):
            continue
        names = archive.filed(e)
        qs = [q for q in quotations(annotation, names)
              if q not in DECLARED.get(e["key"], {})]
        # The names an annotation gives already carry their kind folder, and
        # an entry may file more than one copy: a quotation in any of them is
        # supported.
        paths = [documents / n for n in names if (documents / n).exists()]
        if not paths or not qs:
            continue                    # archive.py is the check for a missing copy
        texts = [text_of(p) for p in paths]
        read += len(qs)
        out += [(e["key"], q) for q in qs
                if not any(contains(text, q) for text in texts)]
    return out, read


# The first run read this many. A later run that reads far fewer has lost its
# files or its parsing, not its quotations.
FEWEST = 30


def main():
    missing, read = unsupported(archive.BIB.read_text())
    for key, q in missing:
        print(f'{key}: the filed copy does not contain "{q}"')
    if missing:
        sys.exit(f"\n{len(missing)} quotations are not in the document they are "
                 f"attributed to. Correct the annotation, or declare the quotation "
                 f"in DECLARED in {Path(__file__).name} with the reason.")
    if read < FEWEST:
        sys.exit(f"only {read} quotations were read, fewer than the {FEWEST} this "
                 f"check is known to cover: the filed copies or the annotations "
                 f"are not being found.")
    print(f"quotations: {read} in legal sources, all in the copy we hold")


if __name__ == "__main__":
    main()
