"""The filed copy of a page a site will not serve to a script.

    .venv/bin/python code/sources/pages.py text.txt out.pdf \\
        --title "1952 Acts of Assembly, ch. 443" \\
        --url "https://babel.hathitrust.org/cgi/pt?id=umn.31951d02280223t&seq=736" \\
        --held "HathiTrust, umn.31951d02280223t, seq 736 (printed p. 732)"

HathiTrust and Virginia Chronicle both put Cloudflare's human check in front
of every route, so neither curl nor headless Chrome can reach a page and
cite.py cannot print one; both pass in Sally's own Chrome, where the page's
own text reads cleanly (docs/web_access.md). What is filed is therefore that
text, set out here on a plain page with the address it came from and the date
it was read - the same device ancestry.py uses for a record behind a sign-in,
and for the same reason: a reader of this repository cannot fetch the page
again, so the copy has to carry the words.

The page says on its face that it is a transcript and not the site's own
image, because a reader who took it for one would be misled about what the
OCR could have got wrong. It writes the pdf and nothing else; pass that file
to cite.py as --copy, which does the filing and the bib entry.
"""
import argparse
import sys
from datetime import date
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# to_pdf is the same headless-Chrome print a filed census page is made with;
# it lives there because that was the first copy this repository had to make.
from ancestry import to_pdf, month_name

# Why the copy is a transcript. It names the text's own source rather than
# this file, so the sentence still answers the question years from now.
HEADER = ("Transcribed from {held}, read in the browser on {read}. This is not the "
          "page the site serves: it refuses an automated request, so what is filed "
          "is the text layer the page carries, taken as it stands. Where the "
          "transcript and the printed page could differ the printed page governs; "
          "the annotation in paper/sources.bib says which passages were read "
          "against the page image.")

PAGE = """<!doctype html><meta charset="utf-8"><style>
body {{ font: 11pt/1.5 Georgia, serif; margin: 2cm; }}
p.url {{ font-size: 9pt; word-break: break-all; }}
p.note {{ font-size: 9pt; color: #333; }}
h1 {{ font-size: 15pt; margin: 1.2em 0 0.6em; }}
div.text {{ white-space: pre-wrap; }}
</style>
<p class="url">{url}</p>
<p class="note">{note}</p>
<h1>{title}</h1>
<div class="text">{text}</div>
"""


def page(title, url, held, text, read=None):
    """The plain page for one transcribed page, as html."""
    note = HEADER.format(held=held, read=month_name(read or date.today().isoformat()))
    return PAGE.format(url=escape(url), note=escape(note),
                       title=escape(title), text=escape(text.strip()))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("text", type=Path, help="the page's text, as read in the browser")
    ap.add_argument("out", type=Path, help="the pdf to write")
    ap.add_argument("--title", required=True, help="what the page is, as the copy heads it")
    ap.add_argument("--url", required=True, help="the address the text was read at")
    ap.add_argument("--held", required=True,
                    help="where the text came from, precisely enough to find it "
                         'again: e.g. "HathiTrust, umn.31951d02280223t, seq 736"')
    ap.add_argument("--read", help="the date it was read, YYYY-MM-DD (default today)")
    a = ap.parse_args()

    body = a.text.read_text()
    if len(body.split()) < 40:
        sys.exit(f"{a.text}: only {len(body.split())} words, which is no page of text")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    to_pdf(page(a.title, a.url, a.held, body, a.read), a.out)
    print(f"{a.out}: {len(body.split())} words, printed")


if __name__ == "__main__":
    main()
