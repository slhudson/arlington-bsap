"""Census scans -> data/transcribed/by_ocr/us_census_bureau/<year>/*.txt, one text file per volume.

Run by hand on a Mac; it takes minutes. The output is not committed: it is
1.8MB of the 7MB of text Overleaf syncs, and nothing reads it. macOS's Vision
OCR with language correction off, since these are tables of numbers.

    .venv/bin/python code/transcribe/census.py

The output is a finding aid, not data: nothing in the build reads it
(CLAUDE.md). Use it to locate a table and page, then read the number off
the scan.
"""
import sys
import time

import pymupdf
import Quartz
import Vision
from Foundation import NSData

from paths import RAW, TRANSCRIBED

SCANS = RAW / "us_census_bureau"
OUT = TRANSCRIBED / "by_ocr" / "us_census_bureau"
DPI = 300


def ocr_image(png_bytes):
    data = NSData.dataWithBytes_length_(png_bytes, len(png_bytes))
    src = Quartz.CGImageSourceCreateWithData(data, None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(0)            # accurate, not fast
    req.setUsesLanguageCorrection_(False)
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    handler.performRequests_error_([req], None)
    return [o.topCandidates_(1)[0].string() for o in (req.results() or [])]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(SCANS.rglob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"no scans in {SCANS}")

    for pdf in pdfs:
        started = time.time()
        doc = pymupdf.open(pdf)
        out = OUT / pdf.parent.relative_to(SCANS) / f"{pdf.stem}.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
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
