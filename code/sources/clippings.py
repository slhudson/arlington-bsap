"""Cut each filed web print down to where its text stops.

    .venv/bin/python code/sources/clippings.py            # dry run: report, cut nothing
    .venv/bin/python code/sources/clippings.py --apply    # cut the pages, rewrite the annotations

A press copy printed from a web page carries the page's furniture after the
article: event promotions, a newsletter box, the comment thread, a trending
list, the site's footer. Those pages are not the source. This cuts every
filed press copy back to the last page the article's own text reaches, and
writes ", cut to the article" into the entry's annotation so the copy and the
bib say the same thing.

What counts as furniture is two rules on a page's text, CHROME and FOOTER
below: a page is furniture if the site's footer is on it, or if removing the
known blocks leaves fewer than WORDS words. Article text and furniture share
the last page often enough that the page is kept whenever any article text is
on it; the cut is only ever trailing, so nothing between the first page and
the last page of article text is touched.

A dry run prints what --apply would cut and, for every page it would drop, the
text left after the known blocks are removed, so the rule can be read against
the pages rather than trusted. --apply refuses a copy whose annotation quotes
words that only the dropped pages carry, and leaves scanned pages alone: a
one-page copy is a scan of a printed page, not a print of a web page.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive

# Furniture that sits around an article, by the site that serves it. Each is
# removed from a page's text before what is left is counted.
# Furniture that sits around an article, by the site that serves it. Each is
# removed from a page's text before what is left is counted.
CHROME = [
    # Local News Now (ARLnow, the Gazette Leader). An event promotion carries an
    # arbitrary title and runs to the link under it; the title is whatever text
    # precedes the event's hours, which an article's sentence would end before.
    r"Featured Event.*?Read More",
    r"Featured Event",                        # the heading alone, its promotion overleaf
    r"[^.]*?\d{1,2}:\d{2} ?[ap]m-\d{1,2}:\d{2} ?[ap]m\s*Read More",
    r"Get our email newsletter.*?Sign up",
    r"Show Comments",
    r"About the Author.*",                    # the heading, then the writer's biography
    r"Announcements.*",                       # a run of other headlines, to the end of the page
    r"(?:ARLnow\.com )?Launched in January 2010.*",
    r"Local is everything",
    r"Get Our App",
    r"#[\w\u2019'.\-]+(?: [A-Z][\w\u2019'.\-]+)?",      # a tag, of a word or two
    # Patch: a rail of other stories, a numbered trending list, a promotion.
    r"(?:[A-Z][\w &]*\|\s*\d+[hdm]\s).*",
    r"\d+\.\s*\W*(?:Arlington|Across Virginia)[\w ,]*News.*",
    r"\U0001f331.*",                          # "Patch AM", the day's promotion
    r"Latest News Nearby.*",
    r"Best of Arlington.*",
    r"Find out what.{0,3}s happening in.*?Patch\.?",
    r"Get more local news delivered straight to you.*",
    r"ADVERTISEMENT",
    r"Thank you to our Local Business Sponsor:.*?(?=Politics|News|$)",
    # Blue Virginia
    r"No Content Available",
    r"Paid Advertising",
    r"FOLLOW US",
    # arlingtonva.us, under a Board member's biography
    r"Registration opens beginning at.*?following Monday\.",
    r"Related County Board Meeting",
    r"(?:\d{1,2} [A-Z][a-z]{2} \d{4}\s*)+",      # the dates above the events rail
    r"\(https?://[^)]*\)",                      # a link printed beside its text
    # Connection Newspapers
    r"The Connection Sign in.*?Votes",
    r"More like this story.*",
]

# The site's own footer. It runs to the end of the document, so the page it
# starts on is the last page any article text can be on, and the pages after it
# are furniture whatever their text looks like - a footer's list of sister sites
# reads like prose to a word count.
FOOTER = [
    r"Advertise Contact Us",                  # Local News Now, and its sister sites
    r"Privacy & Other Policies",
    r"Public Notices on ARLnow",
    r"Site Navigation",
    r"Copyright Local News Now",
    r"Sections\s+News / Sports / Opinion",    # Connection Newspapers
    r"The purpose of Blue Virginia",
    r"Corporate Info About Patch",
    r"Find out what.{0,3}s happening in your community on the Patch app",
    r"Open Door Monday",                      # arlingtonva.us, the events rail under a biography
]

# What a page must hold, furniture removed, to count as the article's. Low,
# because the last page of an article can be a line and a handle: raising it
# drops real text, and the pages it would catch instead are caught by FOOTER.
WORDS = 8

# What the end of a sentence looks like, for the page a sentence runs over onto.
TERMINAL = re.compile(r"[.!?\u201d\"]\s*$")

CHROME_RE = re.compile("|".join(CHROME + [f + ".*" for f in FOOTER]), re.S | re.I)
FOOTER_RE = re.compile("|".join(FOOTER), re.S)   # case as the footer sets it

QUOTED = re.compile(r"[“\"]([^“”\"]{25,})[”\"]")


def text(page):
    return " ".join(page.get_text().split())


def remainder(t):
    """A page's text with every known block of furniture removed."""
    return " ".join(CHROME_RE.sub(" ", t).split())


def is_article(t):
    """Whether a page carries the article's own text."""
    return len(remainder(t).split()) >= WORDS


def article_pages(texts):
    """How many pages the article runs to: the last page with article text on
    it, and never past the page the site's footer starts on. Pages before that
    are kept whatever is on them, so a blank page or an advertisement inside
    the article does not end it."""
    footer = next((i for i, t in enumerate(texts) if FOOTER_RE.search(t)), len(texts) - 1)
    last = 0
    for i, t in enumerate(texts[:footer + 1]):
        if is_article(t):
            last = i + 1
    # A sentence that runs off the bottom of a page carries on overleaf, so a
    # page too short to count on its own is the article's if the page before it
    # stops mid-sentence and anything but furniture is on it. A letter whose
    # signature lands on a page of its own is the case this exists for.
    if (last and last < len(texts) and not FOOTER_RE.search(texts[last])
            and not TERMINAL.search(remainder(texts[last - 1])) and remainder(texts[last])):
        last += 1
    return last


def normalise(s):
    """Text with its whitespace and quotation marks flattened, for comparing a
    quotation against a page."""
    s = " ".join(s.split())
    for a, b in (("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"),
                 ("—", "-"), ("–", "-")):
        s = s.replace(a, b)
    return s


def quotations(e):
    """The phrases an entry's annotation and note quote, long enough to be the
    source's words rather than a title or a filename."""
    out = []
    for field in ("annotation", "note"):
        for q in QUOTED.findall(archive.plain(e.get(field, ""))):
            if not re.search(r"\.(pdf|jpe?g|png|xlsx?|csv|txt)$", q.strip()):
                out.append(normalise(q))
    return out


def copies(bib, documents):
    """Every filed press copy that is a print of a web page, with its entry."""
    out = []
    for e in bib:
        # Press, and the other kinds printed from a web page: a biography and a
        # campaign page carry the site's furniture after them in the same way.
        if archive.kind(e) not in ("press", "obituaries", "bios", "campaign websites"):
            continue
        for name in archive.filed(e):
            p = documents / name
            if p.suffix.lower() == ".pdf" and p.exists():
                out.append((e, p, name))
    return out


CUT = ", cut to the article"


def main():
    import pymupdf          # only reading the copies needs it, not the rules above

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("--apply", action="store_true", help="cut the pages and rewrite the bib")
    ap.add_argument("--documents", type=Path, default=archive.DOCUMENTS,
                    help="the Drive documents folder")
    a = ap.parse_args()
    if not a.documents.is_dir():
        sys.exit(f"documents folder not found: {a.documents}")

    bib_text = archive.BIB.read_text()
    bib = archive.entries(bib_text)
    cuts, blocked, unchanged = [], [], 0

    for e, path, name in copies(bib, a.documents):
        doc = pymupdf.open(path)
        texts = [text(p) for p in doc]
        if len(texts) == 1:                   # a scan of a printed page
            unchanged += 1
            continue
        keep = article_pages(texts)
        if not keep:
            blocked.append((e["key"], name, "no page reads as the article"))
            continue
        if keep == len(texts):
            unchanged += 1
            continue
        kept = normalise(" ".join(texts[:keep]))
        lost = [q for q in quotations(e) if q not in kept]
        if lost:
            blocked.append((e["key"], name,
                            "quoted words are only on the dropped pages: "
                            + "; ".join(f'"{q[:60]}"' for q in lost)))
            continue
        cuts.append((e["key"], path, name, keep, len(texts),
                     [remainder(t) for t in texts[keep:]]))
        doc.close()

    print(f"{len(cuts) + len(blocked) + unchanged} filed press copies: "
          f"{len(cuts)} to cut, {unchanged} already end with the article, "
          f"{len(blocked)} refused")
    for key, name, why in blocked:
        print(f"  refused {key}: {why}")
    print()
    for key, path, name, keep, total, dropped in cuts:
        print(f"{key}: {total} pages -> {keep}   {Path(name).name}")
        for i, r in enumerate(dropped):
            print(f"    drop p{keep + i + 1}: {r[:160] or '(nothing but furniture)'}")

    if not a.apply:
        print("\ndry run: nothing cut. --apply cuts the pages and rewrites the bib.")
        return 1 if blocked else 0

    for key, path, name, keep, total, _ in cuts:
        doc = pymupdf.open(path)
        doc.delete_pages(keep, total - 1)
        tmp = path.with_suffix(".pdf.part")
        doc.save(tmp, garbage=3, deflate=True)
        doc.close()
        if len(pymupdf.open(tmp)) != keep:
            sys.exit(f"{key}: the cut copy does not have {keep} pages")
        tmp.replace(path)
        print(f"cut {name} to {keep} pages")
    new, missed = archive.append_annotation(bib_text, [c[0] for c in cuts], CUT)
    archive.BIB.write_text(new)
    print(f"rewrote {len(cuts) - len(missed)} annotations in {archive.BIB.name}")
    for key in missed:
        print(f"  {key}: add \"cut to the article\" to the annotation by hand")
    return 0


if __name__ == "__main__":
    sys.exit(main())
