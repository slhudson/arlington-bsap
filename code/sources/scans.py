"""Make a filed copy's images weigh what a reader needs, and no more.

    .venv/bin/python code/sources/scans.py            # dry run: report, change nothing
    .venv/bin/python code/sources/scans.py --apply

A copy printed or scanned from elsewhere arrives at whatever weight its source
chose: a photograph stored as PNG, or a manuscript scanned at an archival
resolution no one reads it at. The 1902 Constitution was 97MB of 155 pages, a
sixth of the whole archive, and a campaign page was 16MB of four photographs.

This re-encodes those images and nothing else. Every page is kept, in its
order, at its size on the page - pages are never cut, which is `clippings.py`'s
job and is decided by what the page says, not by what it weighs. A photograph
stored losslessly becomes a JPEG, and an image carrying more detail than DPI
can show on its page is sampled down to it. Text drawn as text is untouched, so
a copy whose pages are text does not change at all.

A dry run prints what each copy would weigh. --apply rewrites it in place and
refuses to keep a result that has fewer pages than it started with, or that is
not smaller. The filed copy is not the document of record: every entry carries
the url it came from, and the annotation of a copy this has reduced says so.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive

DPI = 150          # what a reader opens a page at; archival scans carry much more
QUALITY = 72       # JPEG quality, read against the 1902 manuscript's hand
FLOOR = 2_000_000  # a copy smaller than this is not worth rewriting
HALF = 0.5         # and a rewrite that does not halve it is not worth taking

REDUCED = ", images reduced to 150 dpi"


def already(e):
    """Whether this copy has been through here. The annotation is the record,
    so a second run cannot recompress what a first run already compressed."""
    return REDUCED.strip(", ") in plain_annotation(e)


def plain_annotation(e):
    return " ".join(archive.plain(e.get("annotation", "")).split())


def main():
    import pymupdf

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("--apply", action="store_true", help="rewrite the copies in place")
    ap.add_argument("--documents", type=Path, default=archive.DOCUMENTS)
    ap.add_argument("--floor", type=int, default=FLOOR,
                    help=f"ignore a copy smaller than this many bytes (default {FLOOR})")
    a = ap.parse_args()
    if not a.documents.is_dir():
        sys.exit(f"documents folder not found: {a.documents}")

    bib = archive.entries(archive.BIB.read_text())
    heavy = [(e, a.documents / n) for e in bib for n in archive.filed(e)
             if (a.documents / n).suffix.lower() == ".pdf" and (a.documents / n).exists()
             and (a.documents / n).stat().st_size >= a.floor and not already(e)]
    print(f"{len(heavy)} filed copies over {a.floor / 1e6:.0f}MB that have not been reduced")

    done, refused, saved = [], [], 0
    for e, path in sorted(heavy, key=lambda r: -r[1].stat().st_size):
        before, pages = path.stat().st_size, len(pymupdf.open(path))
        tmp = path.with_suffix(".pdf.part")
        doc = pymupdf.open(path)
        try:
            doc.rewrite_images(dpi_target=DPI, quality=QUALITY)
            doc.save(tmp, garbage=4, deflate=True)
        except Exception as err:
            # A copy some site built badly enough that mupdf will not rewrite
            # it. It is left exactly as it is and named, rather than stopping
            # the run on behalf of every other copy.
            refused.append((e["key"], path.name, f"{type(err).__name__}: {err}"))
            tmp.unlink(missing_ok=True)
            continue
        finally:
            doc.close()
        after = tmp.stat().st_size
        if len(pymupdf.open(tmp)) != pages:
            tmp.unlink()
            sys.exit(f"{path.name}: the rewrite lost a page")
        # Only a copy that was stored wastefully. If re-encoding halves it, the
        # source chose a format that suits nothing - a photograph kept
        # losslessly, a page scanned far above reading resolution. If it saves
        # a quarter, the copy was stored reasonably and the only thing a
        # rewrite buys is lost fidelity, which a table of small digits cannot
        # spare.
        if after >= before * HALF:
            tmp.unlink()
            continue
        saved += before - after
        done.append(e["key"])
        print(f"  {before / 1e6:6.1f} -> {after / 1e6:6.1f} MB  {e['key']}: {path.name[:56]}")
        tmp.replace(path) if a.apply else tmp.unlink()

    for key, name, why in refused:
        print(f"  refused {key}: {name[:50]} - {why[:70]}")
    print(f"{'saved' if a.apply else 'would save'} {saved / 1e6:.0f}MB")
    if not a.apply:
        print("dry run: nothing rewritten. --apply rewrites them in place.")
        return
    new, missed = archive.append_annotation(archive.BIB.read_text(), done, REDUCED)
    archive.BIB.write_text(new)
    print(f"recorded the reduction in {len(done) - len(missed)} annotations")
    for key in missed:
        print(f"  {key}: say in the annotation that the copy's images are reduced")


if __name__ == "__main__":
    main()
