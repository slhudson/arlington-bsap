"""Census scans -> data/extracted/by_ocr/*.txt, one text file per volume.

Seven of the nine scanned volumes have no text layer, so nothing in them can
be searched or cited without this. Running it makes all 521 pages greppable,
which is what documenting the early census figures depends on - see
docs/sources.md.

Uses macOS's built-in Vision OCR, so there is nothing to install beyond the
Python bindings. Language correction is off: these are tables of numbers, and
correction turns digits into words.

NOT part of `bash run.sh`. It takes minutes, not seconds, and its output only
changes if raw/ changes - which it never does. Run it by hand if the output is
ever lost:

    .venv/bin/python build/ocr_census.py

Read the output as a finding aid, not as data. OCR of 19th-century tables
misreads digits routinely - the existing text layer renders 13,659 as
"lB, 659". Use it to locate a table and page, then read the number off the
scan itself.
"""
import sys
import time

import pymupdf
import Quartz
import Vision
from Foundation import NSData

from files import EXTRACTED, RAW

SCANS = RAW / "census"
OUT = EXTRACTED / "by_ocr"
DPI = 300


def ocr_image(png_bytes):
    data = NSData.dataWithBytes_length_(png_bytes, len(png_bytes))
    src = Quartz.CGImageSourceCreateWithData(data, None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(0)            # accurate, not fast
    req.setUsesLanguageCorrection_(False)  # tables of numbers
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    handler.performRequests_error_([req], None)
    return [o.topCandidates_(1)[0].string() for o in (req.results() or [])]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(SCANS.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"no scans in {SCANS}")

    for pdf in pdfs:
        started = time.time()
        doc = pymupdf.open(pdf)
        out = OUT / f"{pdf.stem}.txt"
        with out.open("w") as fh:
            fh.write(f"# OCR of {pdf.name} ({len(doc)} pages)\n")
            fh.write("# Finding aid only - verify every digit against the scan.\n")
            for i, page in enumerate(doc):
                fh.write(f"\n===== {pdf.name} page {i + 1} =====\n")
                png = page.get_pixmap(dpi=DPI).tobytes("png")
                fh.write("\n".join(ocr_image(png)) + "\n")
                print(f"  {pdf.name} p{i+1}/{len(doc)}", end="\r", file=sys.stderr)
        print(f"  {out.name:<24} {len(doc):>3} pages  {time.time()-started:5.0f}s")


if __name__ == "__main__":
    main()
